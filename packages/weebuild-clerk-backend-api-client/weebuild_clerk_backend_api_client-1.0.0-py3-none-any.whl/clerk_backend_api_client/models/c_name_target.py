from typing import Any, Dict, Type, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="CNameTarget")


@_attrs_define
class CNameTarget:
    """
    Attributes:
        host (str):
        value (str):
        required (bool): Denotes whether this CNAME target is required to be set in order for the domain to be
            considered deployed.
    """

    host: str
    value: str
    required: bool

    def to_dict(self) -> Dict[str, Any]:
        host = self.host

        value = self.value

        required = self.required

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "host": host,
                "value": value,
                "required": required,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        host = d.pop("host")

        value = d.pop("value")

        required = d.pop("required")

        c_name_target = cls(
            host=host,
            value=value,
            required=required,
        )

        return c_name_target
