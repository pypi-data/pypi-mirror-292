from typing import Any, Dict, Type, TypeVar, Union, cast

from attrs import define as _attrs_define

from ..models.passkey_nonce import PasskeyNonce
from ..models.passkey_status import PasskeyStatus
from ..models.passkey_strategy import PasskeyStrategy
from ..types import UNSET, Unset

T = TypeVar("T", bound="Passkey")


@_attrs_define
class Passkey:
    """
    Attributes:
        status (PasskeyStatus):
        strategy (PasskeyStrategy):
        nonce (Union[Unset, PasskeyNonce]):
        attempts (Union[None, Unset, int]):
        expire_at (Union[None, Unset, int]):
    """

    status: PasskeyStatus
    strategy: PasskeyStrategy
    nonce: Union[Unset, PasskeyNonce] = UNSET
    attempts: Union[None, Unset, int] = UNSET
    expire_at: Union[None, Unset, int] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        status = self.status.value

        strategy = self.strategy.value

        nonce: Union[Unset, str] = UNSET
        if not isinstance(self.nonce, Unset):
            nonce = self.nonce.value

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
        if nonce is not UNSET:
            field_dict["nonce"] = nonce
        if attempts is not UNSET:
            field_dict["attempts"] = attempts
        if expire_at is not UNSET:
            field_dict["expire_at"] = expire_at

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        status = PasskeyStatus(d.pop("status"))

        strategy = PasskeyStrategy(d.pop("strategy"))

        _nonce = d.pop("nonce", UNSET)
        nonce: Union[Unset, PasskeyNonce]
        if isinstance(_nonce, Unset):
            nonce = UNSET
        else:
            nonce = PasskeyNonce(_nonce)

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

        passkey = cls(
            status=status,
            strategy=strategy,
            nonce=nonce,
            attempts=attempts,
            expire_at=expire_at,
        )

        return passkey
