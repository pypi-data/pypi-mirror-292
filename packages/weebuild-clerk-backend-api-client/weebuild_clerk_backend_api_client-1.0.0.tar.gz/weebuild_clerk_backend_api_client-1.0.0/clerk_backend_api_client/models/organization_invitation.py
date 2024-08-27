from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.organization_invitation_object import OrganizationInvitationObject
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.organization_invitation_private_metadata import OrganizationInvitationPrivateMetadata
    from ..models.organization_invitation_public_metadata import OrganizationInvitationPublicMetadata


T = TypeVar("T", bound="OrganizationInvitation")


@_attrs_define
class OrganizationInvitation:
    """An organization invitation

    Attributes:
        id (Union[Unset, str]):
        object_ (Union[Unset, OrganizationInvitationObject]): String representing the object's type. Objects of the same
            type share the same value.
        email_address (Union[Unset, str]):
        role (Union[Unset, str]):
        organization_id (Union[Unset, str]):
        status (Union[Unset, str]):
        public_metadata (Union[Unset, OrganizationInvitationPublicMetadata]):
        private_metadata (Union[Unset, OrganizationInvitationPrivateMetadata]):
        created_at (Union[Unset, int]): Unix timestamp of creation.
        updated_at (Union[Unset, int]): Unix timestamp of last update.
    """

    id: Union[Unset, str] = UNSET
    object_: Union[Unset, OrganizationInvitationObject] = UNSET
    email_address: Union[Unset, str] = UNSET
    role: Union[Unset, str] = UNSET
    organization_id: Union[Unset, str] = UNSET
    status: Union[Unset, str] = UNSET
    public_metadata: Union[Unset, "OrganizationInvitationPublicMetadata"] = UNSET
    private_metadata: Union[Unset, "OrganizationInvitationPrivateMetadata"] = UNSET
    created_at: Union[Unset, int] = UNSET
    updated_at: Union[Unset, int] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        id = self.id

        object_: Union[Unset, str] = UNSET
        if not isinstance(self.object_, Unset):
            object_ = self.object_.value

        email_address = self.email_address

        role = self.role

        organization_id = self.organization_id

        status = self.status

        public_metadata: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.public_metadata, Unset):
            public_metadata = self.public_metadata.to_dict()

        private_metadata: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.private_metadata, Unset):
            private_metadata = self.private_metadata.to_dict()

        created_at = self.created_at

        updated_at = self.updated_at

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if object_ is not UNSET:
            field_dict["object"] = object_
        if email_address is not UNSET:
            field_dict["email_address"] = email_address
        if role is not UNSET:
            field_dict["role"] = role
        if organization_id is not UNSET:
            field_dict["organization_id"] = organization_id
        if status is not UNSET:
            field_dict["status"] = status
        if public_metadata is not UNSET:
            field_dict["public_metadata"] = public_metadata
        if private_metadata is not UNSET:
            field_dict["private_metadata"] = private_metadata
        if created_at is not UNSET:
            field_dict["created_at"] = created_at
        if updated_at is not UNSET:
            field_dict["updated_at"] = updated_at

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.organization_invitation_private_metadata import OrganizationInvitationPrivateMetadata
        from ..models.organization_invitation_public_metadata import OrganizationInvitationPublicMetadata

        d = src_dict.copy()
        id = d.pop("id", UNSET)

        _object_ = d.pop("object", UNSET)
        object_: Union[Unset, OrganizationInvitationObject]
        if isinstance(_object_, Unset):
            object_ = UNSET
        else:
            object_ = OrganizationInvitationObject(_object_)

        email_address = d.pop("email_address", UNSET)

        role = d.pop("role", UNSET)

        organization_id = d.pop("organization_id", UNSET)

        status = d.pop("status", UNSET)

        _public_metadata = d.pop("public_metadata", UNSET)
        public_metadata: Union[Unset, OrganizationInvitationPublicMetadata]
        if isinstance(_public_metadata, Unset):
            public_metadata = UNSET
        else:
            public_metadata = OrganizationInvitationPublicMetadata.from_dict(_public_metadata)

        _private_metadata = d.pop("private_metadata", UNSET)
        private_metadata: Union[Unset, OrganizationInvitationPrivateMetadata]
        if isinstance(_private_metadata, Unset):
            private_metadata = UNSET
        else:
            private_metadata = OrganizationInvitationPrivateMetadata.from_dict(_private_metadata)

        created_at = d.pop("created_at", UNSET)

        updated_at = d.pop("updated_at", UNSET)

        organization_invitation = cls(
            id=id,
            object_=object_,
            email_address=email_address,
            role=role,
            organization_id=organization_id,
            status=status,
            public_metadata=public_metadata,
            private_metadata=private_metadata,
            created_at=created_at,
            updated_at=updated_at,
        )

        organization_invitation.additional_properties = d
        return organization_invitation

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
