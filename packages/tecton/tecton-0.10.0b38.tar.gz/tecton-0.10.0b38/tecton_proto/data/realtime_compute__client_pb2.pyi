from tecton_proto.server_groups import compute_instance_group__client_pb2 as _compute_instance_group__client_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar, Mapping, Optional, Union

DESCRIPTOR: _descriptor.FileDescriptor

class ColocatedComputeConfig(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class OnlineComputeConfig(_message.Message):
    __slots__ = ["aws_compute_instance_group", "colocated_compute", "google_compute_instance_group", "remote_compute"]
    AWS_COMPUTE_INSTANCE_GROUP_FIELD_NUMBER: ClassVar[int]
    COLOCATED_COMPUTE_FIELD_NUMBER: ClassVar[int]
    GOOGLE_COMPUTE_INSTANCE_GROUP_FIELD_NUMBER: ClassVar[int]
    REMOTE_COMPUTE_FIELD_NUMBER: ClassVar[int]
    aws_compute_instance_group: _compute_instance_group__client_pb2.AWSInstanceGroup
    colocated_compute: ColocatedComputeConfig
    google_compute_instance_group: _compute_instance_group__client_pb2.GoogleCloudInstanceGroup
    remote_compute: RemoteFunctionComputeConfig
    def __init__(self, colocated_compute: Optional[Union[ColocatedComputeConfig, Mapping]] = ..., remote_compute: Optional[Union[RemoteFunctionComputeConfig, Mapping]] = ..., aws_compute_instance_group: Optional[Union[_compute_instance_group__client_pb2.AWSInstanceGroup, Mapping]] = ..., google_compute_instance_group: Optional[Union[_compute_instance_group__client_pb2.GoogleCloudInstanceGroup, Mapping]] = ...) -> None: ...

class RemoteFunctionComputeConfig(_message.Message):
    __slots__ = ["function_uri", "id", "name"]
    FUNCTION_URI_FIELD_NUMBER: ClassVar[int]
    ID_FIELD_NUMBER: ClassVar[int]
    NAME_FIELD_NUMBER: ClassVar[int]
    function_uri: str
    id: str
    name: str
    def __init__(self, id: Optional[str] = ..., name: Optional[str] = ..., function_uri: Optional[str] = ...) -> None: ...
