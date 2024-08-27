from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define

from ..models.user_object import UserObject
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.email_address import EmailAddress
    from ..models.phone_number import PhoneNumber
    from ..models.saml_account import SAMLAccount
    from ..models.schemas_passkey import SchemasPasskey
    from ..models.user_external_accounts_item import UserExternalAccountsItem
    from ..models.user_private_metadata_type_0 import UserPrivateMetadataType0
    from ..models.user_public_metadata import UserPublicMetadata
    from ..models.user_unsafe_metadata import UserUnsafeMetadata
    from ..models.web_3_wallet import Web3Wallet


T = TypeVar("T", bound="User")


@_attrs_define
class User:
    """
    Attributes:
        id (Union[Unset, str]):
        object_ (Union[Unset, UserObject]): String representing the object's type. Objects of the same type share the
            same value.
        external_id (Union[None, Unset, str]):
        primary_email_address_id (Union[None, Unset, str]):
        primary_phone_number_id (Union[None, Unset, str]):
        primary_web3_wallet_id (Union[None, Unset, str]):
        username (Union[None, Unset, str]):
        first_name (Union[None, Unset, str]):
        last_name (Union[None, Unset, str]):
        profile_image_url (Union[Unset, str]):
        image_url (Union[Unset, str]):
        has_image (Union[Unset, bool]):
        public_metadata (Union[Unset, UserPublicMetadata]):
        private_metadata (Union['UserPrivateMetadataType0', None, Unset]):
        unsafe_metadata (Union[Unset, UserUnsafeMetadata]):
        email_addresses (Union[Unset, List['EmailAddress']]):
        phone_numbers (Union[Unset, List['PhoneNumber']]):
        web3_wallets (Union[Unset, List['Web3Wallet']]):
        passkeys (Union[Unset, List['SchemasPasskey']]):
        password_enabled (Union[Unset, bool]):
        two_factor_enabled (Union[Unset, bool]):
        totp_enabled (Union[Unset, bool]):
        backup_code_enabled (Union[Unset, bool]):
        mfa_enabled_at (Union[None, Unset, int]): Unix timestamp of when MFA was last enabled for this user. It should
            be noted that this field is not nullified if MFA is disabled.
        mfa_disabled_at (Union[None, Unset, int]): Unix timestamp of when MFA was last disabled for this user. It should
            be noted that this field is not nullified if MFA is enabled again.
        external_accounts (Union[Unset, List['UserExternalAccountsItem']]):
        saml_accounts (Union[Unset, List['SAMLAccount']]):
        last_sign_in_at (Union[None, Unset, int]): Unix timestamp of last sign-in.
        banned (Union[Unset, bool]): Flag to denote whether user is banned or not.
        locked (Union[Unset, bool]): Flag to denote whether user is currently locked, i.e. restricted from signing in or
            not.
        lockout_expires_in_seconds (Union[None, Unset, int]): The number of seconds remaining until the lockout period
            expires for a locked user. A null value for a locked user indicates that lockout never expires.
        verification_attempts_remaining (Union[None, Unset, int]): The number of verification attempts remaining until
            the user is locked. Null if account lockout is not enabled. Note: if a user is locked explicitly via the Backend
            API, they may still have verification attempts remaining.
        updated_at (Union[Unset, int]): Unix timestamp of last update.
        created_at (Union[Unset, int]): Unix timestamp of creation.
        delete_self_enabled (Union[Unset, bool]): If enabled, user can delete themselves via FAPI.
        create_organization_enabled (Union[Unset, bool]): If enabled, user can create organizations via FAPI.
        create_organizations_limit (Union[None, Unset, int]): The maximum number of organizations the user can create. 0
            means unlimited.
        last_active_at (Union[None, Unset, int]): Unix timestamp of the latest session activity, with day precision.
             Example: 1700690400000.
    """

    id: Union[Unset, str] = UNSET
    object_: Union[Unset, UserObject] = UNSET
    external_id: Union[None, Unset, str] = UNSET
    primary_email_address_id: Union[None, Unset, str] = UNSET
    primary_phone_number_id: Union[None, Unset, str] = UNSET
    primary_web3_wallet_id: Union[None, Unset, str] = UNSET
    username: Union[None, Unset, str] = UNSET
    first_name: Union[None, Unset, str] = UNSET
    last_name: Union[None, Unset, str] = UNSET
    profile_image_url: Union[Unset, str] = UNSET
    image_url: Union[Unset, str] = UNSET
    has_image: Union[Unset, bool] = UNSET
    public_metadata: Union[Unset, "UserPublicMetadata"] = UNSET
    private_metadata: Union["UserPrivateMetadataType0", None, Unset] = UNSET
    unsafe_metadata: Union[Unset, "UserUnsafeMetadata"] = UNSET
    email_addresses: Union[Unset, List["EmailAddress"]] = UNSET
    phone_numbers: Union[Unset, List["PhoneNumber"]] = UNSET
    web3_wallets: Union[Unset, List["Web3Wallet"]] = UNSET
    passkeys: Union[Unset, List["SchemasPasskey"]] = UNSET
    password_enabled: Union[Unset, bool] = UNSET
    two_factor_enabled: Union[Unset, bool] = UNSET
    totp_enabled: Union[Unset, bool] = UNSET
    backup_code_enabled: Union[Unset, bool] = UNSET
    mfa_enabled_at: Union[None, Unset, int] = UNSET
    mfa_disabled_at: Union[None, Unset, int] = UNSET
    external_accounts: Union[Unset, List["UserExternalAccountsItem"]] = UNSET
    saml_accounts: Union[Unset, List["SAMLAccount"]] = UNSET
    last_sign_in_at: Union[None, Unset, int] = UNSET
    banned: Union[Unset, bool] = UNSET
    locked: Union[Unset, bool] = UNSET
    lockout_expires_in_seconds: Union[None, Unset, int] = UNSET
    verification_attempts_remaining: Union[None, Unset, int] = UNSET
    updated_at: Union[Unset, int] = UNSET
    created_at: Union[Unset, int] = UNSET
    delete_self_enabled: Union[Unset, bool] = UNSET
    create_organization_enabled: Union[Unset, bool] = UNSET
    create_organizations_limit: Union[None, Unset, int] = UNSET
    last_active_at: Union[None, Unset, int] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        from ..models.user_private_metadata_type_0 import UserPrivateMetadataType0

        id = self.id

        object_: Union[Unset, str] = UNSET
        if not isinstance(self.object_, Unset):
            object_ = self.object_.value

        external_id: Union[None, Unset, str]
        if isinstance(self.external_id, Unset):
            external_id = UNSET
        else:
            external_id = self.external_id

        primary_email_address_id: Union[None, Unset, str]
        if isinstance(self.primary_email_address_id, Unset):
            primary_email_address_id = UNSET
        else:
            primary_email_address_id = self.primary_email_address_id

        primary_phone_number_id: Union[None, Unset, str]
        if isinstance(self.primary_phone_number_id, Unset):
            primary_phone_number_id = UNSET
        else:
            primary_phone_number_id = self.primary_phone_number_id

        primary_web3_wallet_id: Union[None, Unset, str]
        if isinstance(self.primary_web3_wallet_id, Unset):
            primary_web3_wallet_id = UNSET
        else:
            primary_web3_wallet_id = self.primary_web3_wallet_id

        username: Union[None, Unset, str]
        if isinstance(self.username, Unset):
            username = UNSET
        else:
            username = self.username

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

        profile_image_url = self.profile_image_url

        image_url = self.image_url

        has_image = self.has_image

        public_metadata: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.public_metadata, Unset):
            public_metadata = self.public_metadata.to_dict()

        private_metadata: Union[Dict[str, Any], None, Unset]
        if isinstance(self.private_metadata, Unset):
            private_metadata = UNSET
        elif isinstance(self.private_metadata, UserPrivateMetadataType0):
            private_metadata = self.private_metadata.to_dict()
        else:
            private_metadata = self.private_metadata

        unsafe_metadata: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.unsafe_metadata, Unset):
            unsafe_metadata = self.unsafe_metadata.to_dict()

        email_addresses: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.email_addresses, Unset):
            email_addresses = []
            for email_addresses_item_data in self.email_addresses:
                email_addresses_item = email_addresses_item_data.to_dict()
                email_addresses.append(email_addresses_item)

        phone_numbers: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.phone_numbers, Unset):
            phone_numbers = []
            for phone_numbers_item_data in self.phone_numbers:
                phone_numbers_item = phone_numbers_item_data.to_dict()
                phone_numbers.append(phone_numbers_item)

        web3_wallets: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.web3_wallets, Unset):
            web3_wallets = []
            for web3_wallets_item_data in self.web3_wallets:
                web3_wallets_item = web3_wallets_item_data.to_dict()
                web3_wallets.append(web3_wallets_item)

        passkeys: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.passkeys, Unset):
            passkeys = []
            for passkeys_item_data in self.passkeys:
                passkeys_item = passkeys_item_data.to_dict()
                passkeys.append(passkeys_item)

        password_enabled = self.password_enabled

        two_factor_enabled = self.two_factor_enabled

        totp_enabled = self.totp_enabled

        backup_code_enabled = self.backup_code_enabled

        mfa_enabled_at: Union[None, Unset, int]
        if isinstance(self.mfa_enabled_at, Unset):
            mfa_enabled_at = UNSET
        else:
            mfa_enabled_at = self.mfa_enabled_at

        mfa_disabled_at: Union[None, Unset, int]
        if isinstance(self.mfa_disabled_at, Unset):
            mfa_disabled_at = UNSET
        else:
            mfa_disabled_at = self.mfa_disabled_at

        external_accounts: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.external_accounts, Unset):
            external_accounts = []
            for external_accounts_item_data in self.external_accounts:
                external_accounts_item = external_accounts_item_data.to_dict()
                external_accounts.append(external_accounts_item)

        saml_accounts: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.saml_accounts, Unset):
            saml_accounts = []
            for saml_accounts_item_data in self.saml_accounts:
                saml_accounts_item = saml_accounts_item_data.to_dict()
                saml_accounts.append(saml_accounts_item)

        last_sign_in_at: Union[None, Unset, int]
        if isinstance(self.last_sign_in_at, Unset):
            last_sign_in_at = UNSET
        else:
            last_sign_in_at = self.last_sign_in_at

        banned = self.banned

        locked = self.locked

        lockout_expires_in_seconds: Union[None, Unset, int]
        if isinstance(self.lockout_expires_in_seconds, Unset):
            lockout_expires_in_seconds = UNSET
        else:
            lockout_expires_in_seconds = self.lockout_expires_in_seconds

        verification_attempts_remaining: Union[None, Unset, int]
        if isinstance(self.verification_attempts_remaining, Unset):
            verification_attempts_remaining = UNSET
        else:
            verification_attempts_remaining = self.verification_attempts_remaining

        updated_at = self.updated_at

        created_at = self.created_at

        delete_self_enabled = self.delete_self_enabled

        create_organization_enabled = self.create_organization_enabled

        create_organizations_limit: Union[None, Unset, int]
        if isinstance(self.create_organizations_limit, Unset):
            create_organizations_limit = UNSET
        else:
            create_organizations_limit = self.create_organizations_limit

        last_active_at: Union[None, Unset, int]
        if isinstance(self.last_active_at, Unset):
            last_active_at = UNSET
        else:
            last_active_at = self.last_active_at

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if object_ is not UNSET:
            field_dict["object"] = object_
        if external_id is not UNSET:
            field_dict["external_id"] = external_id
        if primary_email_address_id is not UNSET:
            field_dict["primary_email_address_id"] = primary_email_address_id
        if primary_phone_number_id is not UNSET:
            field_dict["primary_phone_number_id"] = primary_phone_number_id
        if primary_web3_wallet_id is not UNSET:
            field_dict["primary_web3_wallet_id"] = primary_web3_wallet_id
        if username is not UNSET:
            field_dict["username"] = username
        if first_name is not UNSET:
            field_dict["first_name"] = first_name
        if last_name is not UNSET:
            field_dict["last_name"] = last_name
        if profile_image_url is not UNSET:
            field_dict["profile_image_url"] = profile_image_url
        if image_url is not UNSET:
            field_dict["image_url"] = image_url
        if has_image is not UNSET:
            field_dict["has_image"] = has_image
        if public_metadata is not UNSET:
            field_dict["public_metadata"] = public_metadata
        if private_metadata is not UNSET:
            field_dict["private_metadata"] = private_metadata
        if unsafe_metadata is not UNSET:
            field_dict["unsafe_metadata"] = unsafe_metadata
        if email_addresses is not UNSET:
            field_dict["email_addresses"] = email_addresses
        if phone_numbers is not UNSET:
            field_dict["phone_numbers"] = phone_numbers
        if web3_wallets is not UNSET:
            field_dict["web3_wallets"] = web3_wallets
        if passkeys is not UNSET:
            field_dict["passkeys"] = passkeys
        if password_enabled is not UNSET:
            field_dict["password_enabled"] = password_enabled
        if two_factor_enabled is not UNSET:
            field_dict["two_factor_enabled"] = two_factor_enabled
        if totp_enabled is not UNSET:
            field_dict["totp_enabled"] = totp_enabled
        if backup_code_enabled is not UNSET:
            field_dict["backup_code_enabled"] = backup_code_enabled
        if mfa_enabled_at is not UNSET:
            field_dict["mfa_enabled_at"] = mfa_enabled_at
        if mfa_disabled_at is not UNSET:
            field_dict["mfa_disabled_at"] = mfa_disabled_at
        if external_accounts is not UNSET:
            field_dict["external_accounts"] = external_accounts
        if saml_accounts is not UNSET:
            field_dict["saml_accounts"] = saml_accounts
        if last_sign_in_at is not UNSET:
            field_dict["last_sign_in_at"] = last_sign_in_at
        if banned is not UNSET:
            field_dict["banned"] = banned
        if locked is not UNSET:
            field_dict["locked"] = locked
        if lockout_expires_in_seconds is not UNSET:
            field_dict["lockout_expires_in_seconds"] = lockout_expires_in_seconds
        if verification_attempts_remaining is not UNSET:
            field_dict["verification_attempts_remaining"] = verification_attempts_remaining
        if updated_at is not UNSET:
            field_dict["updated_at"] = updated_at
        if created_at is not UNSET:
            field_dict["created_at"] = created_at
        if delete_self_enabled is not UNSET:
            field_dict["delete_self_enabled"] = delete_self_enabled
        if create_organization_enabled is not UNSET:
            field_dict["create_organization_enabled"] = create_organization_enabled
        if create_organizations_limit is not UNSET:
            field_dict["create_organizations_limit"] = create_organizations_limit
        if last_active_at is not UNSET:
            field_dict["last_active_at"] = last_active_at

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.email_address import EmailAddress
        from ..models.phone_number import PhoneNumber
        from ..models.saml_account import SAMLAccount
        from ..models.schemas_passkey import SchemasPasskey
        from ..models.user_external_accounts_item import UserExternalAccountsItem
        from ..models.user_private_metadata_type_0 import UserPrivateMetadataType0
        from ..models.user_public_metadata import UserPublicMetadata
        from ..models.user_unsafe_metadata import UserUnsafeMetadata
        from ..models.web_3_wallet import Web3Wallet

        d = src_dict.copy()
        id = d.pop("id", UNSET)

        _object_ = d.pop("object", UNSET)
        object_: Union[Unset, UserObject]
        if isinstance(_object_, Unset):
            object_ = UNSET
        else:
            object_ = UserObject(_object_)

        def _parse_external_id(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        external_id = _parse_external_id(d.pop("external_id", UNSET))

        def _parse_primary_email_address_id(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        primary_email_address_id = _parse_primary_email_address_id(d.pop("primary_email_address_id", UNSET))

        def _parse_primary_phone_number_id(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        primary_phone_number_id = _parse_primary_phone_number_id(d.pop("primary_phone_number_id", UNSET))

        def _parse_primary_web3_wallet_id(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        primary_web3_wallet_id = _parse_primary_web3_wallet_id(d.pop("primary_web3_wallet_id", UNSET))

        def _parse_username(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        username = _parse_username(d.pop("username", UNSET))

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

        profile_image_url = d.pop("profile_image_url", UNSET)

        image_url = d.pop("image_url", UNSET)

        has_image = d.pop("has_image", UNSET)

        _public_metadata = d.pop("public_metadata", UNSET)
        public_metadata: Union[Unset, UserPublicMetadata]
        if isinstance(_public_metadata, Unset):
            public_metadata = UNSET
        else:
            public_metadata = UserPublicMetadata.from_dict(_public_metadata)

        def _parse_private_metadata(data: object) -> Union["UserPrivateMetadataType0", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                private_metadata_type_0 = UserPrivateMetadataType0.from_dict(data)

                return private_metadata_type_0
            except:  # noqa: E722
                pass
            return cast(Union["UserPrivateMetadataType0", None, Unset], data)

        private_metadata = _parse_private_metadata(d.pop("private_metadata", UNSET))

        _unsafe_metadata = d.pop("unsafe_metadata", UNSET)
        unsafe_metadata: Union[Unset, UserUnsafeMetadata]
        if isinstance(_unsafe_metadata, Unset):
            unsafe_metadata = UNSET
        else:
            unsafe_metadata = UserUnsafeMetadata.from_dict(_unsafe_metadata)

        email_addresses = []
        _email_addresses = d.pop("email_addresses", UNSET)
        for email_addresses_item_data in _email_addresses or []:
            email_addresses_item = EmailAddress.from_dict(email_addresses_item_data)

            email_addresses.append(email_addresses_item)

        phone_numbers = []
        _phone_numbers = d.pop("phone_numbers", UNSET)
        for phone_numbers_item_data in _phone_numbers or []:
            phone_numbers_item = PhoneNumber.from_dict(phone_numbers_item_data)

            phone_numbers.append(phone_numbers_item)

        web3_wallets = []
        _web3_wallets = d.pop("web3_wallets", UNSET)
        for web3_wallets_item_data in _web3_wallets or []:
            web3_wallets_item = Web3Wallet.from_dict(web3_wallets_item_data)

            web3_wallets.append(web3_wallets_item)

        passkeys = []
        _passkeys = d.pop("passkeys", UNSET)
        for passkeys_item_data in _passkeys or []:
            passkeys_item = SchemasPasskey.from_dict(passkeys_item_data)

            passkeys.append(passkeys_item)

        password_enabled = d.pop("password_enabled", UNSET)

        two_factor_enabled = d.pop("two_factor_enabled", UNSET)

        totp_enabled = d.pop("totp_enabled", UNSET)

        backup_code_enabled = d.pop("backup_code_enabled", UNSET)

        def _parse_mfa_enabled_at(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        mfa_enabled_at = _parse_mfa_enabled_at(d.pop("mfa_enabled_at", UNSET))

        def _parse_mfa_disabled_at(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        mfa_disabled_at = _parse_mfa_disabled_at(d.pop("mfa_disabled_at", UNSET))

        external_accounts = []
        _external_accounts = d.pop("external_accounts", UNSET)
        for external_accounts_item_data in _external_accounts or []:
            external_accounts_item = UserExternalAccountsItem.from_dict(external_accounts_item_data)

            external_accounts.append(external_accounts_item)

        saml_accounts = []
        _saml_accounts = d.pop("saml_accounts", UNSET)
        for saml_accounts_item_data in _saml_accounts or []:
            saml_accounts_item = SAMLAccount.from_dict(saml_accounts_item_data)

            saml_accounts.append(saml_accounts_item)

        def _parse_last_sign_in_at(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        last_sign_in_at = _parse_last_sign_in_at(d.pop("last_sign_in_at", UNSET))

        banned = d.pop("banned", UNSET)

        locked = d.pop("locked", UNSET)

        def _parse_lockout_expires_in_seconds(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        lockout_expires_in_seconds = _parse_lockout_expires_in_seconds(d.pop("lockout_expires_in_seconds", UNSET))

        def _parse_verification_attempts_remaining(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        verification_attempts_remaining = _parse_verification_attempts_remaining(
            d.pop("verification_attempts_remaining", UNSET)
        )

        updated_at = d.pop("updated_at", UNSET)

        created_at = d.pop("created_at", UNSET)

        delete_self_enabled = d.pop("delete_self_enabled", UNSET)

        create_organization_enabled = d.pop("create_organization_enabled", UNSET)

        def _parse_create_organizations_limit(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        create_organizations_limit = _parse_create_organizations_limit(d.pop("create_organizations_limit", UNSET))

        def _parse_last_active_at(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        last_active_at = _parse_last_active_at(d.pop("last_active_at", UNSET))

        user = cls(
            id=id,
            object_=object_,
            external_id=external_id,
            primary_email_address_id=primary_email_address_id,
            primary_phone_number_id=primary_phone_number_id,
            primary_web3_wallet_id=primary_web3_wallet_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            profile_image_url=profile_image_url,
            image_url=image_url,
            has_image=has_image,
            public_metadata=public_metadata,
            private_metadata=private_metadata,
            unsafe_metadata=unsafe_metadata,
            email_addresses=email_addresses,
            phone_numbers=phone_numbers,
            web3_wallets=web3_wallets,
            passkeys=passkeys,
            password_enabled=password_enabled,
            two_factor_enabled=two_factor_enabled,
            totp_enabled=totp_enabled,
            backup_code_enabled=backup_code_enabled,
            mfa_enabled_at=mfa_enabled_at,
            mfa_disabled_at=mfa_disabled_at,
            external_accounts=external_accounts,
            saml_accounts=saml_accounts,
            last_sign_in_at=last_sign_in_at,
            banned=banned,
            locked=locked,
            lockout_expires_in_seconds=lockout_expires_in_seconds,
            verification_attempts_remaining=verification_attempts_remaining,
            updated_at=updated_at,
            created_at=created_at,
            delete_self_enabled=delete_self_enabled,
            create_organization_enabled=create_organization_enabled,
            create_organizations_limit=create_organizations_limit,
            last_active_at=last_active_at,
        )

        return user
