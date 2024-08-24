from typeguard import typechecked

from tecton_core.specs import tecton_object_spec
from tecton_core.specs import utils
from tecton_proto.args import server_group__client_pb2 as server_group__arg_pb2
from tecton_proto.data import server_group__client_pb2 as server_group__data_pb2
from tecton_proto.validation import validator__client_pb2 as validator_pb2


__all__ = [
    "FeatureServerGroupSpec",
    "TransformServerGroupSpec",
]


@utils.frozen_strict
class FeatureServerGroupSpec(tecton_object_spec.TectonObjectSpec):
    """Base class for feature server group specs."""

    min_nodes: int
    max_nodes: int
    autoscaling_enabled: bool
    desired_nodes: int

    @classmethod
    @typechecked
    def from_data_proto(cls, proto: server_group__data_pb2.ServerGroup) -> "FeatureServerGroupSpec":
        return cls(
            metadata=tecton_object_spec.TectonObjectMetadataSpec.from_data_proto(
                proto.server_group_id, proto.fco_metadata
            ),
            min_nodes=proto.min_nodes,
            max_nodes=proto.max_nodes,
            autoscaling_enabled=proto.autoscaling_enabled,
            desired_nodes=proto.desired_nodes,
            validation_args=validator_pb2.FcoValidationArgs(server_group=proto.validation_args),
        )

    @classmethod
    @typechecked
    def from_args_proto(cls, proto: server_group__arg_pb2.ServerGroupArgs) -> "FeatureServerGroupSpec":
        return cls(
            metadata=tecton_object_spec.TectonObjectMetadataSpec.from_args_proto(proto.server_group_id, proto.info),
            min_nodes=proto.min_nodes,
            max_nodes=proto.max_nodes,
            autoscaling_enabled=proto.autoscaling_enabled,
            desired_nodes=proto.desired_nodes,
            validation_args=None,
        )


@utils.frozen_strict
class TransformServerGroupSpec(tecton_object_spec.TectonObjectSpec):
    """Base class for feature server group specs."""

    min_nodes: int
    max_nodes: int
    autoscaling_enabled: bool
    desired_nodes: int
    environment: str

    @classmethod
    @typechecked
    def from_data_proto(cls, proto: server_group__data_pb2.ServerGroup) -> "TransformServerGroupSpec":
        return cls(
            metadata=tecton_object_spec.TectonObjectMetadataSpec.from_data_proto(
                proto.server_group_id, proto.fco_metadata
            ),
            min_nodes=proto.min_nodes,
            max_nodes=proto.max_nodes,
            autoscaling_enabled=proto.autoscaling_enabled,
            desired_nodes=proto.desired_nodes,
            environment=proto.transform_server_group.environment_name,
            validation_args=validator_pb2.FcoValidationArgs(server_group=proto.validation_args),
        )

    @classmethod
    @typechecked
    def from_args_proto(cls, proto: server_group__arg_pb2.ServerGroupArgs) -> "TransformServerGroupSpec":
        return cls(
            metadata=tecton_object_spec.TectonObjectMetadataSpec.from_args_proto(proto.server_group_id, proto.info),
            min_nodes=proto.min_nodes,
            max_nodes=proto.max_nodes,
            autoscaling_enabled=proto.autoscaling_enabled,
            desired_nodes=proto.desired_nodes,
            environment=proto.transform_server_group_args.environment,
            validation_args=None,
        )
