from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.create_session_token_from_template_response_200_object import (
    CreateSessionTokenFromTemplateResponse200Object,
)
from ..types import UNSET, Unset

T = TypeVar("T", bound="CreateSessionTokenFromTemplateResponse200")


@_attrs_define
class CreateSessionTokenFromTemplateResponse200:
    """
    Attributes:
        object_ (Union[Unset, CreateSessionTokenFromTemplateResponse200Object]):
        jwt (Union[Unset, str]):
    """

    object_: Union[Unset, CreateSessionTokenFromTemplateResponse200Object] = UNSET
    jwt: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        object_: Union[Unset, str] = UNSET
        if not isinstance(self.object_, Unset):
            object_ = self.object_.value

        jwt = self.jwt

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if object_ is not UNSET:
            field_dict["object"] = object_
        if jwt is not UNSET:
            field_dict["jwt"] = jwt

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        _object_ = d.pop("object", UNSET)
        object_: Union[Unset, CreateSessionTokenFromTemplateResponse200Object]
        if isinstance(_object_, Unset):
            object_ = UNSET
        else:
            object_ = CreateSessionTokenFromTemplateResponse200Object(_object_)

        jwt = d.pop("jwt", UNSET)

        create_session_token_from_template_response_200 = cls(
            object_=object_,
            jwt=jwt,
        )

        create_session_token_from_template_response_200.additional_properties = d
        return create_session_token_from_template_response_200

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
