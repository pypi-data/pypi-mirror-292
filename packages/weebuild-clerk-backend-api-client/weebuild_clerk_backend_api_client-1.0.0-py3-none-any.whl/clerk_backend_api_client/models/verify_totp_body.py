from typing import Any, Dict, Type, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="VerifyTOTPBody")


@_attrs_define
class VerifyTOTPBody:
    """
    Attributes:
        code (str): The TOTP or backup code to verify
    """

    code: str

    def to_dict(self) -> Dict[str, Any]:
        code = self.code

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "code": code,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        code = d.pop("code")

        verify_totp_body = cls(
            code=code,
        )

        return verify_totp_body
