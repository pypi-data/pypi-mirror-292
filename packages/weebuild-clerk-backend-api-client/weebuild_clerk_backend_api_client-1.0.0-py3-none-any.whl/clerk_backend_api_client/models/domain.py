from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.domain_object import DomainObject
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.c_name_target import CNameTarget


T = TypeVar("T", bound="Domain")


@_attrs_define
class Domain:
    """
    Attributes:
        object_ (DomainObject):
        id (str):
        name (str):
        is_satellite (bool):
        frontend_api_url (str):
        development_origin (str):
        accounts_portal_url (Union[None, Unset, str]): Null for satellite domains.
        proxy_url (Union[None, Unset, str]):
        cname_targets (Union[List['CNameTarget'], None, Unset]):
    """

    object_: DomainObject
    id: str
    name: str
    is_satellite: bool
    frontend_api_url: str
    development_origin: str
    accounts_portal_url: Union[None, Unset, str] = UNSET
    proxy_url: Union[None, Unset, str] = UNSET
    cname_targets: Union[List["CNameTarget"], None, Unset] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        object_ = self.object_.value

        id = self.id

        name = self.name

        is_satellite = self.is_satellite

        frontend_api_url = self.frontend_api_url

        development_origin = self.development_origin

        accounts_portal_url: Union[None, Unset, str]
        if isinstance(self.accounts_portal_url, Unset):
            accounts_portal_url = UNSET
        else:
            accounts_portal_url = self.accounts_portal_url

        proxy_url: Union[None, Unset, str]
        if isinstance(self.proxy_url, Unset):
            proxy_url = UNSET
        else:
            proxy_url = self.proxy_url

        cname_targets: Union[List[Dict[str, Any]], None, Unset]
        if isinstance(self.cname_targets, Unset):
            cname_targets = UNSET
        elif isinstance(self.cname_targets, list):
            cname_targets = []
            for cname_targets_type_0_item_data in self.cname_targets:
                cname_targets_type_0_item = cname_targets_type_0_item_data.to_dict()
                cname_targets.append(cname_targets_type_0_item)

        else:
            cname_targets = self.cname_targets

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "object": object_,
                "id": id,
                "name": name,
                "is_satellite": is_satellite,
                "frontend_api_url": frontend_api_url,
                "development_origin": development_origin,
            }
        )
        if accounts_portal_url is not UNSET:
            field_dict["accounts_portal_url"] = accounts_portal_url
        if proxy_url is not UNSET:
            field_dict["proxy_url"] = proxy_url
        if cname_targets is not UNSET:
            field_dict["cname_targets"] = cname_targets

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.c_name_target import CNameTarget

        d = src_dict.copy()
        object_ = DomainObject(d.pop("object"))

        id = d.pop("id")

        name = d.pop("name")

        is_satellite = d.pop("is_satellite")

        frontend_api_url = d.pop("frontend_api_url")

        development_origin = d.pop("development_origin")

        def _parse_accounts_portal_url(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        accounts_portal_url = _parse_accounts_portal_url(d.pop("accounts_portal_url", UNSET))

        def _parse_proxy_url(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        proxy_url = _parse_proxy_url(d.pop("proxy_url", UNSET))

        def _parse_cname_targets(data: object) -> Union[List["CNameTarget"], None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                cname_targets_type_0 = []
                _cname_targets_type_0 = data
                for cname_targets_type_0_item_data in _cname_targets_type_0:
                    cname_targets_type_0_item = CNameTarget.from_dict(cname_targets_type_0_item_data)

                    cname_targets_type_0.append(cname_targets_type_0_item)

                return cname_targets_type_0
            except:  # noqa: E722
                pass
            return cast(Union[List["CNameTarget"], None, Unset], data)

        cname_targets = _parse_cname_targets(d.pop("cname_targets", UNSET))

        domain = cls(
            object_=object_,
            id=id,
            name=name,
            is_satellite=is_satellite,
            frontend_api_url=frontend_api_url,
            development_origin=development_origin,
            accounts_portal_url=accounts_portal_url,
            proxy_url=proxy_url,
            cname_targets=cname_targets,
        )

        domain.additional_properties = d
        return domain

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
