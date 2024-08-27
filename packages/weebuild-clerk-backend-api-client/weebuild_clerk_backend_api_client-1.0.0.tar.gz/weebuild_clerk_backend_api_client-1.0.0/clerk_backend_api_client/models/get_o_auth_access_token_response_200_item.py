from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.get_o_auth_access_token_response_200_item_public_metadata import (
        GetOAuthAccessTokenResponse200ItemPublicMetadata,
    )


T = TypeVar("T", bound="GetOAuthAccessTokenResponse200Item")


@_attrs_define
class GetOAuthAccessTokenResponse200Item:
    """
    Attributes:
        object_ (Union[Unset, str]):
        external_account_id (Union[Unset, str]): External account ID
        provider_user_id (Union[Unset, str]): The unique ID of the user in the external provider's system
        token (Union[Unset, str]): The access token
        provider (Union[Unset, str]): The ID of the provider
        public_metadata (Union[Unset, GetOAuthAccessTokenResponse200ItemPublicMetadata]):
        label (Union[None, Unset, str]):
        scopes (Union[Unset, List[str]]): The list of scopes that the token is valid for.
            Only present for OAuth 2.0 tokens.
        token_secret (Union[Unset, str]): The token secret. Only present for OAuth 1.0 tokens.
    """

    object_: Union[Unset, str] = UNSET
    external_account_id: Union[Unset, str] = UNSET
    provider_user_id: Union[Unset, str] = UNSET
    token: Union[Unset, str] = UNSET
    provider: Union[Unset, str] = UNSET
    public_metadata: Union[Unset, "GetOAuthAccessTokenResponse200ItemPublicMetadata"] = UNSET
    label: Union[None, Unset, str] = UNSET
    scopes: Union[Unset, List[str]] = UNSET
    token_secret: Union[Unset, str] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        object_ = self.object_

        external_account_id = self.external_account_id

        provider_user_id = self.provider_user_id

        token = self.token

        provider = self.provider

        public_metadata: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.public_metadata, Unset):
            public_metadata = self.public_metadata.to_dict()

        label: Union[None, Unset, str]
        if isinstance(self.label, Unset):
            label = UNSET
        else:
            label = self.label

        scopes: Union[Unset, List[str]] = UNSET
        if not isinstance(self.scopes, Unset):
            scopes = self.scopes

        token_secret = self.token_secret

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if object_ is not UNSET:
            field_dict["object"] = object_
        if external_account_id is not UNSET:
            field_dict["external_account_id"] = external_account_id
        if provider_user_id is not UNSET:
            field_dict["provider_user_id"] = provider_user_id
        if token is not UNSET:
            field_dict["token"] = token
        if provider is not UNSET:
            field_dict["provider"] = provider
        if public_metadata is not UNSET:
            field_dict["public_metadata"] = public_metadata
        if label is not UNSET:
            field_dict["label"] = label
        if scopes is not UNSET:
            field_dict["scopes"] = scopes
        if token_secret is not UNSET:
            field_dict["token_secret"] = token_secret

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.get_o_auth_access_token_response_200_item_public_metadata import (
            GetOAuthAccessTokenResponse200ItemPublicMetadata,
        )

        d = src_dict.copy()
        object_ = d.pop("object", UNSET)

        external_account_id = d.pop("external_account_id", UNSET)

        provider_user_id = d.pop("provider_user_id", UNSET)

        token = d.pop("token", UNSET)

        provider = d.pop("provider", UNSET)

        _public_metadata = d.pop("public_metadata", UNSET)
        public_metadata: Union[Unset, GetOAuthAccessTokenResponse200ItemPublicMetadata]
        if isinstance(_public_metadata, Unset):
            public_metadata = UNSET
        else:
            public_metadata = GetOAuthAccessTokenResponse200ItemPublicMetadata.from_dict(_public_metadata)

        def _parse_label(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        label = _parse_label(d.pop("label", UNSET))

        scopes = cast(List[str], d.pop("scopes", UNSET))

        token_secret = d.pop("token_secret", UNSET)

        get_o_auth_access_token_response_200_item = cls(
            object_=object_,
            external_account_id=external_account_id,
            provider_user_id=provider_user_id,
            token=token,
            provider=provider,
            public_metadata=public_metadata,
            label=label,
            scopes=scopes,
            token_secret=token_secret,
        )

        return get_o_auth_access_token_response_200_item
