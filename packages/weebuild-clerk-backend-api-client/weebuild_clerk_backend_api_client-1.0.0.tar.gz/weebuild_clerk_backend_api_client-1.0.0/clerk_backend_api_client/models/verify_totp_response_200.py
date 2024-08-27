from typing import Any, Dict, Type, TypeVar, Union

from attrs import define as _attrs_define

from ..models.verify_totp_response_200_code_type import VerifyTOTPResponse200CodeType
from ..types import UNSET, Unset

T = TypeVar("T", bound="VerifyTOTPResponse200")


@_attrs_define
class VerifyTOTPResponse200:
    """
    Attributes:
        verified (Union[Unset, bool]):
        code_type (Union[Unset, VerifyTOTPResponse200CodeType]):
    """

    verified: Union[Unset, bool] = UNSET
    code_type: Union[Unset, VerifyTOTPResponse200CodeType] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        verified = self.verified

        code_type: Union[Unset, str] = UNSET
        if not isinstance(self.code_type, Unset):
            code_type = self.code_type.value

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if verified is not UNSET:
            field_dict["verified"] = verified
        if code_type is not UNSET:
            field_dict["code_type"] = code_type

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        verified = d.pop("verified", UNSET)

        _code_type = d.pop("code_type", UNSET)
        code_type: Union[Unset, VerifyTOTPResponse200CodeType]
        if isinstance(_code_type, Unset):
            code_type = UNSET
        else:
            code_type = VerifyTOTPResponse200CodeType(_code_type)

        verify_totp_response_200 = cls(
            verified=verified,
            code_type=code_type,
        )

        return verify_totp_response_200
