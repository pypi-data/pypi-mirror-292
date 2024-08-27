from typing import TYPE_CHECKING, Any, Dict, Type, TypeVar, Union, cast

from attrs import define as _attrs_define

from ..models.saml_status import SAMLStatus
from ..models.saml_strategy import SAMLStrategy
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.clerk_error import ClerkError


T = TypeVar("T", bound="SAML")


@_attrs_define
class SAML:
    """
    Attributes:
        status (SAMLStatus):
        strategy (SAMLStrategy):
        external_verification_redirect_url (Union[None, str]):
        expire_at (int):
        error (Union[Unset, ClerkError]):
        attempts (Union[None, Unset, int]):
    """

    status: SAMLStatus
    strategy: SAMLStrategy
    external_verification_redirect_url: Union[None, str]
    expire_at: int
    error: Union[Unset, "ClerkError"] = UNSET
    attempts: Union[None, Unset, int] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        status = self.status.value

        strategy = self.strategy.value

        external_verification_redirect_url: Union[None, str]
        external_verification_redirect_url = self.external_verification_redirect_url

        expire_at = self.expire_at

        error: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.error, Unset):
            error = self.error.to_dict()

        attempts: Union[None, Unset, int]
        if isinstance(self.attempts, Unset):
            attempts = UNSET
        else:
            attempts = self.attempts

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "status": status,
                "strategy": strategy,
                "external_verification_redirect_url": external_verification_redirect_url,
                "expire_at": expire_at,
            }
        )
        if error is not UNSET:
            field_dict["error"] = error
        if attempts is not UNSET:
            field_dict["attempts"] = attempts

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.clerk_error import ClerkError

        d = src_dict.copy()
        status = SAMLStatus(d.pop("status"))

        strategy = SAMLStrategy(d.pop("strategy"))

        def _parse_external_verification_redirect_url(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        external_verification_redirect_url = _parse_external_verification_redirect_url(
            d.pop("external_verification_redirect_url")
        )

        expire_at = d.pop("expire_at")

        _error = d.pop("error", UNSET)
        error: Union[Unset, ClerkError]
        if isinstance(_error, Unset):
            error = UNSET
        else:
            error = ClerkError.from_dict(_error)

        def _parse_attempts(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        attempts = _parse_attempts(d.pop("attempts", UNSET))

        saml = cls(
            status=status,
            strategy=strategy,
            external_verification_redirect_url=external_verification_redirect_url,
            expire_at=expire_at,
            error=error,
            attempts=attempts,
        )

        return saml
