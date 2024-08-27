from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define

from ..models.sign_up_object import SignUpObject
from ..models.sign_up_status import SignUpStatus
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.sign_up_external_account import SignUpExternalAccount
    from ..models.sign_up_public_metadata import SignUpPublicMetadata
    from ..models.sign_up_unsafe_metadata import SignUpUnsafeMetadata
    from ..models.sign_up_verifications import SignUpVerifications


T = TypeVar("T", bound="SignUp")


@_attrs_define
class SignUp:
    """
    Attributes:
        object_ (SignUpObject):
        id (str):
        status (SignUpStatus):
        password_enabled (bool):
        custom_action (bool):
        abandon_at (int):
        required_fields (Union[Unset, List[str]]):
        optional_fields (Union[Unset, List[str]]):
        missing_fields (Union[Unset, List[str]]):
        unverified_fields (Union[Unset, List[str]]):
        verifications (Union[Unset, SignUpVerifications]):
        username (Union[None, Unset, str]):
        email_address (Union[None, Unset, str]):
        phone_number (Union[None, Unset, str]):
        web3_wallet (Union[None, Unset, str]):
        first_name (Union[None, Unset, str]):
        last_name (Union[None, Unset, str]):
        unsafe_metadata (Union[Unset, SignUpUnsafeMetadata]):
        public_metadata (Union[Unset, SignUpPublicMetadata]):
        external_id (Union[None, Unset, str]):
        created_session_id (Union[None, Unset, str]):
        created_user_id (Union[None, Unset, str]):
        external_account (Union[Unset, SignUpExternalAccount]):
    """

    object_: SignUpObject
    id: str
    status: SignUpStatus
    password_enabled: bool
    custom_action: bool
    abandon_at: int
    required_fields: Union[Unset, List[str]] = UNSET
    optional_fields: Union[Unset, List[str]] = UNSET
    missing_fields: Union[Unset, List[str]] = UNSET
    unverified_fields: Union[Unset, List[str]] = UNSET
    verifications: Union[Unset, "SignUpVerifications"] = UNSET
    username: Union[None, Unset, str] = UNSET
    email_address: Union[None, Unset, str] = UNSET
    phone_number: Union[None, Unset, str] = UNSET
    web3_wallet: Union[None, Unset, str] = UNSET
    first_name: Union[None, Unset, str] = UNSET
    last_name: Union[None, Unset, str] = UNSET
    unsafe_metadata: Union[Unset, "SignUpUnsafeMetadata"] = UNSET
    public_metadata: Union[Unset, "SignUpPublicMetadata"] = UNSET
    external_id: Union[None, Unset, str] = UNSET
    created_session_id: Union[None, Unset, str] = UNSET
    created_user_id: Union[None, Unset, str] = UNSET
    external_account: Union[Unset, "SignUpExternalAccount"] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        object_ = self.object_.value

        id = self.id

        status = self.status.value

        password_enabled = self.password_enabled

        custom_action = self.custom_action

        abandon_at = self.abandon_at

        required_fields: Union[Unset, List[str]] = UNSET
        if not isinstance(self.required_fields, Unset):
            required_fields = self.required_fields

        optional_fields: Union[Unset, List[str]] = UNSET
        if not isinstance(self.optional_fields, Unset):
            optional_fields = self.optional_fields

        missing_fields: Union[Unset, List[str]] = UNSET
        if not isinstance(self.missing_fields, Unset):
            missing_fields = self.missing_fields

        unverified_fields: Union[Unset, List[str]] = UNSET
        if not isinstance(self.unverified_fields, Unset):
            unverified_fields = self.unverified_fields

        verifications: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.verifications, Unset):
            verifications = self.verifications.to_dict()

        username: Union[None, Unset, str]
        if isinstance(self.username, Unset):
            username = UNSET
        else:
            username = self.username

        email_address: Union[None, Unset, str]
        if isinstance(self.email_address, Unset):
            email_address = UNSET
        else:
            email_address = self.email_address

        phone_number: Union[None, Unset, str]
        if isinstance(self.phone_number, Unset):
            phone_number = UNSET
        else:
            phone_number = self.phone_number

        web3_wallet: Union[None, Unset, str]
        if isinstance(self.web3_wallet, Unset):
            web3_wallet = UNSET
        else:
            web3_wallet = self.web3_wallet

        first_name: Union[None, Unset, str]
        if isinstance(self.first_name, Unset):
            first_name = UNSET
        else:
            first_name = self.first_name

        last_name: Union[None, Unset, str]
        if isinstance(self.last_name, Unset):
            last_name = UNSET
        else:
            last_name = self.last_name

        unsafe_metadata: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.unsafe_metadata, Unset):
            unsafe_metadata = self.unsafe_metadata.to_dict()

        public_metadata: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.public_metadata, Unset):
            public_metadata = self.public_metadata.to_dict()

        external_id: Union[None, Unset, str]
        if isinstance(self.external_id, Unset):
            external_id = UNSET
        else:
            external_id = self.external_id

        created_session_id: Union[None, Unset, str]
        if isinstance(self.created_session_id, Unset):
            created_session_id = UNSET
        else:
            created_session_id = self.created_session_id

        created_user_id: Union[None, Unset, str]
        if isinstance(self.created_user_id, Unset):
            created_user_id = UNSET
        else:
            created_user_id = self.created_user_id

        external_account: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.external_account, Unset):
            external_account = self.external_account.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "object": object_,
                "id": id,
                "status": status,
                "password_enabled": password_enabled,
                "custom_action": custom_action,
                "abandon_at": abandon_at,
            }
        )
        if required_fields is not UNSET:
            field_dict["required_fields"] = required_fields
        if optional_fields is not UNSET:
            field_dict["optional_fields"] = optional_fields
        if missing_fields is not UNSET:
            field_dict["missing_fields"] = missing_fields
        if unverified_fields is not UNSET:
            field_dict["unverified_fields"] = unverified_fields
        if verifications is not UNSET:
            field_dict["verifications"] = verifications
        if username is not UNSET:
            field_dict["username"] = username
        if email_address is not UNSET:
            field_dict["email_address"] = email_address
        if phone_number is not UNSET:
            field_dict["phone_number"] = phone_number
        if web3_wallet is not UNSET:
            field_dict["web3_wallet"] = web3_wallet
        if first_name is not UNSET:
            field_dict["first_name"] = first_name
        if last_name is not UNSET:
            field_dict["last_name"] = last_name
        if unsafe_metadata is not UNSET:
            field_dict["unsafe_metadata"] = unsafe_metadata
        if public_metadata is not UNSET:
            field_dict["public_metadata"] = public_metadata
        if external_id is not UNSET:
            field_dict["external_id"] = external_id
        if created_session_id is not UNSET:
            field_dict["created_session_id"] = created_session_id
        if created_user_id is not UNSET:
            field_dict["created_user_id"] = created_user_id
        if external_account is not UNSET:
            field_dict["external_account"] = external_account

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.sign_up_external_account import SignUpExternalAccount
        from ..models.sign_up_public_metadata import SignUpPublicMetadata
        from ..models.sign_up_unsafe_metadata import SignUpUnsafeMetadata
        from ..models.sign_up_verifications import SignUpVerifications

        d = src_dict.copy()
        object_ = SignUpObject(d.pop("object"))

        id = d.pop("id")

        status = SignUpStatus(d.pop("status"))

        password_enabled = d.pop("password_enabled")

        custom_action = d.pop("custom_action")

        abandon_at = d.pop("abandon_at")

        required_fields = cast(List[str], d.pop("required_fields", UNSET))

        optional_fields = cast(List[str], d.pop("optional_fields", UNSET))

        missing_fields = cast(List[str], d.pop("missing_fields", UNSET))

        unverified_fields = cast(List[str], d.pop("unverified_fields", UNSET))

        _verifications = d.pop("verifications", UNSET)
        verifications: Union[Unset, SignUpVerifications]
        if isinstance(_verifications, Unset):
            verifications = UNSET
        else:
            verifications = SignUpVerifications.from_dict(_verifications)

        def _parse_username(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        username = _parse_username(d.pop("username", UNSET))

        def _parse_email_address(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        email_address = _parse_email_address(d.pop("email_address", UNSET))

        def _parse_phone_number(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        phone_number = _parse_phone_number(d.pop("phone_number", UNSET))

        def _parse_web3_wallet(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        web3_wallet = _parse_web3_wallet(d.pop("web3_wallet", UNSET))

        def _parse_first_name(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        first_name = _parse_first_name(d.pop("first_name", UNSET))

        def _parse_last_name(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        last_name = _parse_last_name(d.pop("last_name", UNSET))

        _unsafe_metadata = d.pop("unsafe_metadata", UNSET)
        unsafe_metadata: Union[Unset, SignUpUnsafeMetadata]
        if isinstance(_unsafe_metadata, Unset):
            unsafe_metadata = UNSET
        else:
            unsafe_metadata = SignUpUnsafeMetadata.from_dict(_unsafe_metadata)

        _public_metadata = d.pop("public_metadata", UNSET)
        public_metadata: Union[Unset, SignUpPublicMetadata]
        if isinstance(_public_metadata, Unset):
            public_metadata = UNSET
        else:
            public_metadata = SignUpPublicMetadata.from_dict(_public_metadata)

        def _parse_external_id(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        external_id = _parse_external_id(d.pop("external_id", UNSET))

        def _parse_created_session_id(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        created_session_id = _parse_created_session_id(d.pop("created_session_id", UNSET))

        def _parse_created_user_id(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        created_user_id = _parse_created_user_id(d.pop("created_user_id", UNSET))

        _external_account = d.pop("external_account", UNSET)
        external_account: Union[Unset, SignUpExternalAccount]
        if isinstance(_external_account, Unset):
            external_account = UNSET
        else:
            external_account = SignUpExternalAccount.from_dict(_external_account)

        sign_up = cls(
            object_=object_,
            id=id,
            status=status,
            password_enabled=password_enabled,
            custom_action=custom_action,
            abandon_at=abandon_at,
            required_fields=required_fields,
            optional_fields=optional_fields,
            missing_fields=missing_fields,
            unverified_fields=unverified_fields,
            verifications=verifications,
            username=username,
            email_address=email_address,
            phone_number=phone_number,
            web3_wallet=web3_wallet,
            first_name=first_name,
            last_name=last_name,
            unsafe_metadata=unsafe_metadata,
            public_metadata=public_metadata,
            external_id=external_id,
            created_session_id=created_session_id,
            created_user_id=created_user_id,
            external_account=external_account,
        )

        return sign_up
