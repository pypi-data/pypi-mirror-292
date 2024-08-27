from typing import Any, Dict, Type, TypeVar

from attrs import define as _attrs_define

from ..models.total_count_object import TotalCountObject

T = TypeVar("T", bound="TotalCount")


@_attrs_define
class TotalCount:
    """
    Attributes:
        object_ (TotalCountObject): String representing the object's type. Objects of the same type share the same
            value.
        total_count (int):
    """

    object_: TotalCountObject
    total_count: int

    def to_dict(self) -> Dict[str, Any]:
        object_ = self.object_.value

        total_count = self.total_count

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "object": object_,
                "total_count": total_count,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        object_ = TotalCountObject(d.pop("object"))

        total_count = d.pop("total_count")

        total_count = cls(
            object_=object_,
            total_count=total_count,
        )

        return total_count
