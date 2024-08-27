from typing import Any, Dict, Type, TypeVar, Union

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="VerifyPasswordResponse200")


@_attrs_define
class VerifyPasswordResponse200:
    """
    Attributes:
        verified (Union[Unset, bool]):
    """

    verified: Union[Unset, bool] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        verified = self.verified

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if verified is not UNSET:
            field_dict["verified"] = verified

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        verified = d.pop("verified", UNSET)

        verify_password_response_200 = cls(
            verified=verified,
        )

        return verify_password_response_200
