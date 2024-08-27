from typing import TYPE_CHECKING, Any, Dict, Type, TypeVar, Union

from attrs import define as _attrs_define

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.merge_organization_metadata_body_private_metadata import MergeOrganizationMetadataBodyPrivateMetadata
    from ..models.merge_organization_metadata_body_public_metadata import MergeOrganizationMetadataBodyPublicMetadata


T = TypeVar("T", bound="MergeOrganizationMetadataBody")


@_attrs_define
class MergeOrganizationMetadataBody:
    """
    Attributes:
        public_metadata (Union[Unset, MergeOrganizationMetadataBodyPublicMetadata]): Metadata saved on the organization,
            that is visible to both your frontend and backend.
            The new object will be merged with the existing value.
        private_metadata (Union[Unset, MergeOrganizationMetadataBodyPrivateMetadata]): Metadata saved on the
            organization that is only visible to your backend.
            The new object will be merged with the existing value.
    """

    public_metadata: Union[Unset, "MergeOrganizationMetadataBodyPublicMetadata"] = UNSET
    private_metadata: Union[Unset, "MergeOrganizationMetadataBodyPrivateMetadata"] = UNSET

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
        from ..models.merge_organization_metadata_body_private_metadata import (
            MergeOrganizationMetadataBodyPrivateMetadata,
        )
        from ..models.merge_organization_metadata_body_public_metadata import (
            MergeOrganizationMetadataBodyPublicMetadata,
        )

        d = src_dict.copy()
        _public_metadata = d.pop("public_metadata", UNSET)
        public_metadata: Union[Unset, MergeOrganizationMetadataBodyPublicMetadata]
        if isinstance(_public_metadata, Unset):
            public_metadata = UNSET
        else:
            public_metadata = MergeOrganizationMetadataBodyPublicMetadata.from_dict(_public_metadata)

        _private_metadata = d.pop("private_metadata", UNSET)
        private_metadata: Union[Unset, MergeOrganizationMetadataBodyPrivateMetadata]
        if isinstance(_private_metadata, Unset):
            private_metadata = UNSET
        else:
            private_metadata = MergeOrganizationMetadataBodyPrivateMetadata.from_dict(_private_metadata)

        merge_organization_metadata_body = cls(
            public_metadata=public_metadata,
            private_metadata=private_metadata,
        )

        return merge_organization_metadata_body
