from typing import TYPE_CHECKING, Any, Dict, Type, TypeVar, Union, cast

from attrs import define as _attrs_define

from ..models.create_saml_connection_body_provider import CreateSAMLConnectionBodyProvider
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.create_saml_connection_body_attribute_mapping_type_0 import (
        CreateSAMLConnectionBodyAttributeMappingType0,
    )


T = TypeVar("T", bound="CreateSAMLConnectionBody")


@_attrs_define
class CreateSAMLConnectionBody:
    """
    Attributes:
        name (str): The name to use as a label for this SAML Connection
        domain (str): The domain of your organization. Sign in flows using an email with this domain, will use this SAML
            Connection.
        provider (CreateSAMLConnectionBodyProvider): The IdP provider of the connection.
        idp_entity_id (Union[None, Unset, str]): The Entity ID as provided by the IdP
        idp_sso_url (Union[None, Unset, str]): The Single-Sign On URL as provided by the IdP
        idp_certificate (Union[None, Unset, str]): The X.509 certificate as provided by the IdP
        idp_metadata_url (Union[None, Unset, str]): The URL which serves the IdP metadata. If present, it takes priority
            over the corresponding individual properties
        idp_metadata (Union[None, Unset, str]): The XML content of the IdP metadata file. If present, it takes priority
            over the corresponding individual properties
        attribute_mapping (Union['CreateSAMLConnectionBodyAttributeMappingType0', None, Unset]): Define the attribute
            name mapping between Identity Provider and Clerk's user properties
    """

    name: str
    domain: str
    provider: CreateSAMLConnectionBodyProvider
    idp_entity_id: Union[None, Unset, str] = UNSET
    idp_sso_url: Union[None, Unset, str] = UNSET
    idp_certificate: Union[None, Unset, str] = UNSET
    idp_metadata_url: Union[None, Unset, str] = UNSET
    idp_metadata: Union[None, Unset, str] = UNSET
    attribute_mapping: Union["CreateSAMLConnectionBodyAttributeMappingType0", None, Unset] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        from ..models.create_saml_connection_body_attribute_mapping_type_0 import (
            CreateSAMLConnectionBodyAttributeMappingType0,
        )

        name = self.name

        domain = self.domain

        provider = self.provider.value

        idp_entity_id: Union[None, Unset, str]
        if isinstance(self.idp_entity_id, Unset):
            idp_entity_id = UNSET
        else:
            idp_entity_id = self.idp_entity_id

        idp_sso_url: Union[None, Unset, str]
        if isinstance(self.idp_sso_url, Unset):
            idp_sso_url = UNSET
        else:
            idp_sso_url = self.idp_sso_url

        idp_certificate: Union[None, Unset, str]
        if isinstance(self.idp_certificate, Unset):
            idp_certificate = UNSET
        else:
            idp_certificate = self.idp_certificate

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

        attribute_mapping: Union[Dict[str, Any], None, Unset]
        if isinstance(self.attribute_mapping, Unset):
            attribute_mapping = UNSET
        elif isinstance(self.attribute_mapping, CreateSAMLConnectionBodyAttributeMappingType0):
            attribute_mapping = self.attribute_mapping.to_dict()
        else:
            attribute_mapping = self.attribute_mapping

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "name": name,
                "domain": domain,
                "provider": provider,
            }
        )
        if idp_entity_id is not UNSET:
            field_dict["idp_entity_id"] = idp_entity_id
        if idp_sso_url is not UNSET:
            field_dict["idp_sso_url"] = idp_sso_url
        if idp_certificate is not UNSET:
            field_dict["idp_certificate"] = idp_certificate
        if idp_metadata_url is not UNSET:
            field_dict["idp_metadata_url"] = idp_metadata_url
        if idp_metadata is not UNSET:
            field_dict["idp_metadata"] = idp_metadata
        if attribute_mapping is not UNSET:
            field_dict["attribute_mapping"] = attribute_mapping

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.create_saml_connection_body_attribute_mapping_type_0 import (
            CreateSAMLConnectionBodyAttributeMappingType0,
        )

        d = src_dict.copy()
        name = d.pop("name")

        domain = d.pop("domain")

        provider = CreateSAMLConnectionBodyProvider(d.pop("provider"))

        def _parse_idp_entity_id(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        idp_entity_id = _parse_idp_entity_id(d.pop("idp_entity_id", UNSET))

        def _parse_idp_sso_url(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        idp_sso_url = _parse_idp_sso_url(d.pop("idp_sso_url", UNSET))

        def _parse_idp_certificate(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        idp_certificate = _parse_idp_certificate(d.pop("idp_certificate", UNSET))

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

        def _parse_attribute_mapping(
            data: object,
        ) -> Union["CreateSAMLConnectionBodyAttributeMappingType0", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                attribute_mapping_type_0 = CreateSAMLConnectionBodyAttributeMappingType0.from_dict(data)

                return attribute_mapping_type_0
            except:  # noqa: E722
                pass
            return cast(Union["CreateSAMLConnectionBodyAttributeMappingType0", None, Unset], data)

        attribute_mapping = _parse_attribute_mapping(d.pop("attribute_mapping", UNSET))

        create_saml_connection_body = cls(
            name=name,
            domain=domain,
            provider=provider,
            idp_entity_id=idp_entity_id,
            idp_sso_url=idp_sso_url,
            idp_certificate=idp_certificate,
            idp_metadata_url=idp_metadata_url,
            idp_metadata=idp_metadata,
            attribute_mapping=attribute_mapping,
        )

        return create_saml_connection_body
