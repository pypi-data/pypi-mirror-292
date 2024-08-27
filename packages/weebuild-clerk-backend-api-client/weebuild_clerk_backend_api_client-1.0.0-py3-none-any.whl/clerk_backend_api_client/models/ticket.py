from typing import Any, Dict, Type, TypeVar, Union, cast

from attrs import define as _attrs_define

from ..models.ticket_status import TicketStatus
from ..models.ticket_strategy import TicketStrategy
from ..types import UNSET, Unset

T = TypeVar("T", bound="Ticket")


@_attrs_define
class Ticket:
    """
    Attributes:
        status (TicketStatus):
        strategy (TicketStrategy):
        attempts (Union[None, Unset, int]):
        expire_at (Union[None, Unset, int]):
    """

    status: TicketStatus
    strategy: TicketStrategy
    attempts: Union[None, Unset, int] = UNSET
    expire_at: Union[None, Unset, int] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        status = self.status.value

        strategy = self.strategy.value

        attempts: Union[None, Unset, int]
        if isinstance(self.attempts, Unset):
            attempts = UNSET
        else:
            attempts = self.attempts

        expire_at: Union[None, Unset, int]
        if isinstance(self.expire_at, Unset):
            expire_at = UNSET
        else:
            expire_at = self.expire_at

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "status": status,
                "strategy": strategy,
            }
        )
        if attempts is not UNSET:
            field_dict["attempts"] = attempts
        if expire_at is not UNSET:
            field_dict["expire_at"] = expire_at

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        status = TicketStatus(d.pop("status"))

        strategy = TicketStrategy(d.pop("strategy"))

        def _parse_attempts(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        attempts = _parse_attempts(d.pop("attempts", UNSET))

        def _parse_expire_at(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        expire_at = _parse_expire_at(d.pop("expire_at", UNSET))

        ticket = cls(
            status=status,
            strategy=strategy,
            attempts=attempts,
            expire_at=expire_at,
        )

        return ticket
