from typing import TYPE_CHECKING, Any, Dict, Type, TypeVar, Union, cast

from attrs import define as _attrs_define

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.update_organization_body_private_metadata import UpdateOrganizationBodyPrivateMetadata
    from ..models.update_organization_body_public_metadata import UpdateOrganizationBodyPublicMetadata


T = TypeVar("T", bound="UpdateOrganizationBody")


@_attrs_define
class UpdateOrganizationBody:
    """
    Attributes:
        public_metadata (Union[Unset, UpdateOrganizationBodyPublicMetadata]): Metadata saved on the organization, that
            is visible to both your frontend and backend.
        private_metadata (Union[Unset, UpdateOrganizationBodyPrivateMetadata]): Metadata saved on the organization that
            is only visible to your backend.
        name (Union[None, Unset, str]): The new name of the organization
        slug (Union[None, Unset, str]): The new slug of the organization, which needs to be unique in the instance
        max_allowed_memberships (Union[None, Unset, int]): The maximum number of memberships allowed for this
            organization
        admin_delete_enabled (Union[None, Unset, bool]): If true, an admin can delete this organization with the
            Frontend API.
        created_at (Union[Unset, str]): A custom date/time denoting _when_ the organization was created, specified in
            RFC3339 format (e.g. `2012-10-20T07:15:20.902Z`).
    """

    public_metadata: Union[Unset, "UpdateOrganizationBodyPublicMetadata"] = UNSET
    private_metadata: Union[Unset, "UpdateOrganizationBodyPrivateMetadata"] = UNSET
    name: Union[None, Unset, str] = UNSET
    slug: Union[None, Unset, str] = UNSET
    max_allowed_memberships: Union[None, Unset, int] = UNSET
    admin_delete_enabled: Union[None, Unset, bool] = UNSET
    created_at: Union[Unset, str] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        public_metadata: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.public_metadata, Unset):
            public_metadata = self.public_metadata.to_dict()

        private_metadata: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.private_metadata, Unset):
            private_metadata = self.private_metadata.to_dict()

        name: Union[None, Unset, str]
        if isinstance(self.name, Unset):
            name = UNSET
        else:
            name = self.name

        slug: Union[None, Unset, str]
        if isinstance(self.slug, Unset):
            slug = UNSET
        else:
            slug = self.slug

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

        created_at = self.created_at

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if public_metadata is not UNSET:
            field_dict["public_metadata"] = public_metadata
        if private_metadata is not UNSET:
            field_dict["private_metadata"] = private_metadata
        if name is not UNSET:
            field_dict["name"] = name
        if slug is not UNSET:
            field_dict["slug"] = slug
        if max_allowed_memberships is not UNSET:
            field_dict["max_allowed_memberships"] = max_allowed_memberships
        if admin_delete_enabled is not UNSET:
            field_dict["admin_delete_enabled"] = admin_delete_enabled
        if created_at is not UNSET:
            field_dict["created_at"] = created_at

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.update_organization_body_private_metadata import UpdateOrganizationBodyPrivateMetadata
        from ..models.update_organization_body_public_metadata import UpdateOrganizationBodyPublicMetadata

        d = src_dict.copy()
        _public_metadata = d.pop("public_metadata", UNSET)
        public_metadata: Union[Unset, UpdateOrganizationBodyPublicMetadata]
        if isinstance(_public_metadata, Unset):
            public_metadata = UNSET
        else:
            public_metadata = UpdateOrganizationBodyPublicMetadata.from_dict(_public_metadata)

        _private_metadata = d.pop("private_metadata", UNSET)
        private_metadata: Union[Unset, UpdateOrganizationBodyPrivateMetadata]
        if isinstance(_private_metadata, Unset):
            private_metadata = UNSET
        else:
            private_metadata = UpdateOrganizationBodyPrivateMetadata.from_dict(_private_metadata)

        def _parse_name(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        name = _parse_name(d.pop("name", UNSET))

        def _parse_slug(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        slug = _parse_slug(d.pop("slug", UNSET))

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

        created_at = d.pop("created_at", UNSET)

        update_organization_body = cls(
            public_metadata=public_metadata,
            private_metadata=private_metadata,
            name=name,
            slug=slug,
            max_allowed_memberships=max_allowed_memberships,
            admin_delete_enabled=admin_delete_enabled,
            created_at=created_at,
        )

        return update_organization_body
