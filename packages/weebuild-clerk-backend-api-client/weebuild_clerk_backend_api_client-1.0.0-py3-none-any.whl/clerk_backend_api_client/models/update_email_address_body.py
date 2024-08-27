from typing import Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="UpdateEmailAddressBody")


@_attrs_define
class UpdateEmailAddressBody:
    """
    Attributes:
        verified (Union[None, Unset, bool]): The email address will be marked as verified.
        primary (Union[None, Unset, bool]): Set this email address as the primary email address for the user.
    """

    verified: Union[None, Unset, bool] = UNSET
    primary: Union[None, Unset, bool] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
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
        if verified is not UNSET:
            field_dict["verified"] = verified
        if primary is not UNSET:
            field_dict["primary"] = primary

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

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

        update_email_address_body = cls(
            verified=verified,
            primary=primary,
        )

        update_email_address_body.additional_properties = d
        return update_email_address_body

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
