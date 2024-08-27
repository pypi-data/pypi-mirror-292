from typing import Any, Dict, Type, TypeVar, Union, cast

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="UpdateDomainBody")


@_attrs_define
class UpdateDomainBody:
    """
    Attributes:
        name (Union[None, Unset, str]): The new domain name. For development instances, can contain the port,
            i.e `myhostname:3000`. For production instances, must be a valid FQDN,
            i.e `mysite.com`. Cannot contain protocol scheme.
        proxy_url (Union[None, Unset, str]): The full URL of the proxy that will forward requests to Clerk's Frontend
            API.
            Can only be updated for production instances.
        is_secondary (Union[None, Unset, bool]): Whether this is a domain for a secondary app, meaning that any
            subdomain provided is significant and
            will be stored as part of the domain. This is useful for supporting multiple apps (one primary and
            multiple secondaries) on the same root domain (eTLD+1).
    """

    name: Union[None, Unset, str] = UNSET
    proxy_url: Union[None, Unset, str] = UNSET
    is_secondary: Union[None, Unset, bool] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        name: Union[None, Unset, str]
        if isinstance(self.name, Unset):
            name = UNSET
        else:
            name = self.name

        proxy_url: Union[None, Unset, str]
        if isinstance(self.proxy_url, Unset):
            proxy_url = UNSET
        else:
            proxy_url = self.proxy_url

        is_secondary: Union[None, Unset, bool]
        if isinstance(self.is_secondary, Unset):
            is_secondary = UNSET
        else:
            is_secondary = self.is_secondary

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if name is not UNSET:
            field_dict["name"] = name
        if proxy_url is not UNSET:
            field_dict["proxy_url"] = proxy_url
        if is_secondary is not UNSET:
            field_dict["is_secondary"] = is_secondary

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def _parse_name(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        name = _parse_name(d.pop("name", UNSET))

        def _parse_proxy_url(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        proxy_url = _parse_proxy_url(d.pop("proxy_url", UNSET))

        def _parse_is_secondary(data: object) -> Union[None, Unset, bool]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, bool], data)

        is_secondary = _parse_is_secondary(d.pop("is_secondary", UNSET))

        update_domain_body = cls(
            name=name,
            proxy_url=proxy_url,
            is_secondary=is_secondary,
        )

        return update_domain_body
