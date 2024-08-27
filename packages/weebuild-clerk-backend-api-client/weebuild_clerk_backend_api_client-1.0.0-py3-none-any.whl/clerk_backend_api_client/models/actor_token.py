from typing import TYPE_CHECKING, Any, Dict, Type, TypeVar, Union, cast

from attrs import define as _attrs_define

from ..models.actor_token_object import ActorTokenObject
from ..models.actor_token_status import ActorTokenStatus
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.actor_token_actor import ActorTokenActor


T = TypeVar("T", bound="ActorToken")


@_attrs_define
class ActorToken:
    """
    Attributes:
        object_ (ActorTokenObject):
        id (str):
        status (ActorTokenStatus):
        user_id (str):
        actor (ActorTokenActor):
        created_at (int): Unix timestamp of creation.
        updated_at (int): Unix timestamp of last update.
        token (Union[None, Unset, str]):
        url (Union[None, Unset, str]):
    """

    object_: ActorTokenObject
    id: str
    status: ActorTokenStatus
    user_id: str
    actor: "ActorTokenActor"
    created_at: int
    updated_at: int
    token: Union[None, Unset, str] = UNSET
    url: Union[None, Unset, str] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        object_ = self.object_.value

        id = self.id

        status = self.status.value

        user_id = self.user_id

        actor = self.actor.to_dict()

        created_at = self.created_at

        updated_at = self.updated_at

        token: Union[None, Unset, str]
        if isinstance(self.token, Unset):
            token = UNSET
        else:
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
                "actor": actor,
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
        from ..models.actor_token_actor import ActorTokenActor

        d = src_dict.copy()
        object_ = ActorTokenObject(d.pop("object"))

        id = d.pop("id")

        status = ActorTokenStatus(d.pop("status"))

        user_id = d.pop("user_id")

        actor = ActorTokenActor.from_dict(d.pop("actor"))

        created_at = d.pop("created_at")

        updated_at = d.pop("updated_at")

        def _parse_token(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        token = _parse_token(d.pop("token", UNSET))

        def _parse_url(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        url = _parse_url(d.pop("url", UNSET))

        actor_token = cls(
            object_=object_,
            id=id,
            status=status,
            user_id=user_id,
            actor=actor,
            created_at=created_at,
            updated_at=updated_at,
            token=token,
            url=url,
        )

        return actor_token
