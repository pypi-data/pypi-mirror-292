from typing import TYPE_CHECKING, Any, Dict, Type, TypeVar, Union

from attrs import define as _attrs_define

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.update_organization_membership_metadata_body_private_metadata import (
        UpdateOrganizationMembershipMetadataBodyPrivateMetadata,
    )
    from ..models.update_organization_membership_metadata_body_public_metadata import (
        UpdateOrganizationMembershipMetadataBodyPublicMetadata,
    )


T = TypeVar("T", bound="UpdateOrganizationMembershipMetadataBody")


@_attrs_define
class UpdateOrganizationMembershipMetadataBody:
    """
    Attributes:
        public_metadata (Union[Unset, UpdateOrganizationMembershipMetadataBodyPublicMetadata]): Metadata saved on the
            organization membership, that is visible to both your frontend and backend.
            The new object will be merged with the existing value.
        private_metadata (Union[Unset, UpdateOrganizationMembershipMetadataBodyPrivateMetadata]): Metadata saved on the
            organization membership that is only visible to your backend.
            The new object will be merged with the existing value.
    """

    public_metadata: Union[Unset, "UpdateOrganizationMembershipMetadataBodyPublicMetadata"] = UNSET
    private_metadata: Union[Unset, "UpdateOrganizationMembershipMetadataBodyPrivateMetadata"] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        public_metadata: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.public_metadata, Unset):
            public_metadata = self.public_metadata.to_dict()

        private_metadata: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.private_metadata, Unset):
            private_metadata = self.private_metadata.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if public_metadata is not UNSET:
            field_dict["public_metadata"] = public_metadata
        if private_metadata is not UNSET:
            field_dict["private_metadata"] = private_metadata

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.update_organization_membership_metadata_body_private_metadata import (
            UpdateOrganizationMembershipMetadataBodyPrivateMetadata,
        )
        from ..models.update_organization_membership_metadata_body_public_metadata import (
            UpdateOrganizationMembershipMetadataBodyPublicMetadata,
        )

        d = src_dict.copy()
        _public_metadata = d.pop("public_metadata", UNSET)
        public_metadata: Union[Unset, UpdateOrganizationMembershipMetadataBodyPublicMetadata]
        if isinstance(_public_metadata, Unset):
            public_metadata = UNSET
        else:
            public_metadata = UpdateOrganizationMembershipMetadataBodyPublicMetadata.from_dict(_public_metadata)

        _private_metadata = d.pop("private_metadata", UNSET)
        private_metadata: Union[Unset, UpdateOrganizationMembershipMetadataBodyPrivateMetadata]
        if isinstance(_private_metadata, Unset):
            private_metadata = UNSET
        else:
            private_metadata = UpdateOrganizationMembershipMetadataBodyPrivateMetadata.from_dict(_private_metadata)

        update_organization_membership_metadata_body = cls(
            public_metadata=public_metadata,
            private_metadata=private_metadata,
        )

        return update_organization_membership_metadata_body
