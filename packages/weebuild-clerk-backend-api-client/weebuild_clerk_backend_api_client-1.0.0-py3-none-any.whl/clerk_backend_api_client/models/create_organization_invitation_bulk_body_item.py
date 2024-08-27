from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.create_organization_invitation_bulk_body_item_private_metadata import (
        CreateOrganizationInvitationBulkBodyItemPrivateMetadata,
    )
    from ..models.create_organization_invitation_bulk_body_item_public_metadata import (
        CreateOrganizationInvitationBulkBodyItemPublicMetadata,
    )


T = TypeVar("T", bound="CreateOrganizationInvitationBulkBodyItem")


@_attrs_define
class CreateOrganizationInvitationBulkBodyItem:
    """
    Attributes:
        email_address (str): The email address of the new member that is going to be invited to the organization
        inviter_user_id (str): The ID of the user that invites the new member to the organization.
            Must be an administrator in the organization.
        role (str): The role of the new member in the organization.
        public_metadata (Union[Unset, CreateOrganizationInvitationBulkBodyItemPublicMetadata]): Metadata saved on the
            organization invitation, read-only from the Frontend API and fully accessible (read/write) from the Backend API.
        private_metadata (Union[Unset, CreateOrganizationInvitationBulkBodyItemPrivateMetadata]): Metadata saved on the
            organization invitation, fully accessible (read/write) from the Backend API but not visible from the Frontend
            API.
        redirect_url (Union[Unset, str]): Optional URL that the invitee will be redirected to once they accept the
            invitation by clicking the join link in the invitation email.
    """

    email_address: str
    inviter_user_id: str
    role: str
    public_metadata: Union[Unset, "CreateOrganizationInvitationBulkBodyItemPublicMetadata"] = UNSET
    private_metadata: Union[Unset, "CreateOrganizationInvitationBulkBodyItemPrivateMetadata"] = UNSET
    redirect_url: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        email_address = self.email_address

        inviter_user_id = self.inviter_user_id

        role = self.role

        public_metadata: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.public_metadata, Unset):
            public_metadata = self.public_metadata.to_dict()

        private_metadata: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.private_metadata, Unset):
            private_metadata = self.private_metadata.to_dict()

        redirect_url = self.redirect_url

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "email_address": email_address,
                "inviter_user_id": inviter_user_id,
                "role": role,
            }
        )
        if public_metadata is not UNSET:
            field_dict["public_metadata"] = public_metadata
        if private_metadata is not UNSET:
            field_dict["private_metadata"] = private_metadata
        if redirect_url is not UNSET:
            field_dict["redirect_url"] = redirect_url

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.create_organization_invitation_bulk_body_item_private_metadata import (
            CreateOrganizationInvitationBulkBodyItemPrivateMetadata,
        )
        from ..models.create_organization_invitation_bulk_body_item_public_metadata import (
            CreateOrganizationInvitationBulkBodyItemPublicMetadata,
        )

        d = src_dict.copy()
        email_address = d.pop("email_address")

        inviter_user_id = d.pop("inviter_user_id")

        role = d.pop("role")

        _public_metadata = d.pop("public_metadata", UNSET)
        public_metadata: Union[Unset, CreateOrganizationInvitationBulkBodyItemPublicMetadata]
        if isinstance(_public_metadata, Unset):
            public_metadata = UNSET
        else:
            public_metadata = CreateOrganizationInvitationBulkBodyItemPublicMetadata.from_dict(_public_metadata)

        _private_metadata = d.pop("private_metadata", UNSET)
        private_metadata: Union[Unset, CreateOrganizationInvitationBulkBodyItemPrivateMetadata]
        if isinstance(_private_metadata, Unset):
            private_metadata = UNSET
        else:
            private_metadata = CreateOrganizationInvitationBulkBodyItemPrivateMetadata.from_dict(_private_metadata)

        redirect_url = d.pop("redirect_url", UNSET)

        create_organization_invitation_bulk_body_item = cls(
            email_address=email_address,
            inviter_user_id=inviter_user_id,
            role=role,
            public_metadata=public_metadata,
            private_metadata=private_metadata,
            redirect_url=redirect_url,
        )

        create_organization_invitation_bulk_body_item.additional_properties = d
        return create_organization_invitation_bulk_body_item

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
