from tecton_proto.common import container_image__client_pb2 as _container_image__client_pb2
from tecton_proto.common import id__client_pb2 as _id__client_pb2
from tecton_proto.common import server_group_type__client_pb2 as _server_group_type__client_pb2
from tecton_proto.data import fco_metadata__client_pb2 as _fco_metadata__client_pb2
from tecton_proto.validation import validator__client_pb2 as _validator__client_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar, Mapping, Optional, Union

DESCRIPTOR: _descriptor.FileDescriptor

class FeatureServerGroup(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class ServerGroup(_message.Message):
    __slots__ = ["autoscaling_enabled", "desired_nodes", "fco_metadata", "feature_server_group", "max_nodes", "min_nodes", "options", "server_group_id", "transform_server_group", "type", "validation_args"]
    class OptionsEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: ClassVar[int]
        VALUE_FIELD_NUMBER: ClassVar[int]
        key: str
        value: str
        def __init__(self, key: Optional[str] = ..., value: Optional[str] = ...) -> None: ...
    AUTOSCALING_ENABLED_FIELD_NUMBER: ClassVar[int]
    DESIRED_NODES_FIELD_NUMBER: ClassVar[int]
    FCO_METADATA_FIELD_NUMBER: ClassVar[int]
    FEATURE_SERVER_GROUP_FIELD_NUMBER: ClassVar[int]
    MAX_NODES_FIELD_NUMBER: ClassVar[int]
    MIN_NODES_FIELD_NUMBER: ClassVar[int]
    OPTIONS_FIELD_NUMBER: ClassVar[int]
    SERVER_GROUP_ID_FIELD_NUMBER: ClassVar[int]
    TRANSFORM_SERVER_GROUP_FIELD_NUMBER: ClassVar[int]
    TYPE_FIELD_NUMBER: ClassVar[int]
    VALIDATION_ARGS_FIELD_NUMBER: ClassVar[int]
    autoscaling_enabled: bool
    desired_nodes: int
    fco_metadata: _fco_metadata__client_pb2.FcoMetadata
    feature_server_group: FeatureServerGroup
    max_nodes: int
    min_nodes: int
    options: _containers.ScalarMap[str, str]
    server_group_id: _id__client_pb2.Id
    transform_server_group: TransformServerGroup
    type: _server_group_type__client_pb2.ServerGroupType
    validation_args: _validator__client_pb2.ServerGroupValidationArgs
    def __init__(self, server_group_id: Optional[Union[_id__client_pb2.Id, Mapping]] = ..., fco_metadata: Optional[Union[_fco_metadata__client_pb2.FcoMetadata, Mapping]] = ..., type: Optional[Union[_server_group_type__client_pb2.ServerGroupType, str]] = ..., min_nodes: Optional[int] = ..., max_nodes: Optional[int] = ..., autoscaling_enabled: bool = ..., desired_nodes: Optional[int] = ..., transform_server_group: Optional[Union[TransformServerGroup, Mapping]] = ..., feature_server_group: Optional[Union[FeatureServerGroup, Mapping]] = ..., options: Optional[Mapping[str, str]] = ..., validation_args: Optional[Union[_validator__client_pb2.ServerGroupValidationArgs, Mapping]] = ...) -> None: ...

class TransformServerGroup(_message.Message):
    __slots__ = ["environment_id", "environment_name", "image_info"]
    ENVIRONMENT_ID_FIELD_NUMBER: ClassVar[int]
    ENVIRONMENT_NAME_FIELD_NUMBER: ClassVar[int]
    IMAGE_INFO_FIELD_NUMBER: ClassVar[int]
    environment_id: str
    environment_name: str
    image_info: _container_image__client_pb2.ContainerImage
    def __init__(self, environment_id: Optional[str] = ..., environment_name: Optional[str] = ..., image_info: Optional[Union[_container_image__client_pb2.ContainerImage, Mapping]] = ...) -> None: ...
