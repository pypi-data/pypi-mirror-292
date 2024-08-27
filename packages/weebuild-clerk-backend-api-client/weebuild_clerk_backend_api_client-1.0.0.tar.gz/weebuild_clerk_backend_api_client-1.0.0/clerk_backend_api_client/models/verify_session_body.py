from typing import Any, Dict, Type, TypeVar, Union

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="VerifySessionBody")


@_attrs_define
class VerifySessionBody:
    """
    Attributes:
        token (Union[Unset, str]): The JWT that is sent via the `__session` cookie from your frontend.
            Note: this JWT must be associated with the supplied session ID.
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

        verify_session_body = cls(
            token=token,
        )

        return verify_session_body
