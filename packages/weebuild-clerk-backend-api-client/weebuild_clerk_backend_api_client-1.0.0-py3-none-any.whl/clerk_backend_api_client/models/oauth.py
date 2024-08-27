from typing import TYPE_CHECKING, Any, Dict, Type, TypeVar, Union, cast

from attrs import define as _attrs_define

from ..models.oauth_status import OauthStatus
from ..models.oauth_strategy import OauthStrategy
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.clerk_error import ClerkError


T = TypeVar("T", bound="Oauth")


@_attrs_define
class Oauth:
    """
    Attributes:
        status (OauthStatus):
        strategy (OauthStrategy):
        expire_at (int):
        external_verification_redirect_url (Union[Unset, str]):
        error (Union[Unset, ClerkError]):
        attempts (Union[None, Unset, int]):
    """

    status: OauthStatus
    strategy: OauthStrategy
    expire_at: int
    external_verification_redirect_url: Union[Unset, str] = UNSET
    error: Union[Unset, "ClerkError"] = UNSET
    attempts: Union[None, Unset, int] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        status = self.status.value

        strategy = self.strategy.value

        expire_at = self.expire_at

        external_verification_redirect_url = self.external_verification_redirect_url

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
                "expire_at": expire_at,
            }
        )
        if external_verification_redirect_url is not UNSET:
            field_dict["external_verification_redirect_url"] = external_verification_redirect_url
        if error is not UNSET:
            field_dict["error"] = error
        if attempts is not UNSET:
            field_dict["attempts"] = attempts

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.clerk_error import ClerkError

        d = src_dict.copy()
        status = OauthStatus(d.pop("status"))

        strategy = OauthStrategy(d.pop("strategy"))

        expire_at = d.pop("expire_at")

        external_verification_redirect_url = d.pop("external_verification_redirect_url", UNSET)

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

        oauth = cls(
            status=status,
            strategy=strategy,
            expire_at=expire_at,
            external_verification_redirect_url=external_verification_redirect_url,
            error=error,
            attempts=attempts,
        )

        return oauth
