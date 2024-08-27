from typing import Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="UpdateSignUpBody")


@_attrs_define
class UpdateSignUpBody:
    """
    Attributes:
        custom_action (Union[Unset, bool]): Specifies whether a custom action has run for this sign-up attempt.
            This is important when your instance has been configured to require a custom action to run before converting a
            sign-up into a user.
            After executing any external business logic you deem necessary, you can mark the sign-up as ready-to-convert by
            setting `custom_action` to `true`.
        external_id (Union[None, Unset, str]): The ID of the guest attempting to sign up as used in your external
            systems or your previous authentication solution.
            This will be copied to the resulting user when the sign-up is completed.
    """

    custom_action: Union[Unset, bool] = UNSET
    external_id: Union[None, Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        custom_action = self.custom_action

        external_id: Union[None, Unset, str]
        if isinstance(self.external_id, Unset):
            external_id = UNSET
        else:
            external_id = self.external_id

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if custom_action is not UNSET:
            field_dict["custom_action"] = custom_action
        if external_id is not UNSET:
            field_dict["external_id"] = external_id

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        custom_action = d.pop("custom_action", UNSET)

        def _parse_external_id(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        external_id = _parse_external_id(d.pop("external_id", UNSET))

        update_sign_up_body = cls(
            custom_action=custom_action,
            external_id=external_id,
        )

        update_sign_up_body.additional_properties = d
        return update_sign_up_body

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
