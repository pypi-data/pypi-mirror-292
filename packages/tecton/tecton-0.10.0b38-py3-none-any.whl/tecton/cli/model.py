import glob
import io
import os
import sys
import tarfile
import tempfile
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed
from pathlib import Path
from typing import Any
from typing import Callable
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple

import click
import requests
from tqdm import tqdm

from tecton._internals import metadata_service
from tecton._internals import model_utils as internal_model_utils
from tecton._internals import type_utils
from tecton.cli import model_utils
from tecton.cli import printer
from tecton.cli.cli_utils import display_table
from tecton.cli.cli_utils import timestamp_to_string
from tecton.cli.command import TectonGroup
from tecton.cli.upload_utils import DEFAULT_MAX_WORKERS_THREADS
from tecton.cli.upload_utils import UploadPart
from tecton.cli.upload_utils import get_upload_parts
from tecton.framework.model_config import ModelConfig
from tecton_core import http
from tecton_core.data_types import data_type_from_proto
from tecton_core.id_helper import IdHelper
from tecton_proto.common import schema__client_pb2 as schema_pb2
from tecton_proto.common.id__client_pb2 import Id
from tecton_proto.modelartifactservice.model_artifact_service__client_pb2 import CompleteModelArtifactUploadRequest
from tecton_proto.modelartifactservice.model_artifact_service__client_pb2 import CreateModelArtifactRequest
from tecton_proto.modelartifactservice.model_artifact_service__client_pb2 import DeleteModelArtifactRequest
from tecton_proto.modelartifactservice.model_artifact_service__client_pb2 import FetchModelArtifactRequest
from tecton_proto.modelartifactservice.model_artifact_service__client_pb2 import GetModelArtifactUploadUrlRequest
from tecton_proto.modelartifactservice.model_artifact_service__client_pb2 import ListModelArtifactsRequest
from tecton_proto.modelartifactservice.model_artifact_service__client_pb2 import ModelArtifactInfo
from tecton_proto.modelartifactservice.model_artifact_service__client_pb2 import ModelType
from tecton_proto.modelartifactservice.model_artifact_service__client_pb2 import UpdateTectonModelRequest
from tecton_proto.modelartifactservice.model_artifact_service__client_pb2 import UploadModelArtifactPartRequest


# TODO(EMBED-120) - Remove hidden=True
@click.group("model", cls=TectonGroup, hidden=True)
def model():
    """Manage models"""


@model.command("create")
@click.argument("model_config_file", required=True, type=click.Path(exists=True))
def create(model_config_file):
    """Create a custom model"""
    _create(model_config_file)


@model.command("update")
@click.argument("model_config_file", required=True, type=click.Path(exists=True))
def update(model_config_file):
    """Update a custom model"""
    _update(model_config_file)


def error_and_exit(message: str):
    error_message = f"⛔ {message}"
    printer.safe_print(error_message, file=sys.stderr)
    sys.exit(1)


def try_and_exit(call: Callable[[], Any], message: str) -> Any:
    try:
        return call()
    except Exception as e:
        printer.safe_print(f"{message} : {e}", file=sys.stderr)
        sys.exit(1)


def _resolve_file(model_config_file_path: Path, file: str) -> Path:
    return Path(model_config_file_path / file)


def _create(model_config_file: str):
    """Create a custom model"""
    model_config_file_path = Path(os.path.abspath(click.format_filename(model_config_file)))
    if not os.path.isfile(model_config_file):
        internal_model_utils.error_and_exit(f"{model_config_file} is not a file")

    model_configs = model_utils.get_custom_models(model_config_file_path)
    if len(model_configs) != 1:
        internal_model_utils.error_and_exit(
            f"Exactly one `ModelConfig` should be defined in the python file, provided file has {len(model_configs)}."
        )
    model_config = model_configs[0]
    _create_from_model_config(model_config, model_config_file_path)


def _get_files(model_config_file_dir, artifact_files: List[str]):
    return [Path(model_config_file_dir / file) for file_str in artifact_files for file in glob.glob(file_str)]


def _create_from_model_config(model_config: ModelConfig, model_config_file_path: Path):
    model_config_file_dir = model_config_file_path.parent
    archive_root_abs_path = Path(model_config_file_dir).resolve()

    model_file_path = Path(model_config_file_dir / model_config.model_file)
    artifact_files = model_config.artifact_files or []
    all_file_paths = [
        *_get_files(model_config_file_dir, artifact_files),
        model_config_file_path,
        model_file_path,
    ]
    internal_model_utils.validate(
        model_file_path=model_file_path, archive_root_path=archive_root_abs_path, files=all_file_paths
    )

    model_artifact_id = create_model_artifact(
        name=model_config.name,
        model_file_path=str(Path(model_file_path.relative_to(archive_root_abs_path))),
        type=internal_model_utils.model_type_string_to_enum(model_config.model_type),
        description=model_config.description,
        tags=model_config.tags,
        input_schema=type_utils.to_tecton_schema(model_config.input_schema),
        output_schema=type_utils.to_tecton_schema([model_config.output_schema]),
        environments=model_config.environments,
    )

    start_request = GetModelArtifactUploadUrlRequest(model_artifact_id=model_artifact_id)
    start_response = try_and_exit(
        lambda: metadata_service.instance().GetModelArtifactUploadUrl(start_request),
        message="Failed to Upload Model Artifact",
    )

    upload_id = start_response.upload_id
    upload_parts = _upload(
        model_artifact_id=model_artifact_id,
        upload_id=upload_id,
        archive_root_dir=archive_root_abs_path,
        files=all_file_paths,
    )

    complete_upload_request = CompleteModelArtifactUploadRequest(
        model_artifact_id=model_artifact_id, upload_id=upload_id, part_etags=upload_parts
    )
    try_and_exit(
        lambda: metadata_service.instance().CompleteModelArtifactUpload(complete_upload_request),
        message="Failed to Upload Model Artifact",
    )

    printer.safe_print(f"✅ Successfully uploaded model: {model_config.name}")


def _update(model_config_file: str) -> None:
    model_config_file_path = Path(os.path.abspath(click.format_filename(model_config_file)))
    if not os.path.isfile(model_config_file):
        error_and_exit(f"{model_config_file} is not a file")

    model_configs = model_utils.get_custom_models(model_config_file_path)
    if len(model_configs) != 1:
        error_and_exit(
            f"Exactly one `ModelConfig` should be defined in the python file, provided file has {len(model_configs)}."
        )
    model_config = model_configs[0]

    update_model_artifact_request = UpdateTectonModelRequest(
        name=model_config.name,
        type=internal_model_utils.model_type_string_to_enum(model_config.model_type),
        description=model_config.description,
        tags=model_config.tags,
        input_schema=type_utils.to_tecton_schema(model_config.input_schema),
        output_schema=type_utils.to_tecton_schema([model_config.output_schema]),
        environments=model_config.environments,
    )

    try_and_exit(
        lambda: metadata_service.instance().UpdateTectonModel(update_model_artifact_request),
        message="Failed to Update Model Artifact",
    )


def create_model_artifact(
    name: str,
    model_file_path: str,
    type: ModelType,
    input_schema: schema_pb2.Schema,
    output_schema: schema_pb2.Schema,
    environments: List[str],
    tags: Optional[Dict[str, str]] = None,
    description: Optional[str] = None,
):
    create_model_artifact_request = CreateModelArtifactRequest(
        name=name,
        model_file_path=model_file_path,
        type=type,
        description=description,
        tags=tags,
        input_schema=input_schema,
        output_schema=output_schema,
        environments=environments,
    )

    create_model_artifact_response = try_and_exit(
        lambda: metadata_service.instance().CreateModelArtifact(create_model_artifact_request),
        message="Failed to Create Model Artifact",
    )
    model_artifact_id = create_model_artifact_response.model_artifact_info.id
    return model_artifact_id


def _upload(model_artifact_id: Id, upload_id: str, archive_root_dir: Path, files: List[Path]) -> Dict[int, str]:
    with tempfile.TemporaryDirectory() as tmpdir:
        output_zip_file = Path(tmpdir) / "archive.tar.gz"
        with tarfile.open(output_zip_file, mode="w:gz") as targz:
            for file in files:
                if os.path.islink(file):
                    real_path = os.readlink(file)
                    targz.add(real_path, arcname=Path(file.relative_to(archive_root_dir)), recursive=False)
                else:
                    targz.add(file, arcname=Path(file.relative_to(archive_root_dir)), recursive=False)

        file_size = output_zip_file.stat().st_size
        return dict(
            _upload_file_in_parts(
                file_size=file_size,
                upload_id=upload_id,
                model_artifact_id=model_artifact_id,
                output_zip_file=output_zip_file,
            )
        )


def _upload_file_in_parts(file_size: int, upload_id: str, model_artifact_id: Id, output_zip_file: Path) -> List[Tuple]:
    part_data_list = get_upload_parts(file_size=file_size)
    with ThreadPoolExecutor(DEFAULT_MAX_WORKERS_THREADS) as executor:
        upload_futures = [
            executor.submit(
                _upload_part,
                upload_part=part_data,
                parent_upload_id=upload_id,
                model_artifact_id=model_artifact_id,
                dependency_file_path=output_zip_file,
            )
            for part_data in part_data_list
        ]
        with tqdm(total=len(part_data_list), desc="Upload progress", ncols=100) as pbar:
            for future in as_completed(upload_futures):
                # Increment the tqdm progress bar whenever a future is done
                if future.result():
                    pbar.update(1)

        return [future.result() for future in upload_futures]


def _upload_part(
    upload_part: UploadPart,
    parent_upload_id: str,
    model_artifact_id: Id,
    dependency_file_path: Path,
) -> Tuple[int, str]:
    """Upload a part of a file.

    Args:
        upload_part (UploadPart): The part to upload.
        parent_upload_id (str): The ID of the parent upload.
        model_artifact_id (str): The ID of the Model Artifact.
        dependency_file_path (Path): The path to the file to upload.

    Returns:
        (upload_part, e-tag of that part)
    """
    request = UploadModelArtifactPartRequest(
        model_artifact_id=model_artifact_id, parent_upload_id=parent_upload_id, part_number=upload_part.part_number
    )
    response = metadata_service.instance().UploadModelArtifactPart(request)
    signed_url = response.upload_url

    with open(dependency_file_path, "rb") as fp:
        fp.seek(upload_part.offset)
        file_data = fp.read(upload_part.part_size)
        response = http.session().put(signed_url, data=file_data)
        if response.ok:
            e_tag = response.headers["ETag"]
            return (upload_part.part_number, e_tag)
        else:
            msg = f"Upload failed with status {response.status_code} and error {response.text}"
            raise ValueError(msg)


@click.option("--id", default=None, help="Model Id")
@click.option("-n", "--name", default=None, help="Model Name")
@model.command("list")
def list(id: Optional[str], name: Optional[str]):
    """List custom models."""
    if name and id:
        msg = "Specify either the Model ID or Model Name"
        raise click.ClickException(msg)
    _display_models(_list_models(id, name))


def _list_models(id_string: Optional[str] = None, name: Optional[str] = None):
    id = IdHelper.from_string(id_string) if (id_string) else None
    response = try_and_exit(
        lambda: metadata_service.instance().ListModelArtifacts(ListModelArtifactsRequest(id=id, name=name)),
        message="Failed to fetch models",
    )
    return response.models


def _display_models(models: List[ModelArtifactInfo]):
    headings = ["Id", "Name", "Created At"]
    display_table(
        headings,
        [(IdHelper.to_string(m.id), m.name, timestamp_to_string(m.created_at)) for m in models],
    )


@click.option("--id", default=None, help="Model Id")
@click.option("-n", "--name", default=None, help="Model Name")
@model.command("describe")
def describe(id: Optional[str], name: Optional[str]):
    """Describe a custom model."""
    if not (bool(name) ^ bool(id)):
        msg = "Specify either the Model ID or Model Name"
        raise click.ClickException(msg)
    models = _list_models(id, name)
    if len(models) != 1:
        printer.safe_print(f"Error: {len(models)} models found.", file=sys.stderr)
        return
    _display_model(models[0])


def _display_model(model: ModelArtifactInfo):
    printer.safe_print(f"{'Name: ': <15}{model.name}")
    printer.safe_print(f"{'ID: ': <15}{IdHelper.to_string(model.id)}")
    if model.description:
        printer.safe_print(f"{'Description: ': <15}{model.description}")
    if model.tags:
        printer.safe_print(f"{'Tags: ': <15}{model.tags}")
    printer.safe_print(f"{'Environments: ': <15}{model.environments}")
    printer.safe_print()
    printer.safe_print("Input Schema:")
    headings = ["Column Name", "Data Type"]
    display_table(
        headings,
        [(column.name, data_type_from_proto(column.offline_data_type)) for column in model.input_schema.columns],
    )
    printer.safe_print()
    printer.safe_print("Output Schema: ")
    display_table(
        headings,
        [(column.name, data_type_from_proto(column.offline_data_type)) for column in model.output_schema.columns],
    )
    printer.safe_print()


@click.option("--id", default=None, help="Model Id")
@click.option("-n", "--name", default=None, help="Model Name")
@model.command("delete")
def delete(id: Optional[str], name: Optional[str]):
    """Delete custom models."""
    if not (bool(name) ^ bool(id)):
        msg = "Specify either the Model ID or Model Name"
        raise click.ClickException(msg)
    _delete_models(id, name)
    printer.safe_print("✅ Successfully deleted model.")


def _delete_models(id_string: Optional[str], name: Optional[str]):
    id = IdHelper.from_string(id_string) if id_string else None
    try_and_exit(
        lambda: metadata_service.instance().DeleteModelArtifact(DeleteModelArtifactRequest(id=id, name=name)),
        message="Failed to delete model",
    )


@click.option("--id", default=None, help="Model Id")
@click.option("-n", "--name", default=None, help="Model Name")
@model.command("fetch")
def fetch(id: Optional[str], name: Optional[str]):
    """Fetch model artifacts for a custom model."""
    if not (bool(name) ^ bool(id)):
        msg = "Specify either the Model ID or Model Name"
        raise click.ClickException(msg)
    _fetch_model_artifacts(id, name)


def _fetch_model_artifacts(id_string: Optional[str], name: Optional[str]):
    try:
        id = IdHelper.from_string(id_string) if (id_string) else None
        response = metadata_service.instance().FetchModelArtifact(FetchModelArtifactRequest(id=id, name=name))
        try:
            tar_response = http.session().get(response.download_url)
            tar_response.raise_for_status()
        except requests.RequestException as e:
            raise SystemExit(e)

        with tarfile.open(fileobj=io.BytesIO(tar_response.content), mode="r|gz") as tar:
            tar.extractall()

    except Exception as e:
        printer.safe_print(f"Failed to fetch model: {e}", file=sys.stderr)
        sys.exit(1)
