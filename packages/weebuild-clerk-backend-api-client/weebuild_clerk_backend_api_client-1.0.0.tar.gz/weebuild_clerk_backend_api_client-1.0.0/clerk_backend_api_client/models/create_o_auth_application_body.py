from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="CreateOAuthApplicationBody")


@_attrs_define
class CreateOAuthApplicationBody:
    """
    Attributes:
        name (str): The name of the new OAuth application
        callback_url (str): The callback URL of the new OAuth application
        scopes (Union[Unset, str]): Define the allowed scopes for the new OAuth applications that dictate the user
            payload of the OAuth user info endpoint. Available scopes are `profile`, `email`, `public_metadata`,
            `private_metadata`. Provide the requested scopes as a string, separated by spaces. Default: 'profile email'.
            Example: profile email public_metadata.
        public (Union[Unset, bool]): If true, this client is public and cannot securely store a client secret.
            Only the authorization code flow with proof key for code exchange (PKCE) may be used.
            Public clients cannot be updated to be confidential clients, and vice versa.
    """

    name: str
    callback_url: str
    scopes: Union[Unset, str] = "profile email"
    public: Union[Unset, bool] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        name = self.name

        callback_url = self.callback_url

        scopes = self.scopes

        public = self.public

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "callback_url": callback_url,
            }
        )
        if scopes is not UNSET:
            field_dict["scopes"] = scopes
        if public is not UNSET:
            field_dict["public"] = public

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        name = d.pop("name")

        callback_url = d.pop("callback_url")

        scopes = d.pop("scopes", UNSET)

        public = d.pop("public", UNSET)

        create_o_auth_application_body = cls(
            name=name,
            callback_url=callback_url,
            scopes=scopes,
            public=public,
        )

        create_o_auth_application_body.additional_properties = d
        return create_o_auth_application_body

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
