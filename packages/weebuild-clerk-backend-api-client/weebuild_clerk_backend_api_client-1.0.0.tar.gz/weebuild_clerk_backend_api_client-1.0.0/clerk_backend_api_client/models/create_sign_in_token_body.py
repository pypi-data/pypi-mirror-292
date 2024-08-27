from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="CreateSignInTokenBody")


@_attrs_define
class CreateSignInTokenBody:
    """
    Attributes:
        user_id (Union[Unset, str]): The ID of the user that can use the newly created sign in token
        expires_in_seconds (Union[Unset, int]): Optional parameter to specify the life duration of the sign in token in
            seconds.
            By default, the duration is 30 days. Default: 2592000.
    """

    user_id: Union[Unset, str] = UNSET
    expires_in_seconds: Union[Unset, int] = 2592000
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        user_id = self.user_id

        expires_in_seconds = self.expires_in_seconds

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if user_id is not UNSET:
            field_dict["user_id"] = user_id
        if expires_in_seconds is not UNSET:
            field_dict["expires_in_seconds"] = expires_in_seconds

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        user_id = d.pop("user_id", UNSET)

        expires_in_seconds = d.pop("expires_in_seconds", UNSET)

        create_sign_in_token_body = cls(
            user_id=user_id,
            expires_in_seconds=expires_in_seconds,
        )

        create_sign_in_token_body.additional_properties = d
        return create_sign_in_token_body

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
