from tecton_proto.common import id__client_pb2 as _id__client_pb2
from tecton_proto.server_groups import compute_instance_group__client_pb2 as _compute_instance_group__client_pb2
from tecton_proto.server_groups import server_group_states__client_pb2 as _server_group_states__client_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar, Mapping, Optional, Union

DESCRIPTOR: _descriptor.FileDescriptor

class ServerGroupConfig(_message.Message):
    __slots__ = ["autoscaling_policy", "aws_instance_group_config", "environment_variables", "server_group_id"]
    class EnvironmentVariablesEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: ClassVar[int]
        VALUE_FIELD_NUMBER: ClassVar[int]
        key: str
        value: str
        def __init__(self, key: Optional[str] = ..., value: Optional[str] = ...) -> None: ...
    AUTOSCALING_POLICY_FIELD_NUMBER: ClassVar[int]
    AWS_INSTANCE_GROUP_CONFIG_FIELD_NUMBER: ClassVar[int]
    ENVIRONMENT_VARIABLES_FIELD_NUMBER: ClassVar[int]
    SERVER_GROUP_ID_FIELD_NUMBER: ClassVar[int]
    autoscaling_policy: _server_group_states__client_pb2.AutoscalingPolicy
    aws_instance_group_config: _compute_instance_group__client_pb2.AWSInstanceGroupUpdateConfig
    environment_variables: _containers.ScalarMap[str, str]
    server_group_id: _id__client_pb2.Id
    def __init__(self, server_group_id: Optional[Union[_id__client_pb2.Id, Mapping]] = ..., autoscaling_policy: Optional[Union[_server_group_states__client_pb2.AutoscalingPolicy, Mapping]] = ..., aws_instance_group_config: Optional[Union[_compute_instance_group__client_pb2.AWSInstanceGroupUpdateConfig, Mapping]] = ..., environment_variables: Optional[Mapping[str, str]] = ...) -> None: ...
