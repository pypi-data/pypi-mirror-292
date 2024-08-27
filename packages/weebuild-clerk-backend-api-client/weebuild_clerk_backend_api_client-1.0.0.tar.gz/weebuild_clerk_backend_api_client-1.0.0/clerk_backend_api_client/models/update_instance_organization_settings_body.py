from typing import Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="UpdateInstanceOrganizationSettingsBody")


@_attrs_define
class UpdateInstanceOrganizationSettingsBody:
    """
    Attributes:
        enabled (Union[None, Unset, bool]):
        max_allowed_memberships (Union[None, Unset, int]):
        admin_delete_enabled (Union[None, Unset, bool]):
        domains_enabled (Union[None, Unset, bool]):
        domains_enrollment_modes (Union[Unset, List[str]]): Specify which enrollment modes to enable for your
            Organization Domains.
            Supported modes are 'automatic_invitation' & 'automatic_suggestion'.
        creator_role_id (Union[Unset, str]): Specify what the default organization role is for an organization creator.
        domains_default_role_id (Union[Unset, str]): Specify what the default organization role is for the organization
            domains.
    """

    enabled: Union[None, Unset, bool] = UNSET
    max_allowed_memberships: Union[None, Unset, int] = UNSET
    admin_delete_enabled: Union[None, Unset, bool] = UNSET
    domains_enabled: Union[None, Unset, bool] = UNSET
    domains_enrollment_modes: Union[Unset, List[str]] = UNSET
    creator_role_id: Union[Unset, str] = UNSET
    domains_default_role_id: Union[Unset, str] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        enabled: Union[None, Unset, bool]
        if isinstance(self.enabled, Unset):
            enabled = UNSET
        else:
            enabled = self.enabled

        max_allowed_memberships: Union[None, Unset, int]
        if isinstance(self.max_allowed_memberships, Unset):
            max_allowed_memberships = UNSET
        else:
            max_allowed_memberships = self.max_allowed_memberships

        admin_delete_enabled: Union[None, Unset, bool]
        if isinstance(self.admin_delete_enabled, Unset):
            admin_delete_enabled = UNSET
        else:
            admin_delete_enabled = self.admin_delete_enabled

        domains_enabled: Union[None, Unset, bool]
        if isinstance(self.domains_enabled, Unset):
            domains_enabled = UNSET
        else:
            domains_enabled = self.domains_enabled

        domains_enrollment_modes: Union[Unset, List[str]] = UNSET
        if not isinstance(self.domains_enrollment_modes, Unset):
            domains_enrollment_modes = self.domains_enrollment_modes

        creator_role_id = self.creator_role_id

        domains_default_role_id = self.domains_default_role_id

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if enabled is not UNSET:
            field_dict["enabled"] = enabled
        if max_allowed_memberships is not UNSET:
            field_dict["max_allowed_memberships"] = max_allowed_memberships
        if admin_delete_enabled is not UNSET:
            field_dict["admin_delete_enabled"] = admin_delete_enabled
        if domains_enabled is not UNSET:
            field_dict["domains_enabled"] = domains_enabled
        if domains_enrollment_modes is not UNSET:
            field_dict["domains_enrollment_modes"] = domains_enrollment_modes
        if creator_role_id is not UNSET:
            field_dict["creator_role_id"] = creator_role_id
        if domains_default_role_id is not UNSET:
            field_dict["domains_default_role_id"] = domains_default_role_id

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def _parse_enabled(data: object) -> Union[None, Unset, bool]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, bool], data)

        enabled = _parse_enabled(d.pop("enabled", UNSET))

        def _parse_max_allowed_memberships(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        max_allowed_memberships = _parse_max_allowed_memberships(d.pop("max_allowed_memberships", UNSET))

        def _parse_admin_delete_enabled(data: object) -> Union[None, Unset, bool]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, bool], data)

        admin_delete_enabled = _parse_admin_delete_enabled(d.pop("admin_delete_enabled", UNSET))

        def _parse_domains_enabled(data: object) -> Union[None, Unset, bool]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, bool], data)

        domains_enabled = _parse_domains_enabled(d.pop("domains_enabled", UNSET))

        domains_enrollment_modes = cast(List[str], d.pop("domains_enrollment_modes", UNSET))

        creator_role_id = d.pop("creator_role_id", UNSET)

        domains_default_role_id = d.pop("domains_default_role_id", UNSET)

        update_instance_organization_settings_body = cls(
            enabled=enabled,
            max_allowed_memberships=max_allowed_memberships,
            admin_delete_enabled=admin_delete_enabled,
            domains_enabled=domains_enabled,
            domains_enrollment_modes=domains_enrollment_modes,
            creator_role_id=creator_role_id,
            domains_default_role_id=domains_default_role_id,
        )

        return update_instance_organization_settings_body
