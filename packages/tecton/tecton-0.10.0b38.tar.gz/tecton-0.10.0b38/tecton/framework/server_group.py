from typing import Dict
from typing import Optional

import attrs
from typeguard import typechecked

from tecton._internals import sdk_decorators
from tecton._internals import validations_api
from tecton.framework import base_tecton_object
from tecton_core import conf
from tecton_core import id_helper
from tecton_core import specs
from tecton_core.repo_file_handler import construct_fco_source_info
from tecton_proto.args import basic_info__client_pb2 as basic_info_pb2
from tecton_proto.args import fco_args__client_pb2 as fco_args_pb2
from tecton_proto.args import server_group__client_pb2 as server_group_pb2
from tecton_proto.common import server_group_type__client_pb2 as server_group_type_pb2
from tecton_proto.validation import validator__client_pb2 as validator_pb2


@attrs.define(eq=False)
class FeatureServerGroup(base_tecton_object.BaseTectonObject):
    """Configuration used to specify the feature server group options.

    Once deployed in production, each feature service
    """

    _args: Optional[server_group_pb2.ServerGroupArgs] = attrs.field(repr=False, on_setattr=attrs.setters.frozen)
    autoscaling_enabled: bool = attrs.field(repr=False)
    min_nodes: int = attrs.field(repr=False)
    max_nodes: int = attrs.field(repr=False)
    desired_nodes: int = attrs.field(repr=False)
    _spec: Optional[specs.FeatureServerGroupSpec] = attrs.field(repr=False)

    def __init__(
        self,
        *,
        name: str,
        description: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None,
        owner: Optional[str] = None,
        prevent_destroy: bool = False,
        autoscaling_enabled: bool = False,
        min_nodes: int = 0,
        max_nodes: int = 0,
        desired_nodes: int = 0,
    ):
        """
        Instantiates a new FeatureServerGroup.

        :param name: A unique name for the Feature Server Group.
        :param description: A human-readable description.
        :param tags: Tags associated with this Tecton Object (key-value pairs of arbitrary metadata).
        :param owner: Owner name (typically the email of the primary maintainer).
        :param prevent_destroy: If True, this Tecton object will be blocked from being deleted or re-created (i.e. a
            destructive update) during tecton plan/apply. To remove or update this object, `prevent_destroy` must be set to False
            via the same tecton apply or a separate tecton apply. `prevent_destroy` can be used to prevent accidental changes
            such as inadvertantly deleting a Feature Service used in production or recreating a Feature View that
            triggers expensive rematerialization jobs. `prevent_destroy` also blocks changes to dependent Tecton objects
            that would trigger a recreate of the tagged object, e.g. if `prevent_destroy` is set on a Feature Service,
            that will also prevent deletions or re-creates of Feature Views used in that service. `prevent_destroy` is
            only enforced in live (i.e. non-dev) workspaces.
        :param autoscaling_enabled: whether to enable autoscaling on this Feature Server Group.
        :param min_nodes: The minimum number of nodes in this Feature Server Group.
        :param max_nodes: The maximum number of nodes in this Feature Server Group.
        :param desired_nodes: The desired nodes count for this Feature Server Group. Must set if autoscaling is false.
        """
        args = server_group_pb2.ServerGroupArgs(
            server_group_id=id_helper.IdHelper.generate_id(),
            info=basic_info_pb2.BasicInfo(name=name, description=description, tags=tags, owner=owner),
            prevent_destroy=prevent_destroy,
            autoscaling_enabled=autoscaling_enabled,
            min_nodes=min_nodes,
            max_nodes=max_nodes,
            desired_nodes=desired_nodes,
            feature_server_group_args=server_group_pb2.FeatureServerGroupArgs(),
            server_group_type=server_group_type_pb2.SERVER_GROUP_TYPE_FEATURE_SERVER_GROUP,
        )
        info = base_tecton_object.TectonObjectInfo.from_args_proto(args.info, args.server_group_id)
        source_info = construct_fco_source_info(args.server_group_id)
        self.__attrs_init__(
            info=info,
            args=args,
            spec=None,
            source_info=source_info,
            min_nodes=min_nodes,
            max_nodes=max_nodes,
            autoscaling_enabled=autoscaling_enabled,
            desired_nodes=desired_nodes,
        )
        self._spec = specs.FeatureServerGroupSpec.from_args_proto(args)
        if not conf.get_bool("TECTON_SKIP_OBJECT_VALIDATION"):
            self._validate()
        base_tecton_object._register_local_object(self)

    @sdk_decorators.assert_local_object
    def _build_args(self) -> fco_args_pb2.FcoArgs:
        return fco_args_pb2.FcoArgs(server_group=self._args)

    @classmethod
    @typechecked
    def _from_spec(cls, spec: specs.FeatureServerGroupSpec) -> "FeatureServerGroup":
        """Create a Feature Service from directly from a spec. Specs are assumed valid and will not be re-validated."""
        info = base_tecton_object.TectonObjectInfo.from_spec(spec)
        obj = cls.__new__(cls)
        obj.__attrs_init__(
            info=info,
            spec=spec,
            args=None,
            source_info=None,
            min_nodes=spec.min_nodes,
            max_nodes=spec.max_nodes,
            autoscaling_enabled=spec.autoscaling_enabled,
            desired_nodes=spec.desired_nodes,
        )
        return obj

    def _build_fco_validation_args(self) -> validator_pb2.FcoValidationArgs:
        if self.info._is_local_object:
            assert self._args_supplement is not None
            return validator_pb2.FcoValidationArgs(
                server_group=validator_pb2.ServerGroupValidationArgs(
                    args=self._args,
                )
            )
        else:
            return self._spec.validation_args

    def _validate(self) -> None:
        validations_api.run_backend_validation_and_assert_valid(
            self,
            validator_pb2.ValidationRequest(
                validation_args=[self._build_fco_validation_args()],
            ),
        )


@attrs.define(eq=False)
class TransformServerGroup(base_tecton_object.BaseTectonObject):
    """Configuration used to specify the transform server group.

    Once deployed in production, each feature service
    """

    _args: Optional[server_group_pb2.ServerGroupArgs] = attrs.field(repr=False, on_setattr=attrs.setters.frozen)
    environment: str = attrs.field(repr=False)
    autoscaling_enabled: bool = attrs.field(repr=False)
    min_nodes: int = attrs.field(repr=False)
    max_nodes: int = attrs.field(repr=False)
    desired_nodes: int = attrs.field(repr=False)
    _spec: Optional[specs.TransformServerGroupSpec] = attrs.field(repr=False)

    def __init__(
        self,
        *,
        name: str,
        description: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None,
        owner: Optional[str] = None,
        prevent_destroy: bool = False,
        autoscaling_enabled: bool = False,
        min_nodes: int = 0,
        max_nodes: int = 0,
        desired_nodes: int = 0,
        environment: Optional[str] = None,
    ):
        """
        Instantiates a new TransformServerGroup.

        :param name: A unique name for the Transform Server Group.
        :param description: A human-readable description.
        :param tags: Tags associated with this Tecton Object (key-value pairs of arbitrary metadata).
        :param owner: Owner name (typically the email of the primary maintainer).
        :param prevent_destroy: If True, this Tecton object will be blocked from being deleted or re-created (i.e. a
            destructive update) during tecton plan/apply. To remove or update this object, `prevent_destroy` must be set to False
            via the same tecton apply or a separate tecton apply. `prevent_destroy` can be used to prevent accidental changes
            such as inadvertantly deleting a Feature Service used in production or recreating a Feature View that
            triggers expensive rematerialization jobs. `prevent_destroy` also blocks changes to dependent Tecton objects
            that would trigger a recreate of the tagged object, e.g. if `prevent_destroy` is set on a Feature Service,
            that will also prevent deletions or re-creates of Feature Views used in that service. `prevent_destroy` is
            only enforced in live (i.e. non-dev) workspaces.
        :param autoscaling_enabled: whether to enable autoscaling on this Transform Server Group.
        :param min_nodes: The minimum number of nodes in this Transform Server Group.
        :param max_nodes: The maximum number of nodes in this Transform Server Group.
        :param desired_nodes: The desired nodes count for this Transform Server Group. Must set if autoscaling is false.
        :param environment: The name of the Python environments.
        """
        args = server_group_pb2.ServerGroupArgs(
            server_group_id=id_helper.IdHelper.generate_id(),
            info=basic_info_pb2.BasicInfo(name=name, description=description, tags=tags, owner=owner),
            prevent_destroy=prevent_destroy,
            autoscaling_enabled=autoscaling_enabled,
            min_nodes=min_nodes,
            max_nodes=max_nodes,
            desired_nodes=desired_nodes,
            transform_server_group_args=server_group_pb2.TransformServerGroupArgs(environment=environment),
            server_group_type=server_group_type_pb2.SERVER_GROUP_TYPE_TRANSFORM_SERVER_GROUP,
        )
        info = base_tecton_object.TectonObjectInfo.from_args_proto(args.info, args.server_group_id)
        source_info = construct_fco_source_info(args.server_group_id)
        self.__attrs_init__(
            info=info,
            args=args,
            spec=None,
            source_info=source_info,
            min_nodes=min_nodes,
            max_nodes=max_nodes,
            autoscaling_enabled=autoscaling_enabled,
            desired_nodes=desired_nodes,
            environment=environment,
        )
        self._spec = specs.TransformServerGroupSpec.from_args_proto(args)
        if not conf.get_bool("TECTON_SKIP_OBJECT_VALIDATION"):
            self._validate()
        base_tecton_object._register_local_object(self)

    @sdk_decorators.assert_local_object
    def _build_args(self) -> fco_args_pb2.FcoArgs:
        return fco_args_pb2.FcoArgs(server_group=self._args)

    @classmethod
    @typechecked
    def _from_spec(cls, spec: specs.TransformServerGroupSpec) -> "TransformServerGroup":
        """Create a Feature Service from directly from a spec. Specs are assumed valid and will not be re-validated."""
        info = base_tecton_object.TectonObjectInfo.from_spec(spec)
        obj = cls.__new__(cls)
        obj.__attrs_init__(
            info=info,
            spec=spec,
            args=None,
            source_info=None,
            min_nodes=spec.min_nodes,
            max_nodes=spec.max_nodes,
            autoscaling_enabled=spec.autoscaling_enabled,
            desired_nodes=spec.desired_nodes,
        )
        return obj

    def _build_fco_validation_args(self) -> validator_pb2.FcoValidationArgs:
        if self.info._is_local_object:
            assert self._args_supplement is not None
            return validator_pb2.FcoValidationArgs(
                server_group=validator_pb2.ServerGroupValidationArgs(
                    args=self._args,
                )
            )
        else:
            return self._spec.validation_args

    def _validate(self) -> None:
        validations_api.run_backend_validation_and_assert_valid(
            self,
            validator_pb2.ValidationRequest(
                validation_args=[self._build_fco_validation_args()],
            ),
        )
