from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.saml_connection_object import SAMLConnectionObject
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.saml_connection_attribute_mapping import SAMLConnectionAttributeMapping


T = TypeVar("T", bound="SAMLConnection")


@_attrs_define
class SAMLConnection:
    """
    Attributes:
        object_ (SAMLConnectionObject):
        id (str):
        name (str):
        domain (str):
        idp_entity_id (Union[None, str]):
        idp_sso_url (Union[None, str]):
        idp_certificate (Union[None, str]):
        acs_url (str):
        sp_entity_id (str):
        sp_metadata_url (str):
        active (bool):
        provider (str):
        user_count (int):
        sync_user_attributes (bool):
        created_at (int): Unix timestamp of creation.
        updated_at (int): Unix timestamp of last update.
        idp_metadata_url (Union[None, Unset, str]):
        idp_metadata (Union[None, Unset, str]):
        attribute_mapping (Union[Unset, SAMLConnectionAttributeMapping]):
        allow_subdomains (Union[Unset, bool]):
        allow_idp_initiated (Union[Unset, bool]):
    """

    object_: SAMLConnectionObject
    id: str
    name: str
    domain: str
    idp_entity_id: Union[None, str]
    idp_sso_url: Union[None, str]
    idp_certificate: Union[None, str]
    acs_url: str
    sp_entity_id: str
    sp_metadata_url: str
    active: bool
    provider: str
    user_count: int
    sync_user_attributes: bool
    created_at: int
    updated_at: int
    idp_metadata_url: Union[None, Unset, str] = UNSET
    idp_metadata: Union[None, Unset, str] = UNSET
    attribute_mapping: Union[Unset, "SAMLConnectionAttributeMapping"] = UNSET
    allow_subdomains: Union[Unset, bool] = UNSET
    allow_idp_initiated: Union[Unset, bool] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        object_ = self.object_.value

        id = self.id

        name = self.name

        domain = self.domain

        idp_entity_id: Union[None, str]
        idp_entity_id = self.idp_entity_id

        idp_sso_url: Union[None, str]
        idp_sso_url = self.idp_sso_url

        idp_certificate: Union[None, str]
        idp_certificate = self.idp_certificate

        acs_url = self.acs_url

        sp_entity_id = self.sp_entity_id

        sp_metadata_url = self.sp_metadata_url

        active = self.active

        provider = self.provider

        user_count = self.user_count

        sync_user_attributes = self.sync_user_attributes

        created_at = self.created_at

        updated_at = self.updated_at

        idp_metadata_url: Union[None, Unset, str]
        if isinstance(self.idp_metadata_url, Unset):
            idp_metadata_url = UNSET
        else:
            idp_metadata_url = self.idp_metadata_url

        idp_metadata: Union[None, Unset, str]
        if isinstance(self.idp_metadata, Unset):
            idp_metadata = UNSET
        else:
            idp_metadata = self.idp_metadata

        attribute_mapping: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.attribute_mapping, Unset):
            attribute_mapping = self.attribute_mapping.to_dict()

        allow_subdomains = self.allow_subdomains

        allow_idp_initiated = self.allow_idp_initiated

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "object": object_,
                "id": id,
                "name": name,
                "domain": domain,
                "idp_entity_id": idp_entity_id,
                "idp_sso_url": idp_sso_url,
                "idp_certificate": idp_certificate,
                "acs_url": acs_url,
                "sp_entity_id": sp_entity_id,
                "sp_metadata_url": sp_metadata_url,
                "active": active,
                "provider": provider,
                "user_count": user_count,
                "sync_user_attributes": sync_user_attributes,
                "created_at": created_at,
                "updated_at": updated_at,
            }
        )
        if idp_metadata_url is not UNSET:
            field_dict["idp_metadata_url"] = idp_metadata_url
        if idp_metadata is not UNSET:
            field_dict["idp_metadata"] = idp_metadata
        if attribute_mapping is not UNSET:
            field_dict["attribute_mapping"] = attribute_mapping
        if allow_subdomains is not UNSET:
            field_dict["allow_subdomains"] = allow_subdomains
        if allow_idp_initiated is not UNSET:
            field_dict["allow_idp_initiated"] = allow_idp_initiated

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.saml_connection_attribute_mapping import SAMLConnectionAttributeMapping

        d = src_dict.copy()
        object_ = SAMLConnectionObject(d.pop("object"))

        id = d.pop("id")

        name = d.pop("name")

        domain = d.pop("domain")

        def _parse_idp_entity_id(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        idp_entity_id = _parse_idp_entity_id(d.pop("idp_entity_id"))

        def _parse_idp_sso_url(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        idp_sso_url = _parse_idp_sso_url(d.pop("idp_sso_url"))

        def _parse_idp_certificate(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        idp_certificate = _parse_idp_certificate(d.pop("idp_certificate"))

        acs_url = d.pop("acs_url")

        sp_entity_id = d.pop("sp_entity_id")

        sp_metadata_url = d.pop("sp_metadata_url")

        active = d.pop("active")

        provider = d.pop("provider")

        user_count = d.pop("user_count")

        sync_user_attributes = d.pop("sync_user_attributes")

        created_at = d.pop("created_at")

        updated_at = d.pop("updated_at")

        def _parse_idp_metadata_url(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        idp_metadata_url = _parse_idp_metadata_url(d.pop("idp_metadata_url", UNSET))

        def _parse_idp_metadata(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        idp_metadata = _parse_idp_metadata(d.pop("idp_metadata", UNSET))

        _attribute_mapping = d.pop("attribute_mapping", UNSET)
        attribute_mapping: Union[Unset, SAMLConnectionAttributeMapping]
        if isinstance(_attribute_mapping, Unset):
            attribute_mapping = UNSET
        else:
            attribute_mapping = SAMLConnectionAttributeMapping.from_dict(_attribute_mapping)

        allow_subdomains = d.pop("allow_subdomains", UNSET)

        allow_idp_initiated = d.pop("allow_idp_initiated", UNSET)

        saml_connection = cls(
            object_=object_,
            id=id,
            name=name,
            domain=domain,
            idp_entity_id=idp_entity_id,
            idp_sso_url=idp_sso_url,
            idp_certificate=idp_certificate,
            acs_url=acs_url,
            sp_entity_id=sp_entity_id,
            sp_metadata_url=sp_metadata_url,
            active=active,
            provider=provider,
            user_count=user_count,
            sync_user_attributes=sync_user_attributes,
            created_at=created_at,
            updated_at=updated_at,
            idp_metadata_url=idp_metadata_url,
            idp_metadata=idp_metadata,
            attribute_mapping=attribute_mapping,
            allow_subdomains=allow_subdomains,
            allow_idp_initiated=allow_idp_initiated,
        )

        saml_connection.additional_properties = d
        return saml_connection

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
