from typing import Any, Dict, Type, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="CreateBlocklistIdentifierBody")


@_attrs_define
class CreateBlocklistIdentifierBody:
    """
    Attributes:
        identifier (str): The identifier to be added in the block-list.
            This can be an email address, a phone number or a web3 wallet.
    """

    identifier: str

    def to_dict(self) -> Dict[str, Any]:
        identifier = self.identifier

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "identifier": identifier,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        identifier = d.pop("identifier")

        create_blocklist_identifier_body = cls(
            identifier=identifier,
        )

        return create_blocklist_identifier_body
