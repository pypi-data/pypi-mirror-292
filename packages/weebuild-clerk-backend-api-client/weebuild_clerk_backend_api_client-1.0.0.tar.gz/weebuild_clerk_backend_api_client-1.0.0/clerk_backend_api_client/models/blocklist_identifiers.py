from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.blocklist_identifier import BlocklistIdentifier


T = TypeVar("T", bound="BlocklistIdentifiers")


@_attrs_define
class BlocklistIdentifiers:
    """
    Attributes:
        data (List['BlocklistIdentifier']):
        total_count (int): Total number of blocklist identifiers
    """

    data: List["BlocklistIdentifier"]
    total_count: int

    def to_dict(self) -> Dict[str, Any]:
        data = []
        for data_item_data in self.data:
            data_item = data_item_data.to_dict()
            data.append(data_item)

        total_count = self.total_count

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "data": data,
                "total_count": total_count,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.blocklist_identifier import BlocklistIdentifier

        d = src_dict.copy()
        data = []
        _data = d.pop("data")
        for data_item_data in _data:
            data_item = BlocklistIdentifier.from_dict(data_item_data)

            data.append(data_item)

        total_count = d.pop("total_count")

        blocklist_identifiers = cls(
            data=data,
            total_count=total_count,
        )

        return blocklist_identifiers
