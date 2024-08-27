from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.organization_membership_object import OrganizationMembershipObject
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.organization import Organization
    from ..models.organization_membership_private_metadata import OrganizationMembershipPrivateMetadata
    from ..models.organization_membership_public_metadata import OrganizationMembershipPublicMetadata
    from ..models.organization_membership_public_user_data import OrganizationMembershipPublicUserData


T = TypeVar("T", bound="OrganizationMembership")


@_attrs_define
class OrganizationMembership:
    """Hello world

    Attributes:
        id (Union[Unset, str]):
        object_ (Union[Unset, OrganizationMembershipObject]): String representing the object's type. Objects of the same
            type share the same value.
        role (Union[Unset, str]):
        permissions (Union[Unset, List[str]]):
        public_metadata (Union[Unset, OrganizationMembershipPublicMetadata]): Metadata saved on the organization
            membership, accessible from both Frontend and Backend APIs
        private_metadata (Union[Unset, OrganizationMembershipPrivateMetadata]): Metadata saved on the organization
            membership, accessible only from the Backend API
        organization (Union[Unset, Organization]):
        public_user_data (Union[Unset, OrganizationMembershipPublicUserData]):
        created_at (Union[Unset, int]): Unix timestamp of creation.
        updated_at (Union[Unset, int]): Unix timestamp of last update.
    """

    id: Union[Unset, str] = UNSET
    object_: Union[Unset, OrganizationMembershipObject] = UNSET
    role: Union[Unset, str] = UNSET
    permissions: Union[Unset, List[str]] = UNSET
    public_metadata: Union[Unset, "OrganizationMembershipPublicMetadata"] = UNSET
    private_metadata: Union[Unset, "OrganizationMembershipPrivateMetadata"] = UNSET
    organization: Union[Unset, "Organization"] = UNSET
    public_user_data: Union[Unset, "OrganizationMembershipPublicUserData"] = UNSET
    created_at: Union[Unset, int] = UNSET
    updated_at: Union[Unset, int] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        id = self.id

        object_: Union[Unset, str] = UNSET
        if not isinstance(self.object_, Unset):
            object_ = self.object_.value

        role = self.role

        permissions: Union[Unset, List[str]] = UNSET
        if not isinstance(self.permissions, Unset):
            permissions = self.permissions

        public_metadata: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.public_metadata, Unset):
            public_metadata = self.public_metadata.to_dict()

        private_metadata: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.private_metadata, Unset):
            private_metadata = self.private_metadata.to_dict()

        organization: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.organization, Unset):
            organization = self.organization.to_dict()

        public_user_data: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.public_user_data, Unset):
            public_user_data = self.public_user_data.to_dict()

        created_at = self.created_at

        updated_at = self.updated_at

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if object_ is not UNSET:
            field_dict["object"] = object_
        if role is not UNSET:
            field_dict["role"] = role
        if permissions is not UNSET:
            field_dict["permissions"] = permissions
        if public_metadata is not UNSET:
            field_dict["public_metadata"] = public_metadata
        if private_metadata is not UNSET:
            field_dict["private_metadata"] = private_metadata
        if organization is not UNSET:
            field_dict["organization"] = organization
        if public_user_data is not UNSET:
            field_dict["public_user_data"] = public_user_data
        if created_at is not UNSET:
            field_dict["created_at"] = created_at
        if updated_at is not UNSET:
            field_dict["updated_at"] = updated_at

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.organization import Organization
        from ..models.organization_membership_private_metadata import OrganizationMembershipPrivateMetadata
        from ..models.organization_membership_public_metadata import OrganizationMembershipPublicMetadata
        from ..models.organization_membership_public_user_data import OrganizationMembershipPublicUserData

        d = src_dict.copy()
        id = d.pop("id", UNSET)

        _object_ = d.pop("object", UNSET)
        object_: Union[Unset, OrganizationMembershipObject]
        if isinstance(_object_, Unset):
            object_ = UNSET
        else:
            object_ = OrganizationMembershipObject(_object_)

        role = d.pop("role", UNSET)

        permissions = cast(List[str], d.pop("permissions", UNSET))

        _public_metadata = d.pop("public_metadata", UNSET)
        public_metadata: Union[Unset, OrganizationMembershipPublicMetadata]
        if isinstance(_public_metadata, Unset):
            public_metadata = UNSET
        else:
            public_metadata = OrganizationMembershipPublicMetadata.from_dict(_public_metadata)

        _private_metadata = d.pop("private_metadata", UNSET)
        private_metadata: Union[Unset, OrganizationMembershipPrivateMetadata]
        if isinstance(_private_metadata, Unset):
            private_metadata = UNSET
        else:
            private_metadata = OrganizationMembershipPrivateMetadata.from_dict(_private_metadata)

        _organization = d.pop("organization", UNSET)
        organization: Union[Unset, Organization]
        if isinstance(_organization, Unset):
            organization = UNSET
        else:
            organization = Organization.from_dict(_organization)

        _public_user_data = d.pop("public_user_data", UNSET)
        public_user_data: Union[Unset, OrganizationMembershipPublicUserData]
        if isinstance(_public_user_data, Unset):
            public_user_data = UNSET
        else:
            public_user_data = OrganizationMembershipPublicUserData.from_dict(_public_user_data)

        created_at = d.pop("created_at", UNSET)

        updated_at = d.pop("updated_at", UNSET)

        organization_membership = cls(
            id=id,
            object_=object_,
            role=role,
            permissions=permissions,
            public_metadata=public_metadata,
            private_metadata=private_metadata,
            organization=organization,
            public_user_data=public_user_data,
            created_at=created_at,
            updated_at=updated_at,
        )

        organization_membership.additional_properties = d
        return organization_membership

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
