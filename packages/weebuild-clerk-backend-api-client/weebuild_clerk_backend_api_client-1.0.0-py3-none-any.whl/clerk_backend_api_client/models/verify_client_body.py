from typing import Any, Dict, Type, TypeVar, Union

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="VerifyClientBody")


@_attrs_define
class VerifyClientBody:
    """
    Attributes:
        token (Union[Unset, str]): A JWT that represents the active client.
    """

    token: Union[Unset, str] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        token = self.token

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if token is not UNSET:
            field_dict["token"] = token

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        token = d.pop("token", UNSET)

        verify_client_body = cls(
            token=token,
        )

        return verify_client_body
