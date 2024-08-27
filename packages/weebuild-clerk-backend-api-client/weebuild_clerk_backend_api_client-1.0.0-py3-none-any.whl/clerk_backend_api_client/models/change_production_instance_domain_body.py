from typing import Any, Dict, Type, TypeVar, Union

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="ChangeProductionInstanceDomainBody")


@_attrs_define
class ChangeProductionInstanceDomainBody:
    """
    Attributes:
        home_url (Union[Unset, str]): The new home URL of the production instance e.g. https://www.example.com
        is_secondary (Union[Unset, bool]): Whether this is a domain for a secondary app, meaning that any subdomain
            provided is significant and
            will be stored as part of the domain. This is useful for supporting multiple apps (one primary and
            multiple secondaries) on the same root domain (eTLD+1).
    """

    home_url: Union[Unset, str] = UNSET
    is_secondary: Union[Unset, bool] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        home_url = self.home_url

        is_secondary = self.is_secondary

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if home_url is not UNSET:
            field_dict["home_url"] = home_url
        if is_secondary is not UNSET:
            field_dict["is_secondary"] = is_secondary

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        home_url = d.pop("home_url", UNSET)

        is_secondary = d.pop("is_secondary", UNSET)

        change_production_instance_domain_body = cls(
            home_url=home_url,
            is_secondary=is_secondary,
        )

        return change_production_instance_domain_body
