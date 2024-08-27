from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.instance_restrictions_object import InstanceRestrictionsObject
from ..types import UNSET, Unset

T = TypeVar("T", bound="InstanceRestrictions")


@_attrs_define
class InstanceRestrictions:
    """
    Attributes:
        object_ (Union[Unset, InstanceRestrictionsObject]): String representing the object's type. Objects of the same
            type share the same value.
        allowlist (Union[Unset, bool]):
        blocklist (Union[Unset, bool]):
        block_email_subaddresses (Union[Unset, bool]):
        ignore_dots_for_gmail_addresses (Union[Unset, bool]):
    """

    object_: Union[Unset, InstanceRestrictionsObject] = UNSET
    allowlist: Union[Unset, bool] = UNSET
    blocklist: Union[Unset, bool] = UNSET
    block_email_subaddresses: Union[Unset, bool] = UNSET
    ignore_dots_for_gmail_addresses: Union[Unset, bool] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        object_: Union[Unset, str] = UNSET
        if not isinstance(self.object_, Unset):
            object_ = self.object_.value

        allowlist = self.allowlist

        blocklist = self.blocklist

        block_email_subaddresses = self.block_email_subaddresses

        ignore_dots_for_gmail_addresses = self.ignore_dots_for_gmail_addresses

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if object_ is not UNSET:
            field_dict["object"] = object_
        if allowlist is not UNSET:
            field_dict["allowlist"] = allowlist
        if blocklist is not UNSET:
            field_dict["blocklist"] = blocklist
        if block_email_subaddresses is not UNSET:
            field_dict["block_email_subaddresses"] = block_email_subaddresses
        if ignore_dots_for_gmail_addresses is not UNSET:
            field_dict["ignore_dots_for_gmail_addresses"] = ignore_dots_for_gmail_addresses

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        _object_ = d.pop("object", UNSET)
        object_: Union[Unset, InstanceRestrictionsObject]
        if isinstance(_object_, Unset):
            object_ = UNSET
        else:
            object_ = InstanceRestrictionsObject(_object_)

        allowlist = d.pop("allowlist", UNSET)

        blocklist = d.pop("blocklist", UNSET)

        block_email_subaddresses = d.pop("block_email_subaddresses", UNSET)

        ignore_dots_for_gmail_addresses = d.pop("ignore_dots_for_gmail_addresses", UNSET)

        instance_restrictions = cls(
            object_=object_,
            allowlist=allowlist,
            blocklist=blocklist,
            block_email_subaddresses=block_email_subaddresses,
            ignore_dots_for_gmail_addresses=ignore_dots_for_gmail_addresses,
        )

        instance_restrictions.additional_properties = d
        return instance_restrictions

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
