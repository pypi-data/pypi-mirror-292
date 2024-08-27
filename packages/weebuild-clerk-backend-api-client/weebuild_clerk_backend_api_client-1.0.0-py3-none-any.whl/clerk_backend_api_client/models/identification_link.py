from typing import Any, Dict, Type, TypeVar

from attrs import define as _attrs_define

from ..models.identification_link_type import IdentificationLinkType

T = TypeVar("T", bound="IdentificationLink")


@_attrs_define
class IdentificationLink:
    """
    Attributes:
        type (IdentificationLinkType):
        id (str):
    """

    type: IdentificationLinkType
    id: str

    def to_dict(self) -> Dict[str, Any]:
        type = self.type.value

        id = self.id

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "type": type,
                "id": id,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        type = IdentificationLinkType(d.pop("type"))

        id = d.pop("id")

        identification_link = cls(
            type=type,
            id=id,
        )

        return identification_link
