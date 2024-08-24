import ast
import os
import sys
from pathlib import Path
from typing import Callable
from typing import List

from tecton.cli import printer
from tecton_proto.modelartifactservice.model_artifact_service__client_pb2 import ModelType


def error_and_exit(message: str):
    error_message = f"⛔ {message}"
    printer.safe_print(error_message, file=sys.stderr)
    sys.exit(1)


def _find_function_and_validate(objects: List[ast.FunctionDef], name: str, condition: Callable[[int], bool]):
    find_object = [obj for obj in objects if obj.name == name]
    if not condition(len(find_object)):
        error_and_exit(f"Exactly one `{name}` function should be found in the model file.")


def validate(model_file_path: Path, files: List[Path], archive_root_path: Path) -> None:
    for file in files:
        if not os.path.isfile(file):
            error_and_exit(f"File {file} defined in ModelConfig does not exist.")
        if archive_root_path and archive_root_path not in file.parents:
            error_and_exit("All `artifact_files` must be within directory containing model config file.")

    model_file_text = model_file_path.read_text()
    ast_module = ast.parse(model_file_text)
    functions = [obj for obj in ast_module.body if type(obj) == ast.FunctionDef]

    _find_function_and_validate(functions, "load_context", lambda x: x == 1)
    _find_function_and_validate(functions, "preprocessor", lambda x: x <= 1)
    _find_function_and_validate(functions, "postprocessor", lambda x: x <= 1)


def model_type_string_to_enum(model_type: str) -> ModelType:
    if model_type == "pytorch":
        return ModelType.PYTORCH
    else:
        return ModelType.MODEL_TYPE_UNSPECIFIED
