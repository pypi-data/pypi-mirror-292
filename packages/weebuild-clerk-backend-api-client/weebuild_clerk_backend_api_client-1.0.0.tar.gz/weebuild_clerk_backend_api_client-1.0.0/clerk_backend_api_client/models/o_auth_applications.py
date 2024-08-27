from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.o_auth_application import OAuthApplication


T = TypeVar("T", bound="OAuthApplications")


@_attrs_define
class OAuthApplications:
    """
    Attributes:
        data (List['OAuthApplication']):
        total_count (int): Total number of OAuth applications
    """

    data: List["OAuthApplication"]
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
        from ..models.o_auth_application import OAuthApplication

        d = src_dict.copy()
        data = []
        _data = d.pop("data")
        for data_item_data in _data:
            data_item = OAuthApplication.from_dict(data_item_data)

            data.append(data_item)

        total_count = d.pop("total_count")

        o_auth_applications = cls(
            data=data,
            total_count=total_count,
        )

        return o_auth_applications
