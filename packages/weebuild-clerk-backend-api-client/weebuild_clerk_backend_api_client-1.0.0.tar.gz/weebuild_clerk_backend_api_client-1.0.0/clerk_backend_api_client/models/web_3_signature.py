from typing import Any, Dict, Type, TypeVar, Union, cast

from attrs import define as _attrs_define

from ..models.web_3_signature_status import Web3SignatureStatus
from ..models.web_3_signature_strategy import Web3SignatureStrategy
from ..types import UNSET, Unset

T = TypeVar("T", bound="Web3Signature")


@_attrs_define
class Web3Signature:
    """
    Attributes:
        status (Web3SignatureStatus):
        strategy (Web3SignatureStrategy):
        nonce (Union[None, Unset, str]):
        attempts (Union[None, Unset, int]):
        expire_at (Union[None, Unset, int]):
    """

    status: Web3SignatureStatus
    strategy: Web3SignatureStrategy
    nonce: Union[None, Unset, str] = UNSET
    attempts: Union[None, Unset, int] = UNSET
    expire_at: Union[None, Unset, int] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        status = self.status.value

        strategy = self.strategy.value

        nonce: Union[None, Unset, str]
        if isinstance(self.nonce, Unset):
            nonce = UNSET
        else:
            nonce = self.nonce

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
        status = Web3SignatureStatus(d.pop("status"))

        strategy = Web3SignatureStrategy(d.pop("strategy"))

        def _parse_nonce(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        nonce = _parse_nonce(d.pop("nonce", UNSET))

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

        web_3_signature = cls(
            status=status,
            strategy=strategy,
            nonce=nonce,
            attempts=attempts,
            expire_at=expire_at,
        )

        return web_3_signature
