from typing import Any, Dict, Type, TypeVar

from attrs import define as _attrs_define

from ..models.otp_status import OTPStatus
from ..models.otp_strategy import OTPStrategy

T = TypeVar("T", bound="OTP")


@_attrs_define
class OTP:
    """
    Attributes:
        status (OTPStatus):
        strategy (OTPStrategy):
        attempts (int):
        expire_at (int):
    """

    status: OTPStatus
    strategy: OTPStrategy
    attempts: int
    expire_at: int

    def to_dict(self) -> Dict[str, Any]:
        status = self.status.value

        strategy = self.strategy.value

        attempts = self.attempts

        expire_at = self.expire_at

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "status": status,
                "strategy": strategy,
                "attempts": attempts,
                "expire_at": expire_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        status = OTPStatus(d.pop("status"))

        strategy = OTPStrategy(d.pop("strategy"))

        attempts = d.pop("attempts")

        expire_at = d.pop("expire_at")

        otp = cls(
            status=status,
            strategy=strategy,
            attempts=attempts,
            expire_at=expire_at,
        )

        return otp
