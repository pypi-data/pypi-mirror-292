from typing import TYPE_CHECKING, Any, Dict, Type, TypeVar, Union

from attrs import define as _attrs_define

from ..models.schemas_passkey_object import SchemasPasskeyObject
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.passkey import Passkey


T = TypeVar("T", bound="SchemasPasskey")


@_attrs_define
class SchemasPasskey:
    """
    Attributes:
        object_ (SchemasPasskeyObject): String representing the object's type. Objects of the same type share the same
            value.
        name (str):
        last_used_at (int): Unix timestamp of when the passkey was last used.
        verification (Passkey):
        id (Union[Unset, str]):
    """

    object_: SchemasPasskeyObject
    name: str
    last_used_at: int
    verification: "Passkey"
    id: Union[Unset, str] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        object_ = self.object_.value

        name = self.name

        last_used_at = self.last_used_at

        verification = self.verification.to_dict()

        id = self.id

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "object": object_,
                "name": name,
                "last_used_at": last_used_at,
                "verification": verification,
            }
        )
        if id is not UNSET:
            field_dict["id"] = id

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.passkey import Passkey

        d = src_dict.copy()
        object_ = SchemasPasskeyObject(d.pop("object"))

        name = d.pop("name")

        last_used_at = d.pop("last_used_at")

        verification = Passkey.from_dict(d.pop("verification"))

        id = d.pop("id", UNSET)

        schemas_passkey = cls(
            object_=object_,
            name=name,
            last_used_at=last_used_at,
            verification=verification,
            id=id,
        )

        return schemas_passkey
