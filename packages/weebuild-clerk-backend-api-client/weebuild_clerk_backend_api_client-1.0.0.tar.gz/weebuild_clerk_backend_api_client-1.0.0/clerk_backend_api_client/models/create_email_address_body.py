from typing import Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="CreateEmailAddressBody")


@_attrs_define
class CreateEmailAddressBody:
    """
    Attributes:
        user_id (Union[Unset, str]): The ID representing the user
        email_address (Union[Unset, str]): The new email address. Must adhere to the RFC 5322 specification for email
            address format.
        verified (Union[None, Unset, bool]): When created, the email address will be marked as verified.
        primary (Union[None, Unset, bool]): Create this email address as the primary email address for the user.
            Default: false, unless it is the first email address.
    """

    user_id: Union[Unset, str] = UNSET
    email_address: Union[Unset, str] = UNSET
    verified: Union[None, Unset, bool] = UNSET
    primary: Union[None, Unset, bool] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        user_id = self.user_id

        email_address = self.email_address

        verified: Union[None, Unset, bool]
        if isinstance(self.verified, Unset):
            verified = UNSET
        else:
            verified = self.verified

        primary: Union[None, Unset, bool]
        if isinstance(self.primary, Unset):
            primary = UNSET
        else:
            primary = self.primary

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if user_id is not UNSET:
            field_dict["user_id"] = user_id
        if email_address is not UNSET:
            field_dict["email_address"] = email_address
        if verified is not UNSET:
            field_dict["verified"] = verified
        if primary is not UNSET:
            field_dict["primary"] = primary

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        user_id = d.pop("user_id", UNSET)

        email_address = d.pop("email_address", UNSET)

        def _parse_verified(data: object) -> Union[None, Unset, bool]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, bool], data)

        verified = _parse_verified(d.pop("verified", UNSET))

        def _parse_primary(data: object) -> Union[None, Unset, bool]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, bool], data)

        primary = _parse_primary(d.pop("primary", UNSET))

        create_email_address_body = cls(
            user_id=user_id,
            email_address=email_address,
            verified=verified,
            primary=primary,
        )

        create_email_address_body.additional_properties = d
        return create_email_address_body

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
