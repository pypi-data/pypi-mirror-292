from typing import Any, Dict, Type, TypeVar, Union, cast

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="ToggleTemplateDeliveryBody")


@_attrs_define
class ToggleTemplateDeliveryBody:
    """
    Attributes:
        delivered_by_clerk (Union[None, Unset, bool]): Whether Clerk should deliver emails or SMS messages based on the
            current template
    """

    delivered_by_clerk: Union[None, Unset, bool] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        delivered_by_clerk: Union[None, Unset, bool]
        if isinstance(self.delivered_by_clerk, Unset):
            delivered_by_clerk = UNSET
        else:
            delivered_by_clerk = self.delivered_by_clerk

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if delivered_by_clerk is not UNSET:
            field_dict["delivered_by_clerk"] = delivered_by_clerk

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def _parse_delivered_by_clerk(data: object) -> Union[None, Unset, bool]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, bool], data)

        delivered_by_clerk = _parse_delivered_by_clerk(d.pop("delivered_by_clerk", UNSET))

        toggle_template_delivery_body = cls(
            delivered_by_clerk=delivered_by_clerk,
        )

        return toggle_template_delivery_body
