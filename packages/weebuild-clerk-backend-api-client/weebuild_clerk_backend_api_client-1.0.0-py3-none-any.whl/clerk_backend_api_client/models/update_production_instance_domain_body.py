from typing import Any, Dict, Type, TypeVar, Union

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="UpdateProductionInstanceDomainBody")


@_attrs_define
class UpdateProductionInstanceDomainBody:
    """
    Attributes:
        home_url (Union[Unset, str]): The new home URL of the production instance e.g. https://www.example.com
    """

    home_url: Union[Unset, str] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        home_url = self.home_url

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if home_url is not UNSET:
            field_dict["home_url"] = home_url

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        home_url = d.pop("home_url", UNSET)

        update_production_instance_domain_body = cls(
            home_url=home_url,
        )

        return update_production_instance_domain_body
