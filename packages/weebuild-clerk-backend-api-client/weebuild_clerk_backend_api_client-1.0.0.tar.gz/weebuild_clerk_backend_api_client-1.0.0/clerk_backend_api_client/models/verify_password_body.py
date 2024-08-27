from typing import Any, Dict, Type, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="VerifyPasswordBody")


@_attrs_define
class VerifyPasswordBody:
    """
    Attributes:
        password (str): The user password to verify
    """

    password: str

    def to_dict(self) -> Dict[str, Any]:
        password = self.password

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "password": password,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        password = d.pop("password")

        verify_password_body = cls(
            password=password,
        )

        return verify_password_body
