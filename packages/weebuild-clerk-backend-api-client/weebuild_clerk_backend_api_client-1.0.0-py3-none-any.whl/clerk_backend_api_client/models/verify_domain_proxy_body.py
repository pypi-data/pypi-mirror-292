from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="VerifyDomainProxyBody")


@_attrs_define
class VerifyDomainProxyBody:
    """
    Attributes:
        domain_id (Union[Unset, str]): The ID of the domain that will be updated.
        proxy_url (Union[Unset, str]): The full URL of the proxy which will forward requests to the Clerk Frontend API
            for this domain. e.g. https://example.com/__clerk
    """

    domain_id: Union[Unset, str] = UNSET
    proxy_url: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        domain_id = self.domain_id

        proxy_url = self.proxy_url

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if domain_id is not UNSET:
            field_dict["domain_id"] = domain_id
        if proxy_url is not UNSET:
            field_dict["proxy_url"] = proxy_url

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        domain_id = d.pop("domain_id", UNSET)

        proxy_url = d.pop("proxy_url", UNSET)

        verify_domain_proxy_body = cls(
            domain_id=domain_id,
            proxy_url=proxy_url,
        )

        verify_domain_proxy_body.additional_properties = d
        return verify_domain_proxy_body

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
