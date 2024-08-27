from typing import TYPE_CHECKING, Any, Dict, Type, TypeVar, Union

from attrs import define as _attrs_define

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.update_user_metadata_body_private_metadata import UpdateUserMetadataBodyPrivateMetadata
    from ..models.update_user_metadata_body_public_metadata import UpdateUserMetadataBodyPublicMetadata
    from ..models.update_user_metadata_body_unsafe_metadata import UpdateUserMetadataBodyUnsafeMetadata


T = TypeVar("T", bound="UpdateUserMetadataBody")


@_attrs_define
class UpdateUserMetadataBody:
    """
    Attributes:
        public_metadata (Union[Unset, UpdateUserMetadataBodyPublicMetadata]): Metadata saved on the user, that is
            visible to both your frontend and backend.
            The new object will be merged with the existing value.
        private_metadata (Union[Unset, UpdateUserMetadataBodyPrivateMetadata]): Metadata saved on the user that is only
            visible to your backend.
            The new object will be merged with the existing value.
        unsafe_metadata (Union[Unset, UpdateUserMetadataBodyUnsafeMetadata]): Metadata saved on the user, that can be
            updated from both the Frontend and Backend APIs.
            The new object will be merged with the existing value.

            Note: Since this data can be modified from the frontend, it is not guaranteed to be safe.
    """

    public_metadata: Union[Unset, "UpdateUserMetadataBodyPublicMetadata"] = UNSET
    private_metadata: Union[Unset, "UpdateUserMetadataBodyPrivateMetadata"] = UNSET
    unsafe_metadata: Union[Unset, "UpdateUserMetadataBodyUnsafeMetadata"] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        public_metadata: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.public_metadata, Unset):
            public_metadata = self.public_metadata.to_dict()

        private_metadata: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.private_metadata, Unset):
            private_metadata = self.private_metadata.to_dict()

        unsafe_metadata: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.unsafe_metadata, Unset):
            unsafe_metadata = self.unsafe_metadata.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if public_metadata is not UNSET:
            field_dict["public_metadata"] = public_metadata
        if private_metadata is not UNSET:
            field_dict["private_metadata"] = private_metadata
        if unsafe_metadata is not UNSET:
            field_dict["unsafe_metadata"] = unsafe_metadata

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.update_user_metadata_body_private_metadata import UpdateUserMetadataBodyPrivateMetadata
        from ..models.update_user_metadata_body_public_metadata import UpdateUserMetadataBodyPublicMetadata
        from ..models.update_user_metadata_body_unsafe_metadata import UpdateUserMetadataBodyUnsafeMetadata

        d = src_dict.copy()
        _public_metadata = d.pop("public_metadata", UNSET)
        public_metadata: Union[Unset, UpdateUserMetadataBodyPublicMetadata]
        if isinstance(_public_metadata, Unset):
            public_metadata = UNSET
        else:
            public_metadata = UpdateUserMetadataBodyPublicMetadata.from_dict(_public_metadata)

        _private_metadata = d.pop("private_metadata", UNSET)
        private_metadata: Union[Unset, UpdateUserMetadataBodyPrivateMetadata]
        if isinstance(_private_metadata, Unset):
            private_metadata = UNSET
        else:
            private_metadata = UpdateUserMetadataBodyPrivateMetadata.from_dict(_private_metadata)

        _unsafe_metadata = d.pop("unsafe_metadata", UNSET)
        unsafe_metadata: Union[Unset, UpdateUserMetadataBodyUnsafeMetadata]
        if isinstance(_unsafe_metadata, Unset):
            unsafe_metadata = UNSET
        else:
            unsafe_metadata = UpdateUserMetadataBodyUnsafeMetadata.from_dict(_unsafe_metadata)

        update_user_metadata_body = cls(
            public_metadata=public_metadata,
            private_metadata=private_metadata,
            unsafe_metadata=unsafe_metadata,
        )

        return update_user_metadata_body
