from typing import TYPE_CHECKING, Any, Dict, Type, TypeVar, Union, cast

from attrs import define as _attrs_define

from ..models.session_object import SessionObject
from ..models.session_status import SessionStatus
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.session_actor_type_0 import SessionActorType0


T = TypeVar("T", bound="Session")


@_attrs_define
class Session:
    """
    Attributes:
        object_ (SessionObject): String representing the object's type. Objects of the same type share the same value.
        id (str):
        user_id (str):
        client_id (str):
        status (SessionStatus):
        last_active_at (int):
        expire_at (int):
        abandon_at (int):
        updated_at (int): Unix timestamp of last update.
        created_at (int): Unix timestamp of creation.
        actor (Union['SessionActorType0', None, Unset]):
        last_active_organization_id (Union[None, Unset, str]):
    """

    object_: SessionObject
    id: str
    user_id: str
    client_id: str
    status: SessionStatus
    last_active_at: int
    expire_at: int
    abandon_at: int
    updated_at: int
    created_at: int
    actor: Union["SessionActorType0", None, Unset] = UNSET
    last_active_organization_id: Union[None, Unset, str] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        from ..models.session_actor_type_0 import SessionActorType0

        object_ = self.object_.value

        id = self.id

        user_id = self.user_id

        client_id = self.client_id

        status = self.status.value

        last_active_at = self.last_active_at

        expire_at = self.expire_at

        abandon_at = self.abandon_at

        updated_at = self.updated_at

        created_at = self.created_at

        actor: Union[Dict[str, Any], None, Unset]
        if isinstance(self.actor, Unset):
            actor = UNSET
        elif isinstance(self.actor, SessionActorType0):
            actor = self.actor.to_dict()
        else:
            actor = self.actor

        last_active_organization_id: Union[None, Unset, str]
        if isinstance(self.last_active_organization_id, Unset):
            last_active_organization_id = UNSET
        else:
            last_active_organization_id = self.last_active_organization_id

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "object": object_,
                "id": id,
                "user_id": user_id,
                "client_id": client_id,
                "status": status,
                "last_active_at": last_active_at,
                "expire_at": expire_at,
                "abandon_at": abandon_at,
                "updated_at": updated_at,
                "created_at": created_at,
            }
        )
        if actor is not UNSET:
            field_dict["actor"] = actor
        if last_active_organization_id is not UNSET:
            field_dict["last_active_organization_id"] = last_active_organization_id

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.session_actor_type_0 import SessionActorType0

        d = src_dict.copy()
        object_ = SessionObject(d.pop("object"))

        id = d.pop("id")

        user_id = d.pop("user_id")

        client_id = d.pop("client_id")

        status = SessionStatus(d.pop("status"))

        last_active_at = d.pop("last_active_at")

        expire_at = d.pop("expire_at")

        abandon_at = d.pop("abandon_at")

        updated_at = d.pop("updated_at")

        created_at = d.pop("created_at")

        def _parse_actor(data: object) -> Union["SessionActorType0", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                actor_type_0 = SessionActorType0.from_dict(data)

                return actor_type_0
            except:  # noqa: E722
                pass
            return cast(Union["SessionActorType0", None, Unset], data)

        actor = _parse_actor(d.pop("actor", UNSET))

        def _parse_last_active_organization_id(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        last_active_organization_id = _parse_last_active_organization_id(d.pop("last_active_organization_id", UNSET))

        session = cls(
            object_=object_,
            id=id,
            user_id=user_id,
            client_id=client_id,
            status=status,
            last_active_at=last_active_at,
            expire_at=expire_at,
            abandon_at=abandon_at,
            updated_at=updated_at,
            created_at=created_at,
            actor=actor,
            last_active_organization_id=last_active_organization_id,
        )

        return session
