from typing import TYPE_CHECKING, Any, Dict, Type, TypeVar, Union

from attrs import define as _attrs_define

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.create_actor_token_body_actor import CreateActorTokenBodyActor


T = TypeVar("T", bound="CreateActorTokenBody")


@_attrs_define
class CreateActorTokenBody:
    """
    Attributes:
        user_id (str): The ID of the user being impersonated.
        actor (CreateActorTokenBodyActor): The actor payload. It needs to include a sub property which should contain
            the ID of the actor.
            This whole payload will be also included in the JWT session token. Example: {'sub':
            'user_2OEpKhcCN1Lat9NQ0G6puh7q5Rb'}.
        expires_in_seconds (Union[Unset, int]): Optional parameter to specify the life duration of the actor token in
            seconds.
            By default, the duration is 1 hour. Default: 3600.
        session_max_duration_in_seconds (Union[Unset, int]): The maximum duration that the session which will be created
            by the generated actor token should last.
            By default, the duration of a session created via an actor token, lasts 30 minutes. Default: 1800.
    """

    user_id: str
    actor: "CreateActorTokenBodyActor"
    expires_in_seconds: Union[Unset, int] = 3600
    session_max_duration_in_seconds: Union[Unset, int] = 1800

    def to_dict(self) -> Dict[str, Any]:
        user_id = self.user_id

        actor = self.actor.to_dict()

        expires_in_seconds = self.expires_in_seconds

        session_max_duration_in_seconds = self.session_max_duration_in_seconds

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "user_id": user_id,
                "actor": actor,
            }
        )
        if expires_in_seconds is not UNSET:
            field_dict["expires_in_seconds"] = expires_in_seconds
        if session_max_duration_in_seconds is not UNSET:
            field_dict["session_max_duration_in_seconds"] = session_max_duration_in_seconds

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.create_actor_token_body_actor import CreateActorTokenBodyActor

        d = src_dict.copy()
        user_id = d.pop("user_id")

        actor = CreateActorTokenBodyActor.from_dict(d.pop("actor"))

        expires_in_seconds = d.pop("expires_in_seconds", UNSET)

        session_max_duration_in_seconds = d.pop("session_max_duration_in_seconds", UNSET)

        create_actor_token_body = cls(
            user_id=user_id,
            actor=actor,
            expires_in_seconds=expires_in_seconds,
            session_max_duration_in_seconds=session_max_duration_in_seconds,
        )

        return create_actor_token_body
