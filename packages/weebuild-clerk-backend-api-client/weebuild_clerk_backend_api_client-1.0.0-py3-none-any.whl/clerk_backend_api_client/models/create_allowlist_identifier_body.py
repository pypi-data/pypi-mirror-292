from typing import Any, Dict, Type, TypeVar, Union

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="CreateAllowlistIdentifierBody")


@_attrs_define
class CreateAllowlistIdentifierBody:
    """
    Attributes:
        identifier (str): The identifier to be added in the allow-list.
            This can be an email address, a phone number or a web3 wallet.
        notify (Union[Unset, bool]): This flag denotes whether the given identifier will receive an invitation to join
            the application.
            Note that this only works for email address and phone number identifiers. Default: False.
    """

    identifier: str
    notify: Union[Unset, bool] = False

    def to_dict(self) -> Dict[str, Any]:
        identifier = self.identifier

        notify = self.notify

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "identifier": identifier,
            }
        )
        if notify is not UNSET:
            field_dict["notify"] = notify

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        identifier = d.pop("identifier")

        notify = d.pop("notify", UNSET)

        create_allowlist_identifier_body = cls(
            identifier=identifier,
            notify=notify,
        )

        return create_allowlist_identifier_body
