from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.create_jwt_template_body_claims import CreateJWTTemplateBodyClaims


T = TypeVar("T", bound="CreateJWTTemplateBody")


@_attrs_define
class CreateJWTTemplateBody:
    """
    Attributes:
        name (Union[Unset, str]): JWT template name
        claims (Union[Unset, CreateJWTTemplateBodyClaims]): JWT template claims in JSON format
        lifetime (Union[None, Unset, float]): JWT token lifetime
        allowed_clock_skew (Union[None, Unset, float]): JWT token allowed clock skew
        custom_signing_key (Union[Unset, bool]): Whether a custom signing key/algorithm is also provided for this
            template
        signing_algorithm (Union[None, Unset, str]): The custom signing algorithm to use when minting JWTs
        signing_key (Union[None, Unset, str]): The custom signing private key to use when minting JWTs
    """

    name: Union[Unset, str] = UNSET
    claims: Union[Unset, "CreateJWTTemplateBodyClaims"] = UNSET
    lifetime: Union[None, Unset, float] = UNSET
    allowed_clock_skew: Union[None, Unset, float] = UNSET
    custom_signing_key: Union[Unset, bool] = UNSET
    signing_algorithm: Union[None, Unset, str] = UNSET
    signing_key: Union[None, Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        name = self.name

        claims: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.claims, Unset):
            claims = self.claims.to_dict()

        lifetime: Union[None, Unset, float]
        if isinstance(self.lifetime, Unset):
            lifetime = UNSET
        else:
            lifetime = self.lifetime

        allowed_clock_skew: Union[None, Unset, float]
        if isinstance(self.allowed_clock_skew, Unset):
            allowed_clock_skew = UNSET
        else:
            allowed_clock_skew = self.allowed_clock_skew

        custom_signing_key = self.custom_signing_key

        signing_algorithm: Union[None, Unset, str]
        if isinstance(self.signing_algorithm, Unset):
            signing_algorithm = UNSET
        else:
            signing_algorithm = self.signing_algorithm

        signing_key: Union[None, Unset, str]
        if isinstance(self.signing_key, Unset):
            signing_key = UNSET
        else:
            signing_key = self.signing_key

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if name is not UNSET:
            field_dict["name"] = name
        if claims is not UNSET:
            field_dict["claims"] = claims
        if lifetime is not UNSET:
            field_dict["lifetime"] = lifetime
        if allowed_clock_skew is not UNSET:
            field_dict["allowed_clock_skew"] = allowed_clock_skew
        if custom_signing_key is not UNSET:
            field_dict["custom_signing_key"] = custom_signing_key
        if signing_algorithm is not UNSET:
            field_dict["signing_algorithm"] = signing_algorithm
        if signing_key is not UNSET:
            field_dict["signing_key"] = signing_key

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.create_jwt_template_body_claims import CreateJWTTemplateBodyClaims

        d = src_dict.copy()
        name = d.pop("name", UNSET)

        _claims = d.pop("claims", UNSET)
        claims: Union[Unset, CreateJWTTemplateBodyClaims]
        if isinstance(_claims, Unset):
            claims = UNSET
        else:
            claims = CreateJWTTemplateBodyClaims.from_dict(_claims)

        def _parse_lifetime(data: object) -> Union[None, Unset, float]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, float], data)

        lifetime = _parse_lifetime(d.pop("lifetime", UNSET))

        def _parse_allowed_clock_skew(data: object) -> Union[None, Unset, float]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, float], data)

        allowed_clock_skew = _parse_allowed_clock_skew(d.pop("allowed_clock_skew", UNSET))

        custom_signing_key = d.pop("custom_signing_key", UNSET)

        def _parse_signing_algorithm(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        signing_algorithm = _parse_signing_algorithm(d.pop("signing_algorithm", UNSET))

        def _parse_signing_key(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        signing_key = _parse_signing_key(d.pop("signing_key", UNSET))

        create_jwt_template_body = cls(
            name=name,
            claims=claims,
            lifetime=lifetime,
            allowed_clock_skew=allowed_clock_skew,
            custom_signing_key=custom_signing_key,
            signing_algorithm=signing_algorithm,
            signing_key=signing_key,
        )

        create_jwt_template_body.additional_properties = d
        return create_jwt_template_body

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
