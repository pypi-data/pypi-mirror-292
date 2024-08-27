from typing import TYPE_CHECKING, Any, Dict, Type, TypeVar, Union, cast

from attrs import define as _attrs_define

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.update_saml_connection_body_attribute_mapping_type_0 import (
        UpdateSAMLConnectionBodyAttributeMappingType0,
    )


T = TypeVar("T", bound="UpdateSAMLConnectionBody")


@_attrs_define
class UpdateSAMLConnectionBody:
    """
    Attributes:
        name (Union[None, Unset, str]): The name of the new SAML Connection
        domain (Union[None, Unset, str]): The domain to use for the new SAML Connection
        idp_entity_id (Union[None, Unset, str]): The entity id as provided by the IdP
        idp_sso_url (Union[None, Unset, str]): The SSO url as provided by the IdP
        idp_certificate (Union[None, Unset, str]): The x509 certificated as provided by the IdP
        idp_metadata_url (Union[None, Unset, str]): The URL which serves the IdP metadata. If present, it takes priority
            over the corresponding individual properties and replaces them
        idp_metadata (Union[None, Unset, str]): The XML content of the IdP metadata file. If present, it takes priority
            over the corresponding individual properties
        attribute_mapping (Union['UpdateSAMLConnectionBodyAttributeMappingType0', None, Unset]): Define the atrtibute
            name mapping between Identity Provider and Clerk's user properties
        active (Union[None, Unset, bool]): Activate or de-activate the SAML Connection
        sync_user_attributes (Union[None, Unset, bool]): Controls whether to update the user's attributes in each sign-
            in
        allow_subdomains (Union[None, Unset, bool]): Allow users with an email address subdomain to use this connection
            in order to authenticate
        allow_idp_initiated (Union[None, Unset, bool]): Enable or deactivate IdP-initiated flows
    """

    name: Union[None, Unset, str] = UNSET
    domain: Union[None, Unset, str] = UNSET
    idp_entity_id: Union[None, Unset, str] = UNSET
    idp_sso_url: Union[None, Unset, str] = UNSET
    idp_certificate: Union[None, Unset, str] = UNSET
    idp_metadata_url: Union[None, Unset, str] = UNSET
    idp_metadata: Union[None, Unset, str] = UNSET
    attribute_mapping: Union["UpdateSAMLConnectionBodyAttributeMappingType0", None, Unset] = UNSET
    active: Union[None, Unset, bool] = UNSET
    sync_user_attributes: Union[None, Unset, bool] = UNSET
    allow_subdomains: Union[None, Unset, bool] = UNSET
    allow_idp_initiated: Union[None, Unset, bool] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        from ..models.update_saml_connection_body_attribute_mapping_type_0 import (
            UpdateSAMLConnectionBodyAttributeMappingType0,
        )

        name: Union[None, Unset, str]
        if isinstance(self.name, Unset):
            name = UNSET
        else:
            name = self.name

        domain: Union[None, Unset, str]
        if isinstance(self.domain, Unset):
            domain = UNSET
        else:
            domain = self.domain

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
        elif isinstance(self.attribute_mapping, UpdateSAMLConnectionBodyAttributeMappingType0):
            attribute_mapping = self.attribute_mapping.to_dict()
        else:
            attribute_mapping = self.attribute_mapping

        active: Union[None, Unset, bool]
        if isinstance(self.active, Unset):
            active = UNSET
        else:
            active = self.active

        sync_user_attributes: Union[None, Unset, bool]
        if isinstance(self.sync_user_attributes, Unset):
            sync_user_attributes = UNSET
        else:
            sync_user_attributes = self.sync_user_attributes

        allow_subdomains: Union[None, Unset, bool]
        if isinstance(self.allow_subdomains, Unset):
            allow_subdomains = UNSET
        else:
            allow_subdomains = self.allow_subdomains

        allow_idp_initiated: Union[None, Unset, bool]
        if isinstance(self.allow_idp_initiated, Unset):
            allow_idp_initiated = UNSET
        else:
            allow_idp_initiated = self.allow_idp_initiated

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if name is not UNSET:
            field_dict["name"] = name
        if domain is not UNSET:
            field_dict["domain"] = domain
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
        if active is not UNSET:
            field_dict["active"] = active
        if sync_user_attributes is not UNSET:
            field_dict["sync_user_attributes"] = sync_user_attributes
        if allow_subdomains is not UNSET:
            field_dict["allow_subdomains"] = allow_subdomains
        if allow_idp_initiated is not UNSET:
            field_dict["allow_idp_initiated"] = allow_idp_initiated

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.update_saml_connection_body_attribute_mapping_type_0 import (
            UpdateSAMLConnectionBodyAttributeMappingType0,
        )

        d = src_dict.copy()

        def _parse_name(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        name = _parse_name(d.pop("name", UNSET))

        def _parse_domain(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        domain = _parse_domain(d.pop("domain", UNSET))

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
        ) -> Union["UpdateSAMLConnectionBodyAttributeMappingType0", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                attribute_mapping_type_0 = UpdateSAMLConnectionBodyAttributeMappingType0.from_dict(data)

                return attribute_mapping_type_0
            except:  # noqa: E722
                pass
            return cast(Union["UpdateSAMLConnectionBodyAttributeMappingType0", None, Unset], data)

        attribute_mapping = _parse_attribute_mapping(d.pop("attribute_mapping", UNSET))

        def _parse_active(data: object) -> Union[None, Unset, bool]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, bool], data)

        active = _parse_active(d.pop("active", UNSET))

        def _parse_sync_user_attributes(data: object) -> Union[None, Unset, bool]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, bool], data)

        sync_user_attributes = _parse_sync_user_attributes(d.pop("sync_user_attributes", UNSET))

        def _parse_allow_subdomains(data: object) -> Union[None, Unset, bool]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, bool], data)

        allow_subdomains = _parse_allow_subdomains(d.pop("allow_subdomains", UNSET))

        def _parse_allow_idp_initiated(data: object) -> Union[None, Unset, bool]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, bool], data)

        allow_idp_initiated = _parse_allow_idp_initiated(d.pop("allow_idp_initiated", UNSET))

        update_saml_connection_body = cls(
            name=name,
            domain=domain,
            idp_entity_id=idp_entity_id,
            idp_sso_url=idp_sso_url,
            idp_certificate=idp_certificate,
            idp_metadata_url=idp_metadata_url,
            idp_metadata=idp_metadata,
            attribute_mapping=attribute_mapping,
            active=active,
            sync_user_attributes=sync_user_attributes,
            allow_subdomains=allow_subdomains,
            allow_idp_initiated=allow_idp_initiated,
        )

        return update_saml_connection_body
