from typing import Any, Dict, Type, TypeVar, Union, cast

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="UpdateInstanceAuthConfigBody")


@_attrs_define
class UpdateInstanceAuthConfigBody:
    """
    Attributes:
        restricted_to_allowlist (Union[None, Unset, bool]): Whether sign up is restricted to email addresses, phone
            numbers and usernames that are on the allowlist. Default: False.
        from_email_address (Union[None, Unset, str]): The local part of the email address from which authentication-
            related emails (e.g. OTP code, magic links) will be sent.
            Only alphanumeric values are allowed.
            Note that this value should contain only the local part of the address (e.g. `foo` for `foo@example.com`).
        progressive_sign_up (Union[None, Unset, bool]): Enable the Progressive Sign Up algorithm. Refer to the
            [docs](https://clerk.com/docs/upgrade-guides/progressive-sign-up) for more info.
        session_token_template (Union[None, Unset, str]): The name of the JWT Template used to augment your session
            tokens. To disable this, pass an empty string.
        enhanced_email_deliverability (Union[None, Unset, bool]): The "enhanced_email_deliverability" feature will send
            emails from "verifications@clerk.dev" instead of your domain.
            This can be helpful if you do not have a high domain reputation.
        test_mode (Union[None, Unset, bool]): Toggles test mode for this instance, allowing the use of test email
            addresses and phone numbers.
            Defaults to true for development instances.
    """

    restricted_to_allowlist: Union[None, Unset, bool] = False
    from_email_address: Union[None, Unset, str] = UNSET
    progressive_sign_up: Union[None, Unset, bool] = UNSET
    session_token_template: Union[None, Unset, str] = UNSET
    enhanced_email_deliverability: Union[None, Unset, bool] = UNSET
    test_mode: Union[None, Unset, bool] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        restricted_to_allowlist: Union[None, Unset, bool]
        if isinstance(self.restricted_to_allowlist, Unset):
            restricted_to_allowlist = UNSET
        else:
            restricted_to_allowlist = self.restricted_to_allowlist

        from_email_address: Union[None, Unset, str]
        if isinstance(self.from_email_address, Unset):
            from_email_address = UNSET
        else:
            from_email_address = self.from_email_address

        progressive_sign_up: Union[None, Unset, bool]
        if isinstance(self.progressive_sign_up, Unset):
            progressive_sign_up = UNSET
        else:
            progressive_sign_up = self.progressive_sign_up

        session_token_template: Union[None, Unset, str]
        if isinstance(self.session_token_template, Unset):
            session_token_template = UNSET
        else:
            session_token_template = self.session_token_template

        enhanced_email_deliverability: Union[None, Unset, bool]
        if isinstance(self.enhanced_email_deliverability, Unset):
            enhanced_email_deliverability = UNSET
        else:
            enhanced_email_deliverability = self.enhanced_email_deliverability

        test_mode: Union[None, Unset, bool]
        if isinstance(self.test_mode, Unset):
            test_mode = UNSET
        else:
            test_mode = self.test_mode

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if restricted_to_allowlist is not UNSET:
            field_dict["restricted_to_allowlist"] = restricted_to_allowlist
        if from_email_address is not UNSET:
            field_dict["from_email_address"] = from_email_address
        if progressive_sign_up is not UNSET:
            field_dict["progressive_sign_up"] = progressive_sign_up
        if session_token_template is not UNSET:
            field_dict["session_token_template"] = session_token_template
        if enhanced_email_deliverability is not UNSET:
            field_dict["enhanced_email_deliverability"] = enhanced_email_deliverability
        if test_mode is not UNSET:
            field_dict["test_mode"] = test_mode

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def _parse_restricted_to_allowlist(data: object) -> Union[None, Unset, bool]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, bool], data)

        restricted_to_allowlist = _parse_restricted_to_allowlist(d.pop("restricted_to_allowlist", UNSET))

        def _parse_from_email_address(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        from_email_address = _parse_from_email_address(d.pop("from_email_address", UNSET))

        def _parse_progressive_sign_up(data: object) -> Union[None, Unset, bool]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, bool], data)

        progressive_sign_up = _parse_progressive_sign_up(d.pop("progressive_sign_up", UNSET))

        def _parse_session_token_template(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        session_token_template = _parse_session_token_template(d.pop("session_token_template", UNSET))

        def _parse_enhanced_email_deliverability(data: object) -> Union[None, Unset, bool]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, bool], data)

        enhanced_email_deliverability = _parse_enhanced_email_deliverability(
            d.pop("enhanced_email_deliverability", UNSET)
        )

        def _parse_test_mode(data: object) -> Union[None, Unset, bool]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, bool], data)

        test_mode = _parse_test_mode(d.pop("test_mode", UNSET))

        update_instance_auth_config_body = cls(
            restricted_to_allowlist=restricted_to_allowlist,
            from_email_address=from_email_address,
            progressive_sign_up=progressive_sign_up,
            session_token_template=session_token_template,
            enhanced_email_deliverability=enhanced_email_deliverability,
            test_mode=test_mode,
        )

        return update_instance_auth_config_body
