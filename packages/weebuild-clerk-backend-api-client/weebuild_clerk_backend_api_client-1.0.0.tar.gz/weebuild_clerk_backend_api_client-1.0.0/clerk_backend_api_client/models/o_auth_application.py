from typing import Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.o_auth_application_object import OAuthApplicationObject

T = TypeVar("T", bound="OAuthApplication")


@_attrs_define
class OAuthApplication:
    """
    Attributes:
        object_ (OAuthApplicationObject):
        id (str):
        instance_id (str):
        name (str):
        client_id (str):
        public (bool):
        scopes (str):
        callback_url (str):
        authorize_url (str):
        token_fetch_url (str):
        user_info_url (str):
        created_at (int): Unix timestamp of creation.
        updated_at (int): Unix timestamp of last update.
    """

    object_: OAuthApplicationObject
    id: str
    instance_id: str
    name: str
    client_id: str
    public: bool
    scopes: str
    callback_url: str
    authorize_url: str
    token_fetch_url: str
    user_info_url: str
    created_at: int
    updated_at: int
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        object_ = self.object_.value

        id = self.id

        instance_id = self.instance_id

        name = self.name

        client_id = self.client_id

        public = self.public

        scopes = self.scopes

        callback_url = self.callback_url

        authorize_url = self.authorize_url

        token_fetch_url = self.token_fetch_url

        user_info_url = self.user_info_url

        created_at = self.created_at

        updated_at = self.updated_at

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "object": object_,
                "id": id,
                "instance_id": instance_id,
                "name": name,
                "client_id": client_id,
                "public": public,
                "scopes": scopes,
                "callback_url": callback_url,
                "authorize_url": authorize_url,
                "token_fetch_url": token_fetch_url,
                "user_info_url": user_info_url,
                "created_at": created_at,
                "updated_at": updated_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        object_ = OAuthApplicationObject(d.pop("object"))

        id = d.pop("id")

        instance_id = d.pop("instance_id")

        name = d.pop("name")

        client_id = d.pop("client_id")

        public = d.pop("public")

        scopes = d.pop("scopes")

        callback_url = d.pop("callback_url")

        authorize_url = d.pop("authorize_url")

        token_fetch_url = d.pop("token_fetch_url")

        user_info_url = d.pop("user_info_url")

        created_at = d.pop("created_at")

        updated_at = d.pop("updated_at")

        o_auth_application = cls(
            object_=object_,
            id=id,
            instance_id=instance_id,
            name=name,
            client_id=client_id,
            public=public,
            scopes=scopes,
            callback_url=callback_url,
            authorize_url=authorize_url,
            token_fetch_url=token_fetch_url,
            user_info_url=user_info_url,
            created_at=created_at,
            updated_at=updated_at,
        )

        o_auth_application.additional_properties = d
        return o_auth_application

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
