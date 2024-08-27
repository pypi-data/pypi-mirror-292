from typing import Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="CreateInvitationBodyPublicMetadata")


@_attrs_define
class CreateInvitationBodyPublicMetadata:
    """Metadata that will be attached to the newly created invitation.
    The value of this property should be a well-formed JSON object.
    Once the user accepts the invitation and signs up, these metadata will end up in the user's public metadata.

    """

    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        create_invitation_body_public_metadata = cls()

        create_invitation_body_public_metadata.additional_properties = d
        return create_invitation_body_public_metadata

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
