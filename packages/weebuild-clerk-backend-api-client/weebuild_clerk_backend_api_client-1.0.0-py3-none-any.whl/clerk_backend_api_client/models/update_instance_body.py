from typing import Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="UpdateInstanceBody")


@_attrs_define
class UpdateInstanceBody:
    """
    Attributes:
        test_mode (Union[None, Unset, bool]): Toggles test mode for this instance, allowing the use of test email
            addresses and phone numbers.
            Defaults to true for development instances.
        hibp (Union[None, Unset, bool]): Whether the instance should be using the HIBP service to check passwords for
            breaches
        enhanced_email_deliverability (Union[None, Unset, bool]): The "enhanced_email_deliverability" feature will send
            emails from "verifications@clerk.dev" instead of your domain.
            This can be helpful if you do not have a high domain reputation.
        support_email (Union[None, Unset, str]):
        clerk_js_version (Union[None, Unset, str]):
        development_origin (Union[None, Unset, str]):
        allowed_origins (Union[Unset, List[str]]): For browser-like stacks such as browser extensions, Electron, or
            Capacitor.js the instance allowed origins need to be updated with the request origin value.
            For Chrome extensions popup, background, or service worker pages the origin is chrome-
            extension://extension_uiid. For Electron apps the default origin is http://localhost:3000. For Capacitor, the
            origin is capacitor://localhost.
        cookieless_dev (Union[Unset, bool]): Whether the instance should operate in cookieless development mode (i.e.
            without third-party cookies).
            Deprecated: Please use `url_based_session_syncing` instead.
        url_based_session_syncing (Union[Unset, bool]): Whether the instance should use URL-based session syncing in
            development mode (i.e. without third-party cookies).
    """

    test_mode: Union[None, Unset, bool] = UNSET
    hibp: Union[None, Unset, bool] = UNSET
    enhanced_email_deliverability: Union[None, Unset, bool] = UNSET
    support_email: Union[None, Unset, str] = UNSET
    clerk_js_version: Union[None, Unset, str] = UNSET
    development_origin: Union[None, Unset, str] = UNSET
    allowed_origins: Union[Unset, List[str]] = UNSET
    cookieless_dev: Union[Unset, bool] = UNSET
    url_based_session_syncing: Union[Unset, bool] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        test_mode: Union[None, Unset, bool]
        if isinstance(self.test_mode, Unset):
            test_mode = UNSET
        else:
            test_mode = self.test_mode

        hibp: Union[None, Unset, bool]
        if isinstance(self.hibp, Unset):
            hibp = UNSET
        else:
            hibp = self.hibp

        enhanced_email_deliverability: Union[None, Unset, bool]
        if isinstance(self.enhanced_email_deliverability, Unset):
            enhanced_email_deliverability = UNSET
        else:
            enhanced_email_deliverability = self.enhanced_email_deliverability

        support_email: Union[None, Unset, str]
        if isinstance(self.support_email, Unset):
            support_email = UNSET
        else:
            support_email = self.support_email

        clerk_js_version: Union[None, Unset, str]
        if isinstance(self.clerk_js_version, Unset):
            clerk_js_version = UNSET
        else:
            clerk_js_version = self.clerk_js_version

        development_origin: Union[None, Unset, str]
        if isinstance(self.development_origin, Unset):
            development_origin = UNSET
        else:
            development_origin = self.development_origin

        allowed_origins: Union[Unset, List[str]] = UNSET
        if not isinstance(self.allowed_origins, Unset):
            allowed_origins = self.allowed_origins

        cookieless_dev = self.cookieless_dev

        url_based_session_syncing = self.url_based_session_syncing

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if test_mode is not UNSET:
            field_dict["test_mode"] = test_mode
        if hibp is not UNSET:
            field_dict["hibp"] = hibp
        if enhanced_email_deliverability is not UNSET:
            field_dict["enhanced_email_deliverability"] = enhanced_email_deliverability
        if support_email is not UNSET:
            field_dict["support_email"] = support_email
        if clerk_js_version is not UNSET:
            field_dict["clerk_js_version"] = clerk_js_version
        if development_origin is not UNSET:
            field_dict["development_origin"] = development_origin
        if allowed_origins is not UNSET:
            field_dict["allowed_origins"] = allowed_origins
        if cookieless_dev is not UNSET:
            field_dict["cookieless_dev"] = cookieless_dev
        if url_based_session_syncing is not UNSET:
            field_dict["url_based_session_syncing"] = url_based_session_syncing

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def _parse_test_mode(data: object) -> Union[None, Unset, bool]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, bool], data)

        test_mode = _parse_test_mode(d.pop("test_mode", UNSET))

        def _parse_hibp(data: object) -> Union[None, Unset, bool]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, bool], data)

        hibp = _parse_hibp(d.pop("hibp", UNSET))

        def _parse_enhanced_email_deliverability(data: object) -> Union[None, Unset, bool]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, bool], data)

        enhanced_email_deliverability = _parse_enhanced_email_deliverability(
            d.pop("enhanced_email_deliverability", UNSET)
        )

        def _parse_support_email(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        support_email = _parse_support_email(d.pop("support_email", UNSET))

        def _parse_clerk_js_version(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        clerk_js_version = _parse_clerk_js_version(d.pop("clerk_js_version", UNSET))

        def _parse_development_origin(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        development_origin = _parse_development_origin(d.pop("development_origin", UNSET))

        allowed_origins = cast(List[str], d.pop("allowed_origins", UNSET))

        cookieless_dev = d.pop("cookieless_dev", UNSET)

        url_based_session_syncing = d.pop("url_based_session_syncing", UNSET)

        update_instance_body = cls(
            test_mode=test_mode,
            hibp=hibp,
            enhanced_email_deliverability=enhanced_email_deliverability,
            support_email=support_email,
            clerk_js_version=clerk_js_version,
            development_origin=development_origin,
            allowed_origins=allowed_origins,
            cookieless_dev=cookieless_dev,
            url_based_session_syncing=url_based_session_syncing,
        )

        return update_instance_body
