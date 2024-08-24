from google.protobuf import timestamp_pb2 as _timestamp_pb2
from tecton_proto.common import container_image__client_pb2 as _container_image__client_pb2
from tecton_proto.common import id__client_pb2 as _id__client_pb2
from tecton_proto.common import server_group_status__client_pb2 as _server_group_status__client_pb2
from tecton_proto.common import server_group_type__client_pb2 as _server_group_type__client_pb2
from tecton_proto.server_groups import compute_instance_group__client_pb2 as _compute_instance_group__client_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar, Mapping, Optional, Union

DESCRIPTOR: _descriptor.FileDescriptor

class AutoscalingPolicy(_message.Message):
    __slots__ = ["autoscaling_enabled", "initialization_period_seconds", "target_concurrent_request_limit", "target_cpu_utilization", "target_percentage_node_utilization"]
    AUTOSCALING_ENABLED_FIELD_NUMBER: ClassVar[int]
    INITIALIZATION_PERIOD_SECONDS_FIELD_NUMBER: ClassVar[int]
    TARGET_CONCURRENT_REQUEST_LIMIT_FIELD_NUMBER: ClassVar[int]
    TARGET_CPU_UTILIZATION_FIELD_NUMBER: ClassVar[int]
    TARGET_PERCENTAGE_NODE_UTILIZATION_FIELD_NUMBER: ClassVar[int]
    autoscaling_enabled: bool
    initialization_period_seconds: int
    target_concurrent_request_limit: int
    target_cpu_utilization: float
    target_percentage_node_utilization: int
    def __init__(self, autoscaling_enabled: bool = ..., target_cpu_utilization: Optional[float] = ..., target_concurrent_request_limit: Optional[int] = ..., target_percentage_node_utilization: Optional[int] = ..., initialization_period_seconds: Optional[int] = ...) -> None: ...

class FeatureServerGroupState(_message.Message):
    __slots__ = ["instance_type"]
    INSTANCE_TYPE_FIELD_NUMBER: ClassVar[int]
    instance_type: str
    def __init__(self, instance_type: Optional[str] = ...) -> None: ...

class ServerGroupCapacity(_message.Message):
    __slots__ = ["desired_nodes", "max_nodes", "min_nodes"]
    DESIRED_NODES_FIELD_NUMBER: ClassVar[int]
    MAX_NODES_FIELD_NUMBER: ClassVar[int]
    MIN_NODES_FIELD_NUMBER: ClassVar[int]
    desired_nodes: int
    max_nodes: int
    min_nodes: int
    def __init__(self, min_nodes: Optional[int] = ..., max_nodes: Optional[int] = ..., desired_nodes: Optional[int] = ...) -> None: ...

class ServerGroupState(_message.Message):
    __slots__ = ["autoscaling_policy", "aws_compute_instance_group", "created_at", "environment_variables", "feature_server_group_state", "google_compute_instance_group", "last_updated_at", "name", "server_group_capacity", "server_group_id", "server_group_state_id", "status", "status_details", "transform_server_group_state", "type", "workspace", "workspace_state_id"]
    class EnvironmentVariablesEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: ClassVar[int]
        VALUE_FIELD_NUMBER: ClassVar[int]
        key: str
        value: str
        def __init__(self, key: Optional[str] = ..., value: Optional[str] = ...) -> None: ...
    AUTOSCALING_POLICY_FIELD_NUMBER: ClassVar[int]
    AWS_COMPUTE_INSTANCE_GROUP_FIELD_NUMBER: ClassVar[int]
    CREATED_AT_FIELD_NUMBER: ClassVar[int]
    ENVIRONMENT_VARIABLES_FIELD_NUMBER: ClassVar[int]
    FEATURE_SERVER_GROUP_STATE_FIELD_NUMBER: ClassVar[int]
    GOOGLE_COMPUTE_INSTANCE_GROUP_FIELD_NUMBER: ClassVar[int]
    LAST_UPDATED_AT_FIELD_NUMBER: ClassVar[int]
    NAME_FIELD_NUMBER: ClassVar[int]
    SERVER_GROUP_CAPACITY_FIELD_NUMBER: ClassVar[int]
    SERVER_GROUP_ID_FIELD_NUMBER: ClassVar[int]
    SERVER_GROUP_STATE_ID_FIELD_NUMBER: ClassVar[int]
    STATUS_DETAILS_FIELD_NUMBER: ClassVar[int]
    STATUS_FIELD_NUMBER: ClassVar[int]
    TRANSFORM_SERVER_GROUP_STATE_FIELD_NUMBER: ClassVar[int]
    TYPE_FIELD_NUMBER: ClassVar[int]
    WORKSPACE_FIELD_NUMBER: ClassVar[int]
    WORKSPACE_STATE_ID_FIELD_NUMBER: ClassVar[int]
    autoscaling_policy: AutoscalingPolicy
    aws_compute_instance_group: _compute_instance_group__client_pb2.AWSInstanceGroup
    created_at: _timestamp_pb2.Timestamp
    environment_variables: _containers.ScalarMap[str, str]
    feature_server_group_state: FeatureServerGroupState
    google_compute_instance_group: _compute_instance_group__client_pb2.GoogleCloudInstanceGroup
    last_updated_at: _timestamp_pb2.Timestamp
    name: str
    server_group_capacity: ServerGroupCapacity
    server_group_id: _id__client_pb2.Id
    server_group_state_id: _id__client_pb2.Id
    status: _server_group_status__client_pb2.ServerGroupStatus
    status_details: str
    transform_server_group_state: TransformServerGroupState
    type: _server_group_type__client_pb2.ServerGroupType
    workspace: str
    workspace_state_id: _id__client_pb2.Id
    def __init__(self, server_group_state_id: Optional[Union[_id__client_pb2.Id, Mapping]] = ..., server_group_id: Optional[Union[_id__client_pb2.Id, Mapping]] = ..., name: Optional[str] = ..., autoscaling_policy: Optional[Union[AutoscalingPolicy, Mapping]] = ..., status: Optional[Union[_server_group_status__client_pb2.ServerGroupStatus, str]] = ..., type: Optional[Union[_server_group_type__client_pb2.ServerGroupType, str]] = ..., status_details: Optional[str] = ..., server_group_capacity: Optional[Union[ServerGroupCapacity, Mapping]] = ..., created_at: Optional[Union[_timestamp_pb2.Timestamp, Mapping]] = ..., last_updated_at: Optional[Union[_timestamp_pb2.Timestamp, Mapping]] = ..., transform_server_group_state: Optional[Union[TransformServerGroupState, Mapping]] = ..., feature_server_group_state: Optional[Union[FeatureServerGroupState, Mapping]] = ..., workspace: Optional[str] = ..., workspace_state_id: Optional[Union[_id__client_pb2.Id, Mapping]] = ..., environment_variables: Optional[Mapping[str, str]] = ..., aws_compute_instance_group: Optional[Union[_compute_instance_group__client_pb2.AWSInstanceGroup, Mapping]] = ..., google_compute_instance_group: Optional[Union[_compute_instance_group__client_pb2.GoogleCloudInstanceGroup, Mapping]] = ...) -> None: ...

class TransformServerGroupState(_message.Message):
    __slots__ = ["environment_id", "environment_name", "image_info"]
    ENVIRONMENT_ID_FIELD_NUMBER: ClassVar[int]
    ENVIRONMENT_NAME_FIELD_NUMBER: ClassVar[int]
    IMAGE_INFO_FIELD_NUMBER: ClassVar[int]
    environment_id: str
    environment_name: str
    image_info: _container_image__client_pb2.ContainerImage
    def __init__(self, environment_id: Optional[str] = ..., environment_name: Optional[str] = ..., image_info: Optional[Union[_container_image__client_pb2.ContainerImage, Mapping]] = ...) -> None: ...
