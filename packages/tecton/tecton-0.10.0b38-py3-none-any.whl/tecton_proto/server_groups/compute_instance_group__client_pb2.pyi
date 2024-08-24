from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar, Iterable, Mapping, Optional, Union

DESCRIPTOR: _descriptor.FileDescriptor

class AWSInstanceGroup(_message.Message):
    __slots__ = ["ami_image_id", "autoscaling_group_arn", "autoscaling_group_name", "health_check_path", "iam_instance_profile_arn", "instance_type", "launch_template_id", "port", "region", "security_group_ids", "subnet_ids", "tags"]
    class TagsEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: ClassVar[int]
        VALUE_FIELD_NUMBER: ClassVar[int]
        key: str
        value: str
        def __init__(self, key: Optional[str] = ..., value: Optional[str] = ...) -> None: ...
    AMI_IMAGE_ID_FIELD_NUMBER: ClassVar[int]
    AUTOSCALING_GROUP_ARN_FIELD_NUMBER: ClassVar[int]
    AUTOSCALING_GROUP_NAME_FIELD_NUMBER: ClassVar[int]
    HEALTH_CHECK_PATH_FIELD_NUMBER: ClassVar[int]
    IAM_INSTANCE_PROFILE_ARN_FIELD_NUMBER: ClassVar[int]
    INSTANCE_TYPE_FIELD_NUMBER: ClassVar[int]
    LAUNCH_TEMPLATE_ID_FIELD_NUMBER: ClassVar[int]
    PORT_FIELD_NUMBER: ClassVar[int]
    REGION_FIELD_NUMBER: ClassVar[int]
    SECURITY_GROUP_IDS_FIELD_NUMBER: ClassVar[int]
    SUBNET_IDS_FIELD_NUMBER: ClassVar[int]
    TAGS_FIELD_NUMBER: ClassVar[int]
    ami_image_id: str
    autoscaling_group_arn: str
    autoscaling_group_name: str
    health_check_path: str
    iam_instance_profile_arn: str
    instance_type: str
    launch_template_id: str
    port: int
    region: str
    security_group_ids: _containers.RepeatedScalarFieldContainer[str]
    subnet_ids: _containers.RepeatedScalarFieldContainer[str]
    tags: _containers.ScalarMap[str, str]
    def __init__(self, autoscaling_group_arn: Optional[str] = ..., autoscaling_group_name: Optional[str] = ..., region: Optional[str] = ..., port: Optional[int] = ..., health_check_path: Optional[str] = ..., instance_type: Optional[str] = ..., ami_image_id: Optional[str] = ..., iam_instance_profile_arn: Optional[str] = ..., security_group_ids: Optional[Iterable[str]] = ..., subnet_ids: Optional[Iterable[str]] = ..., launch_template_id: Optional[str] = ..., tags: Optional[Mapping[str, str]] = ...) -> None: ...

class AWSInstanceGroupUpdateConfig(_message.Message):
    __slots__ = ["ami_image_id", "instance_type", "launch_template_id", "tags"]
    class TagsEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: ClassVar[int]
        VALUE_FIELD_NUMBER: ClassVar[int]
        key: str
        value: str
        def __init__(self, key: Optional[str] = ..., value: Optional[str] = ...) -> None: ...
    AMI_IMAGE_ID_FIELD_NUMBER: ClassVar[int]
    INSTANCE_TYPE_FIELD_NUMBER: ClassVar[int]
    LAUNCH_TEMPLATE_ID_FIELD_NUMBER: ClassVar[int]
    TAGS_FIELD_NUMBER: ClassVar[int]
    ami_image_id: str
    instance_type: str
    launch_template_id: str
    tags: _containers.ScalarMap[str, str]
    def __init__(self, instance_type: Optional[str] = ..., ami_image_id: Optional[str] = ..., launch_template_id: Optional[str] = ..., tags: Optional[Mapping[str, str]] = ...) -> None: ...

class AWSTargetGroup(_message.Message):
    __slots__ = ["arn", "instance_group", "name"]
    ARN_FIELD_NUMBER: ClassVar[int]
    INSTANCE_GROUP_FIELD_NUMBER: ClassVar[int]
    NAME_FIELD_NUMBER: ClassVar[int]
    arn: str
    instance_group: AWSInstanceGroup
    name: str
    def __init__(self, arn: Optional[str] = ..., name: Optional[str] = ..., instance_group: Optional[Union[AWSInstanceGroup, Mapping]] = ...) -> None: ...

class GoogleCloudBackendService(_message.Message):
    __slots__ = ["instance_group", "project", "region", "target_id"]
    INSTANCE_GROUP_FIELD_NUMBER: ClassVar[int]
    PROJECT_FIELD_NUMBER: ClassVar[int]
    REGION_FIELD_NUMBER: ClassVar[int]
    TARGET_ID_FIELD_NUMBER: ClassVar[int]
    instance_group: GoogleCloudInstanceGroup
    project: str
    region: str
    target_id: str
    def __init__(self, target_id: Optional[str] = ..., project: Optional[str] = ..., region: Optional[str] = ..., instance_group: Optional[Union[GoogleCloudInstanceGroup, Mapping]] = ...) -> None: ...

class GoogleCloudInstanceGroup(_message.Message):
    __slots__ = ["project", "region", "target_id"]
    PROJECT_FIELD_NUMBER: ClassVar[int]
    REGION_FIELD_NUMBER: ClassVar[int]
    TARGET_ID_FIELD_NUMBER: ClassVar[int]
    project: str
    region: str
    target_id: str
    def __init__(self, project: Optional[str] = ..., region: Optional[str] = ..., target_id: Optional[str] = ...) -> None: ...

class LoadBalancerTarget(_message.Message):
    __slots__ = ["aws_target_group", "google_backend_service"]
    AWS_TARGET_GROUP_FIELD_NUMBER: ClassVar[int]
    GOOGLE_BACKEND_SERVICE_FIELD_NUMBER: ClassVar[int]
    aws_target_group: AWSTargetGroup
    google_backend_service: GoogleCloudBackendService
    def __init__(self, aws_target_group: Optional[Union[AWSTargetGroup, Mapping]] = ..., google_backend_service: Optional[Union[GoogleCloudBackendService, Mapping]] = ...) -> None: ...
