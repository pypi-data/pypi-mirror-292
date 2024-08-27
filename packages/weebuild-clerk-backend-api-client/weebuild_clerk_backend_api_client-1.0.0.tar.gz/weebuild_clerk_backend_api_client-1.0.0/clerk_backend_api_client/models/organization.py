from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.organization_object import OrganizationObject
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.organization_private_metadata import OrganizationPrivateMetadata
    from ..models.organization_public_metadata import OrganizationPublicMetadata


T = TypeVar("T", bound="Organization")


@_attrs_define
class Organization:
    """
    Attributes:
        object_ (OrganizationObject):
        id (str):
        name (str):
        slug (str):
        max_allowed_memberships (int):
        public_metadata (OrganizationPublicMetadata):
        private_metadata (OrganizationPrivateMetadata):
        created_at (int): Unix timestamp of creation.
        updated_at (int): Unix timestamp of last update.
        members_count (Union[None, Unset, int]):
        admin_delete_enabled (Union[Unset, bool]):
        created_by (Union[Unset, str]):
    """

    object_: OrganizationObject
    id: str
    name: str
    slug: str
    max_allowed_memberships: int
    public_metadata: "OrganizationPublicMetadata"
    private_metadata: "OrganizationPrivateMetadata"
    created_at: int
    updated_at: int
    members_count: Union[None, Unset, int] = UNSET
    admin_delete_enabled: Union[Unset, bool] = UNSET
    created_by: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        object_ = self.object_.value

        id = self.id

        name = self.name

        slug = self.slug

        max_allowed_memberships = self.max_allowed_memberships

        public_metadata = self.public_metadata.to_dict()

        private_metadata = self.private_metadata.to_dict()

        created_at = self.created_at

        updated_at = self.updated_at

        members_count: Union[None, Unset, int]
        if isinstance(self.members_count, Unset):
            members_count = UNSET
        else:
            members_count = self.members_count

        admin_delete_enabled = self.admin_delete_enabled

        created_by = self.created_by

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "object": object_,
                "id": id,
                "name": name,
                "slug": slug,
                "max_allowed_memberships": max_allowed_memberships,
                "public_metadata": public_metadata,
                "private_metadata": private_metadata,
                "created_at": created_at,
                "updated_at": updated_at,
            }
        )
        if members_count is not UNSET:
            field_dict["members_count"] = members_count
        if admin_delete_enabled is not UNSET:
            field_dict["admin_delete_enabled"] = admin_delete_enabled
        if created_by is not UNSET:
            field_dict["created_by"] = created_by

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.organization_private_metadata import OrganizationPrivateMetadata
        from ..models.organization_public_metadata import OrganizationPublicMetadata

        d = src_dict.copy()
        object_ = OrganizationObject(d.pop("object"))

        id = d.pop("id")

        name = d.pop("name")

        slug = d.pop("slug")

        max_allowed_memberships = d.pop("max_allowed_memberships")

        public_metadata = OrganizationPublicMetadata.from_dict(d.pop("public_metadata"))

        private_metadata = OrganizationPrivateMetadata.from_dict(d.pop("private_metadata"))

        created_at = d.pop("created_at")

        updated_at = d.pop("updated_at")

        def _parse_members_count(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        members_count = _parse_members_count(d.pop("members_count", UNSET))

        admin_delete_enabled = d.pop("admin_delete_enabled", UNSET)

        created_by = d.pop("created_by", UNSET)

        organization = cls(
            object_=object_,
            id=id,
            name=name,
            slug=slug,
            max_allowed_memberships=max_allowed_memberships,
            public_metadata=public_metadata,
            private_metadata=private_metadata,
            created_at=created_at,
            updated_at=updated_at,
            members_count=members_count,
            admin_delete_enabled=admin_delete_enabled,
            created_by=created_by,
        )

        organization.additional_properties = d
        return organization

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
