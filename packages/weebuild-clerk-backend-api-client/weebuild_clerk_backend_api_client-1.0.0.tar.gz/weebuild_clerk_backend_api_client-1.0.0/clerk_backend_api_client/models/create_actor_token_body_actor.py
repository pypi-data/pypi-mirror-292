from typing import Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="CreateActorTokenBodyActor")


@_attrs_define
class CreateActorTokenBodyActor:
    """The actor payload. It needs to include a sub property which should contain the ID of the actor.
    This whole payload will be also included in the JWT session token.

        Example:
            {'sub': 'user_2OEpKhcCN1Lat9NQ0G6puh7q5Rb'}

    """

    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        create_actor_token_body_actor = cls()

        create_actor_token_body_actor.additional_properties = d
        return create_actor_token_body_actor

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
