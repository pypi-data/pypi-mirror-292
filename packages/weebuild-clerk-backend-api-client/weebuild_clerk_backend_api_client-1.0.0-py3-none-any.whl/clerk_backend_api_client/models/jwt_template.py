from typing import TYPE_CHECKING, Any, Dict, Type, TypeVar, Union

from attrs import define as _attrs_define

from ..models.jwt_template_object import JWTTemplateObject
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.jwt_template_claims import JWTTemplateClaims


T = TypeVar("T", bound="JWTTemplate")


@_attrs_define
class JWTTemplate:
    """
    Attributes:
        object_ (JWTTemplateObject):
        id (str):
        name (str):
        claims (JWTTemplateClaims):
        lifetime (int):
        allowed_clock_skew (int):
        created_at (int): Unix timestamp of creation.
        updated_at (int): Unix timestamp of last update.
        custom_signing_key (Union[Unset, bool]):
        signing_algorithm (Union[Unset, str]):
    """

    object_: JWTTemplateObject
    id: str
    name: str
    claims: "JWTTemplateClaims"
    lifetime: int
    allowed_clock_skew: int
    created_at: int
    updated_at: int
    custom_signing_key: Union[Unset, bool] = UNSET
    signing_algorithm: Union[Unset, str] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        object_ = self.object_.value

        id = self.id

        name = self.name

        claims = self.claims.to_dict()

        lifetime = self.lifetime

        allowed_clock_skew = self.allowed_clock_skew

        created_at = self.created_at

        updated_at = self.updated_at

        custom_signing_key = self.custom_signing_key

        signing_algorithm = self.signing_algorithm

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "object": object_,
                "id": id,
                "name": name,
                "claims": claims,
                "lifetime": lifetime,
                "allowed_clock_skew": allowed_clock_skew,
                "created_at": created_at,
                "updated_at": updated_at,
            }
        )
        if custom_signing_key is not UNSET:
            field_dict["custom_signing_key"] = custom_signing_key
        if signing_algorithm is not UNSET:
            field_dict["signing_algorithm"] = signing_algorithm

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.jwt_template_claims import JWTTemplateClaims

        d = src_dict.copy()
        object_ = JWTTemplateObject(d.pop("object"))

        id = d.pop("id")

        name = d.pop("name")

        claims = JWTTemplateClaims.from_dict(d.pop("claims"))

        lifetime = d.pop("lifetime")

        allowed_clock_skew = d.pop("allowed_clock_skew")

        created_at = d.pop("created_at")

        updated_at = d.pop("updated_at")

        custom_signing_key = d.pop("custom_signing_key", UNSET)

        signing_algorithm = d.pop("signing_algorithm", UNSET)

        jwt_template = cls(
            object_=object_,
            id=id,
            name=name,
            claims=claims,
            lifetime=lifetime,
            allowed_clock_skew=allowed_clock_skew,
            created_at=created_at,
            updated_at=updated_at,
            custom_signing_key=custom_signing_key,
            signing_algorithm=signing_algorithm,
        )

        return jwt_template
