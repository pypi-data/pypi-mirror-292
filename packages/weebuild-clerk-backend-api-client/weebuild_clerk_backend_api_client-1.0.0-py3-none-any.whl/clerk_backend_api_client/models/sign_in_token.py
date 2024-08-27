from typing import Any, Dict, Type, TypeVar, Union, cast

from attrs import define as _attrs_define

from ..models.sign_in_token_object import SignInTokenObject
from ..models.sign_in_token_status import SignInTokenStatus
from ..types import UNSET, Unset

T = TypeVar("T", bound="SignInToken")


@_attrs_define
class SignInToken:
    """
    Attributes:
        object_ (SignInTokenObject):
        id (str):
        status (SignInTokenStatus):
        user_id (str):
        created_at (int): Unix timestamp of creation.
        updated_at (int): Unix timestamp of last update.
        token (Union[Unset, str]):
        url (Union[None, Unset, str]):
    """

    object_: SignInTokenObject
    id: str
    status: SignInTokenStatus
    user_id: str
    created_at: int
    updated_at: int
    token: Union[Unset, str] = UNSET
    url: Union[None, Unset, str] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        object_ = self.object_.value

        id = self.id

        status = self.status.value

        user_id = self.user_id

        created_at = self.created_at

        updated_at = self.updated_at

        token = self.token

        url: Union[None, Unset, str]
        if isinstance(self.url, Unset):
            url = UNSET
        else:
            url = self.url

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "object": object_,
                "id": id,
                "status": status,
                "user_id": user_id,
                "created_at": created_at,
                "updated_at": updated_at,
            }
        )
        if token is not UNSET:
            field_dict["token"] = token
        if url is not UNSET:
            field_dict["url"] = url

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        object_ = SignInTokenObject(d.pop("object"))

        id = d.pop("id")

        status = SignInTokenStatus(d.pop("status"))

        user_id = d.pop("user_id")

        created_at = d.pop("created_at")

        updated_at = d.pop("updated_at")

        token = d.pop("token", UNSET)

        def _parse_url(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        url = _parse_url(d.pop("url", UNSET))

        sign_in_token = cls(
            object_=object_,
            id=id,
            status=status,
            user_id=user_id,
            created_at=created_at,
            updated_at=updated_at,
            token=token,
            url=url,
        )

        return sign_in_token
