from typing import Any, Dict, Type, TypeVar, Union

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="UpdateOAuthApplicationBody")


@_attrs_define
class UpdateOAuthApplicationBody:
    """
    Attributes:
        name (Union[Unset, str]): The new name of the OAuth application
        callback_url (Union[Unset, str]): The new callback URL of the OAuth application
        scopes (Union[Unset, str]): Define the allowed scopes for the new OAuth applications that dictate the user
            payload of the OAuth user info endpoint. Available scopes are `profile`, `email`, `public_metadata`,
            `private_metadata`. Provide the requested scopes as a string, separated by spaces. Default: 'profile email'.
            Example: profile email public_metadata private_metadata.
    """

    name: Union[Unset, str] = UNSET
    callback_url: Union[Unset, str] = UNSET
    scopes: Union[Unset, str] = "profile email"

    def to_dict(self) -> Dict[str, Any]:
        name = self.name

        callback_url = self.callback_url

        scopes = self.scopes

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if name is not UNSET:
            field_dict["name"] = name
        if callback_url is not UNSET:
            field_dict["callback_url"] = callback_url
        if scopes is not UNSET:
            field_dict["scopes"] = scopes

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        name = d.pop("name", UNSET)

        callback_url = d.pop("callback_url", UNSET)

        scopes = d.pop("scopes", UNSET)

        update_o_auth_application_body = cls(
            name=name,
            callback_url=callback_url,
            scopes=scopes,
        )

        return update_o_auth_application_body
