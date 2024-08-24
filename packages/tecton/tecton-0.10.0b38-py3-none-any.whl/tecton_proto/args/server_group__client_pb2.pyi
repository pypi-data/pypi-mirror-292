from tecton_proto.args import basic_info__client_pb2 as _basic_info__client_pb2
from tecton_proto.args import diff_options__client_pb2 as _diff_options__client_pb2
from tecton_proto.common import id__client_pb2 as _id__client_pb2
from tecton_proto.common import server_group_type__client_pb2 as _server_group_type__client_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar, Mapping, Optional, Union

DESCRIPTOR: _descriptor.FileDescriptor

class FeatureServerGroupArgs(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class ServerGroupArgs(_message.Message):
    __slots__ = ["autoscaling_enabled", "desired_nodes", "feature_server_group_args", "info", "max_nodes", "min_nodes", "options", "prevent_destroy", "server_group_id", "server_group_type", "transform_server_group_args"]
    class OptionsEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: ClassVar[int]
        VALUE_FIELD_NUMBER: ClassVar[int]
        key: str
        value: str
        def __init__(self, key: Optional[str] = ..., value: Optional[str] = ...) -> None: ...
    AUTOSCALING_ENABLED_FIELD_NUMBER: ClassVar[int]
    DESIRED_NODES_FIELD_NUMBER: ClassVar[int]
    FEATURE_SERVER_GROUP_ARGS_FIELD_NUMBER: ClassVar[int]
    INFO_FIELD_NUMBER: ClassVar[int]
    MAX_NODES_FIELD_NUMBER: ClassVar[int]
    MIN_NODES_FIELD_NUMBER: ClassVar[int]
    OPTIONS_FIELD_NUMBER: ClassVar[int]
    PREVENT_DESTROY_FIELD_NUMBER: ClassVar[int]
    SERVER_GROUP_ID_FIELD_NUMBER: ClassVar[int]
    SERVER_GROUP_TYPE_FIELD_NUMBER: ClassVar[int]
    TRANSFORM_SERVER_GROUP_ARGS_FIELD_NUMBER: ClassVar[int]
    autoscaling_enabled: bool
    desired_nodes: int
    feature_server_group_args: FeatureServerGroupArgs
    info: _basic_info__client_pb2.BasicInfo
    max_nodes: int
    min_nodes: int
    options: _containers.ScalarMap[str, str]
    prevent_destroy: bool
    server_group_id: _id__client_pb2.Id
    server_group_type: _server_group_type__client_pb2.ServerGroupType
    transform_server_group_args: TransformServerGroupArgs
    def __init__(self, server_group_id: Optional[Union[_id__client_pb2.Id, Mapping]] = ..., info: Optional[Union[_basic_info__client_pb2.BasicInfo, Mapping]] = ..., server_group_type: Optional[Union[_server_group_type__client_pb2.ServerGroupType, str]] = ..., min_nodes: Optional[int] = ..., max_nodes: Optional[int] = ..., autoscaling_enabled: bool = ..., desired_nodes: Optional[int] = ..., transform_server_group_args: Optional[Union[TransformServerGroupArgs, Mapping]] = ..., feature_server_group_args: Optional[Union[FeatureServerGroupArgs, Mapping]] = ..., prevent_destroy: bool = ..., options: Optional[Mapping[str, str]] = ...) -> None: ...

class TransformServerGroupArgs(_message.Message):
    __slots__ = ["environment"]
    ENVIRONMENT_FIELD_NUMBER: ClassVar[int]
    environment: str
    def __init__(self, environment: Optional[str] = ...) -> None: ...
