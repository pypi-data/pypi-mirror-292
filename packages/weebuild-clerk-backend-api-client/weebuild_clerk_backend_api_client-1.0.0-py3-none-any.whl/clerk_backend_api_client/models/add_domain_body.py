from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="AddDomainBody")


@_attrs_define
class AddDomainBody:
    """
    Attributes:
        name (str): The new domain name. Can contain the port for development instances.
        is_satellite (bool): Marks the new domain as satellite. Only `true` is accepted at the moment.
        proxy_url (Union[Unset, str]): The full URL of the proxy which will forward requests to the Clerk Frontend API
            for this domain. Applicable only to production instances.
    """

    name: str
    is_satellite: bool
    proxy_url: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        name = self.name

        is_satellite = self.is_satellite

        proxy_url = self.proxy_url

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "is_satellite": is_satellite,
            }
        )
        if proxy_url is not UNSET:
            field_dict["proxy_url"] = proxy_url

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        name = d.pop("name")

        is_satellite = d.pop("is_satellite")

        proxy_url = d.pop("proxy_url", UNSET)

        add_domain_body = cls(
            name=name,
            is_satellite=is_satellite,
            proxy_url=proxy_url,
        )

        add_domain_body.additional_properties = d
        return add_domain_body

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
