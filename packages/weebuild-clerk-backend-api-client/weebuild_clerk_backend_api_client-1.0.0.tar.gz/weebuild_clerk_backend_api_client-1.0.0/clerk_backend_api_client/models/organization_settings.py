from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define

from ..models.organization_settings_domains_enrollment_modes_item import OrganizationSettingsDomainsEnrollmentModesItem
from ..models.organization_settings_object import OrganizationSettingsObject
from ..types import UNSET, Unset

T = TypeVar("T", bound="OrganizationSettings")


@_attrs_define
class OrganizationSettings:
    """
    Attributes:
        object_ (OrganizationSettingsObject): String representing the object's type. Objects of the same type share the
            same value.
        enabled (bool):
        max_allowed_memberships (int):
        creator_role (str): The role key that a user will be assigned after creating an organization.
        admin_delete_enabled (bool): The default for whether an admin can delete an organization with the Frontend API.
        domains_enabled (bool):
        domains_enrollment_modes (List[OrganizationSettingsDomainsEnrollmentModesItem]):
        domains_default_role (str): The role key that it will be used in order to create an organization invitation or
            suggestion.
        max_allowed_roles (Union[Unset, int]):
        max_allowed_permissions (Union[Unset, int]):
    """

    object_: OrganizationSettingsObject
    enabled: bool
    max_allowed_memberships: int
    creator_role: str
    admin_delete_enabled: bool
    domains_enabled: bool
    domains_enrollment_modes: List[OrganizationSettingsDomainsEnrollmentModesItem]
    domains_default_role: str
    max_allowed_roles: Union[Unset, int] = UNSET
    max_allowed_permissions: Union[Unset, int] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        object_ = self.object_.value

        enabled = self.enabled

        max_allowed_memberships = self.max_allowed_memberships

        creator_role = self.creator_role

        admin_delete_enabled = self.admin_delete_enabled

        domains_enabled = self.domains_enabled

        domains_enrollment_modes = []
        for domains_enrollment_modes_item_data in self.domains_enrollment_modes:
            domains_enrollment_modes_item = domains_enrollment_modes_item_data.value
            domains_enrollment_modes.append(domains_enrollment_modes_item)

        domains_default_role = self.domains_default_role

        max_allowed_roles = self.max_allowed_roles

        max_allowed_permissions = self.max_allowed_permissions

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "object": object_,
                "enabled": enabled,
                "max_allowed_memberships": max_allowed_memberships,
                "creator_role": creator_role,
                "admin_delete_enabled": admin_delete_enabled,
                "domains_enabled": domains_enabled,
                "domains_enrollment_modes": domains_enrollment_modes,
                "domains_default_role": domains_default_role,
            }
        )
        if max_allowed_roles is not UNSET:
            field_dict["max_allowed_roles"] = max_allowed_roles
        if max_allowed_permissions is not UNSET:
            field_dict["max_allowed_permissions"] = max_allowed_permissions

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        object_ = OrganizationSettingsObject(d.pop("object"))

        enabled = d.pop("enabled")

        max_allowed_memberships = d.pop("max_allowed_memberships")

        creator_role = d.pop("creator_role")

        admin_delete_enabled = d.pop("admin_delete_enabled")

        domains_enabled = d.pop("domains_enabled")

        domains_enrollment_modes = []
        _domains_enrollment_modes = d.pop("domains_enrollment_modes")
        for domains_enrollment_modes_item_data in _domains_enrollment_modes:
            domains_enrollment_modes_item = OrganizationSettingsDomainsEnrollmentModesItem(
                domains_enrollment_modes_item_data
            )

            domains_enrollment_modes.append(domains_enrollment_modes_item)

        domains_default_role = d.pop("domains_default_role")

        max_allowed_roles = d.pop("max_allowed_roles", UNSET)

        max_allowed_permissions = d.pop("max_allowed_permissions", UNSET)

        organization_settings = cls(
            object_=object_,
            enabled=enabled,
            max_allowed_memberships=max_allowed_memberships,
            creator_role=creator_role,
            admin_delete_enabled=admin_delete_enabled,
            domains_enabled=domains_enabled,
            domains_enrollment_modes=domains_enrollment_modes,
            domains_default_role=domains_default_role,
            max_allowed_roles=max_allowed_roles,
            max_allowed_permissions=max_allowed_permissions,
        )

        return organization_settings
