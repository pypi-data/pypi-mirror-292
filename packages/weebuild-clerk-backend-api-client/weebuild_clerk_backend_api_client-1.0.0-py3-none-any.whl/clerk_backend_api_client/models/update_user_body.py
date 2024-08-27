from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define

from ..models.password_hasher import PasswordHasher
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.update_user_body_private_metadata import UpdateUserBodyPrivateMetadata
    from ..models.update_user_body_public_metadata import UpdateUserBodyPublicMetadata
    from ..models.update_user_body_unsafe_metadata import UpdateUserBodyUnsafeMetadata


T = TypeVar("T", bound="UpdateUserBody")


@_attrs_define
class UpdateUserBody:
    """
    Attributes:
        external_id (Union[None, Unset, str]): The ID of the user as used in your external systems or your previous
            authentication solution.
            Must be unique across your instance.
        first_name (Union[None, Unset, str]): The first name to assign to the user
        last_name (Union[None, Unset, str]): The last name to assign to the user
        primary_email_address_id (Union[Unset, str]): The ID of the email address to set as primary.
            It must be verified, and present on the current user.
        notify_primary_email_address_changed (Union[Unset, bool]): If set to `true`, the user will be notified that
            their primary email address has changed.
            By default, no notification is sent. Default: False.
        primary_phone_number_id (Union[Unset, str]): The ID of the phone number to set as primary.
            It must be verified, and present on the current user.
        primary_web3_wallet_id (Union[Unset, str]): The ID of the web3 wallets to set as primary.
            It must be verified, and present on the current user.
        username (Union[None, Unset, str]): The username to give to the user.
            It must be unique across your instance.
        profile_image_id (Union[None, Unset, str]): The ID of the image to set as the user's profile image
        password (Union[None, Unset, str]): The plaintext password to give the user.
            Must be at least 8 characters long, and can not be in any list of hacked passwords.
        password_digest (Union[Unset, str]): In case you already have the password digests and not the passwords, you
            can use them for the newly created user via this property.
            The digests should be generated with one of the supported algorithms.
            The hashing algorithm can be specified using the `password_hasher` property.
        password_hasher (Union[Unset, PasswordHasher]): The hashing algorithm that was used to generate the password
            digest.
            The algorithms we support at the moment are [bcrypt](https://en.wikipedia.org/wiki/Bcrypt),
            [bcrypt_sha256_django](https://docs.djangoproject.com/en/4.0/topics/auth/passwords/),
            [bcrypt_peppered](https://github.com/heartcombo/devise),
            hmac_sha256_utf16_b64, [md5](https://en.wikipedia.org/wiki/MD5), pbkdf2_sha1, pbkdf2_sha256, pbkdf2_sha512,
            [pbkdf2_sha256_django](https://docs.djangoproject.com/en/4.0/topics/auth/passwords/),
            [phpass](https://www.openwall.com/phpass/),
            [scrypt_firebase](https://firebaseopensource.com/projects/firebase/scrypt/),
            [scrypt_werkzeug](https://werkzeug.palletsprojects.com/en/3.0.x/utils/#werkzeug.security.generate_password_hash)
            , [sha256](https://en.wikipedia.org/wiki/SHA-2), sha256_salted
            and the [argon2](https://argon2.online/) variants argon2i and argon2id.

            If you need support for any particular hashing algorithm, [please let us know](https://clerk.com/support).

            Note: for password hashers considered insecure (at this moment MD5 and SHA256), the corresponding user password
            hashes will be transparently migrated to Bcrypt (a secure hasher) upon the user's first successful password sign
            in.
            Insecure schemes are marked with `(insecure)` in the list below.

            Each of the supported hashers expects the incoming digest to be in a particular format. Specifically:

            **bcrypt:** The digest should be of the following form:

            `$<algorithm version>$<cost>$<salt & hash>`

            **bcrypt_sha256_django:** This is the Django-specific variant of Bcrypt, using SHA256 hashing function. The
            format should be as follows (as exported from Django):

            `bcrypt_sha256$$<algorithm version>$<cost>$<salt & hash>`

            **bcrypt_peppered:** As used in implementations such as Devise for Ruby on Rails applications. Identical to
            bcrypt except for the fact that a `pepper` string is appended to the input before hashing. Should be provided in
            the following format:

            `$<algorithm version>$<cost>$<salt & hash>$<pepper>`

            **hmac_sha256_utf16_b64** (insecure): This is HMAC algorithm using the SHA256 hashing function. The format
            should be as follows:

            `hmac_sha256_utf16_b64$<hash>$<key>`

            **md5** (insecure): The digest should follow the regular form e.g.:

            `5f4dcc3b5aa765d61d8327deb882cf99`

            **pbkdf2_sha256:** This is the PBKDF2 algorithm using the SHA256 hashing function. The format should be as
            follows:

            `pbkdf2_sha256$<iterations>$<salt>$<hash>`

            Note: Both the salt and the hash are expected to be base64-encoded.

            **pbkdf2_sha512:** This is the PBKDF2 algorithm using the SHA512 hashing function. The format should be as
            follows:

            `pbkdf2_sha512$<iterations>$<salt>$<hash>`

              _iterations:_ The number of iterations used. Must be an integer less than 420000.
              _salt:_ The salt used when generating the hash. Must be less than 1024 bytes.
              _hash:_ The hex-encoded hash. Must have been generated with a key length less than 1024 bytes.

            **pbkdf2_sha256_django:** This is the Django-specific variant of PBKDF2 and the digest should have the following
            format (as exported from Django):

            `pbkdf2_sha256$<iterations>$<salt>$<hash>`

            Note: The salt is expected to be un-encoded, the hash is expected base64-encoded.

            **pbkdf2_sha1:** This is similar to pkbdf2_sha256_django, but with two differences:
            1. uses sha1 instead of sha256
            2. accepts the salt as a hex-encoded string. If the salt is not a valid hex string,
               the raw bytes will be used instead
            3. accepts the hash as a hex-encoded string
            4. optionally accepts the key length as the last parameter (defaults to `32`)

            The format is the following:

            `pbkdf2_sha1$<iterations>$<salt>$<hash-as-hex-string>` or
            `pbkdf2_sha1$<iterations>$<salt-as-hex-string>$<hash-as-hex-string>$<key-length>`

            **phpass:** Portable public domain password hashing framework for use in PHP applications. Digests hashed with
            phpass have the following sections:

            The format is the following:

            `$P$<rounds><salt><encoded-checksum>`

            - $P$ is the prefix used to identify phpass hashes.
            - rounds is a single character encoding a 6-bit integer representing the number of rounds used.
            - salt is eight characters drawn from [./0-9A-Za-z], providing a 48-bit salt.
            - checksum is 22 characters drawn from the same set, encoding the 128-bit checksum with MD5.

            **scrypt_firebase:** The Firebase-specific variant of scrypt.
            The value is expected to have 6 segments separated by the $ character and include the following information:

            _hash:_ The actual Base64 hash. This can be retrieved when exporting the user from Firebase.
            _salt:_ The salt used to generate the above hash. Again, this is given when exporting the user.
            _signer key:_ The base64 encoded signer key.
            _salt separator:_ The base64 encoded salt separator.
            _rounds:_ The number of rounds the algorithm needs to run.
            _memory cost:_ The cost of the algorithm run

            The first 2 (hash and salt) are per user and can be retrieved when exporting the user from Firebase.
            The other 4 values (signer key, salt separator, rounds and memory cost) are project-wide settings and can be
            retrieved from the project's password hash parameters.

            Once you have all these, you can combine it in the following format and send this as the digest in order for
            Clerk to accept it:

            `<hash>$<salt>$<signer key>$<salt separator>$<rounds>$<memory cost>`

            **scrypt_werkzeug:** The Werkzeug-specific variant of scrypt.

              The value is expected to have 3 segments separated by the $ character and include the following information:

              _algorithm args:_ The algorithm used to generate the hash.
              _salt:_ The salt used to generate the above hash.
              _hash:_ The actual Base64 hash.

              The algorithm args are the parameters used to generate the hash and are included in the digest.

            **argon2i:** Algorithms in the argon2 family generate digests that encode the following information:

            _version (v):_ The argon version, version 19 is assumed
            _memory (m):_ The memory used by the algorithm (in kibibytes)
            _iterations (t):_ The number of iterations to perform
            _parallelism (p):_ The number of threads to use

            Parts are demarcated by the `$` character, with the first part identifying the algorithm variant.
            The middle part is a comma-separated list of the encoding options (memory, iterations, parallelism).
            The final part is the actual digest.

            `$argon2i$v=19$m=4096,t=3,p=1$4t6CL3P7YiHBtwESXawI8Hm20zJj4cs7/4/G3c187e0$m7RQFczcKr5bIR0IIxbpO2P0tyrLjf3eUW3M3Q
            SwnLc`

            **argon2id:** See the previous algorithm for an explanation of the formatting.

            For the argon2id case, the value of the algorithm in the first part of the digest is `argon2id`:

            `$argon2id$v=19$m=64,t=4,p=8$Z2liZXJyaXNo$iGXEpMBTDYQ8G/71tF0qGjxRHEmR3gpGULcE93zUJVU`

            **sha256** (insecure): The digest should be a 64-length hex string, e.g.:

            `9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08`

            **sha256_salted** (insecure): The digest should be a 64-length hex string with a salt.

            The format is the following:
              `<hash>$<salt>`

            The value is expected to have 2 segments separated by the $ character and include the following information:
              _hash:_ The sha256 hash, a 64-length hex string.
              _salt:_ The salt used to generate the above hash. Must be between 1 and 1024 bits.

            **awscognito**:

            This is a special migration hasher. The value must be `awscognito`.

            When set, `password_digest` must be in the format of `awscognito#<userpoolid>#<clientid>#<identifier>`.

            Upon a successful migration, `password_hasher` will be updated to `bcrypt`, and
            `password_digest` will be updated to a `bcrypt` hash.

            See our [migration guide](https://clerk.com/docs/deployments/migrate-from-cognito)
            for usage details.
        skip_password_checks (Union[None, Unset, bool]): Set it to `true` if you're updating the user's password and
            want to skip any password policy settings check. This parameter can only be used when providing a `password`.
        sign_out_of_other_sessions (Union[None, Unset, bool]): Set to `true` to sign out the user from all their active
            sessions once their password is updated. This parameter can only be used when providing a `password`.
        totp_secret (Union[Unset, str]): In case TOTP is configured on the instance, you can provide the secret to
            enable it on the specific user without the need to reset it.
            Please note that currently the supported options are:
            * Period: 30 seconds
            * Code length: 6 digits
            * Algorithm: SHA1
        backup_codes (Union[Unset, List[str]]): If Backup Codes are configured on the instance, you can provide them to
            enable it on the specific user without the need to reset them.
            You must provide the backup codes in plain format or the corresponding bcrypt digest.
        public_metadata (Union[Unset, UpdateUserBodyPublicMetadata]): Metadata saved on the user, that is visible to
            both your Frontend and Backend APIs
        private_metadata (Union[Unset, UpdateUserBodyPrivateMetadata]): Metadata saved on the user, that is only visible
            to your Backend API
        unsafe_metadata (Union[Unset, UpdateUserBodyUnsafeMetadata]): Metadata saved on the user, that can be updated
            from both the Frontend and Backend APIs.
            Note: Since this data can be modified from the frontend, it is not guaranteed to be safe.
        delete_self_enabled (Union[None, Unset, bool]): If true, the user can delete themselves with the Frontend API.
        create_organization_enabled (Union[None, Unset, bool]): If true, the user can create organizations with the
            Frontend API.
        create_organizations_limit (Union[None, Unset, int]): The maximum number of organizations the user can create. 0
            means unlimited.
        created_at (Union[Unset, str]): A custom date/time denoting _when_ the user signed up to the application,
            specified in RFC3339 format (e.g. `2012-10-20T07:15:20.902Z`).
    """

    external_id: Union[None, Unset, str] = UNSET
    first_name: Union[None, Unset, str] = UNSET
    last_name: Union[None, Unset, str] = UNSET
    primary_email_address_id: Union[Unset, str] = UNSET
    notify_primary_email_address_changed: Union[Unset, bool] = False
    primary_phone_number_id: Union[Unset, str] = UNSET
    primary_web3_wallet_id: Union[Unset, str] = UNSET
    username: Union[None, Unset, str] = UNSET
    profile_image_id: Union[None, Unset, str] = UNSET
    password: Union[None, Unset, str] = UNSET
    password_digest: Union[Unset, str] = UNSET
    password_hasher: Union[Unset, PasswordHasher] = UNSET
    skip_password_checks: Union[None, Unset, bool] = UNSET
    sign_out_of_other_sessions: Union[None, Unset, bool] = UNSET
    totp_secret: Union[Unset, str] = UNSET
    backup_codes: Union[Unset, List[str]] = UNSET
    public_metadata: Union[Unset, "UpdateUserBodyPublicMetadata"] = UNSET
    private_metadata: Union[Unset, "UpdateUserBodyPrivateMetadata"] = UNSET
    unsafe_metadata: Union[Unset, "UpdateUserBodyUnsafeMetadata"] = UNSET
    delete_self_enabled: Union[None, Unset, bool] = UNSET
    create_organization_enabled: Union[None, Unset, bool] = UNSET
    create_organizations_limit: Union[None, Unset, int] = UNSET
    created_at: Union[Unset, str] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        external_id: Union[None, Unset, str]
        if isinstance(self.external_id, Unset):
            external_id = UNSET
        else:
            external_id = self.external_id

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

        primary_email_address_id = self.primary_email_address_id

        notify_primary_email_address_changed = self.notify_primary_email_address_changed

        primary_phone_number_id = self.primary_phone_number_id

        primary_web3_wallet_id = self.primary_web3_wallet_id

        username: Union[None, Unset, str]
        if isinstance(self.username, Unset):
            username = UNSET
        else:
            username = self.username

        profile_image_id: Union[None, Unset, str]
        if isinstance(self.profile_image_id, Unset):
            profile_image_id = UNSET
        else:
            profile_image_id = self.profile_image_id

        password: Union[None, Unset, str]
        if isinstance(self.password, Unset):
            password = UNSET
        else:
            password = self.password

        password_digest = self.password_digest

        password_hasher: Union[Unset, str] = UNSET
        if not isinstance(self.password_hasher, Unset):
            password_hasher = self.password_hasher.value

        skip_password_checks: Union[None, Unset, bool]
        if isinstance(self.skip_password_checks, Unset):
            skip_password_checks = UNSET
        else:
            skip_password_checks = self.skip_password_checks

        sign_out_of_other_sessions: Union[None, Unset, bool]
        if isinstance(self.sign_out_of_other_sessions, Unset):
            sign_out_of_other_sessions = UNSET
        else:
            sign_out_of_other_sessions = self.sign_out_of_other_sessions

        totp_secret = self.totp_secret

        backup_codes: Union[Unset, List[str]] = UNSET
        if not isinstance(self.backup_codes, Unset):
            backup_codes = self.backup_codes

        public_metadata: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.public_metadata, Unset):
            public_metadata = self.public_metadata.to_dict()

        private_metadata: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.private_metadata, Unset):
            private_metadata = self.private_metadata.to_dict()

        unsafe_metadata: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.unsafe_metadata, Unset):
            unsafe_metadata = self.unsafe_metadata.to_dict()

        delete_self_enabled: Union[None, Unset, bool]
        if isinstance(self.delete_self_enabled, Unset):
            delete_self_enabled = UNSET
        else:
            delete_self_enabled = self.delete_self_enabled

        create_organization_enabled: Union[None, Unset, bool]
        if isinstance(self.create_organization_enabled, Unset):
            create_organization_enabled = UNSET
        else:
            create_organization_enabled = self.create_organization_enabled

        create_organizations_limit: Union[None, Unset, int]
        if isinstance(self.create_organizations_limit, Unset):
            create_organizations_limit = UNSET
        else:
            create_organizations_limit = self.create_organizations_limit

        created_at = self.created_at

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if external_id is not UNSET:
            field_dict["external_id"] = external_id
        if first_name is not UNSET:
            field_dict["first_name"] = first_name
        if last_name is not UNSET:
            field_dict["last_name"] = last_name
        if primary_email_address_id is not UNSET:
            field_dict["primary_email_address_id"] = primary_email_address_id
        if notify_primary_email_address_changed is not UNSET:
            field_dict["notify_primary_email_address_changed"] = notify_primary_email_address_changed
        if primary_phone_number_id is not UNSET:
            field_dict["primary_phone_number_id"] = primary_phone_number_id
        if primary_web3_wallet_id is not UNSET:
            field_dict["primary_web3_wallet_id"] = primary_web3_wallet_id
        if username is not UNSET:
            field_dict["username"] = username
        if profile_image_id is not UNSET:
            field_dict["profile_image_id"] = profile_image_id
        if password is not UNSET:
            field_dict["password"] = password
        if password_digest is not UNSET:
            field_dict["password_digest"] = password_digest
        if password_hasher is not UNSET:
            field_dict["password_hasher"] = password_hasher
        if skip_password_checks is not UNSET:
            field_dict["skip_password_checks"] = skip_password_checks
        if sign_out_of_other_sessions is not UNSET:
            field_dict["sign_out_of_other_sessions"] = sign_out_of_other_sessions
        if totp_secret is not UNSET:
            field_dict["totp_secret"] = totp_secret
        if backup_codes is not UNSET:
            field_dict["backup_codes"] = backup_codes
        if public_metadata is not UNSET:
            field_dict["public_metadata"] = public_metadata
        if private_metadata is not UNSET:
            field_dict["private_metadata"] = private_metadata
        if unsafe_metadata is not UNSET:
            field_dict["unsafe_metadata"] = unsafe_metadata
        if delete_self_enabled is not UNSET:
            field_dict["delete_self_enabled"] = delete_self_enabled
        if create_organization_enabled is not UNSET:
            field_dict["create_organization_enabled"] = create_organization_enabled
        if create_organizations_limit is not UNSET:
            field_dict["create_organizations_limit"] = create_organizations_limit
        if created_at is not UNSET:
            field_dict["created_at"] = created_at

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.update_user_body_private_metadata import UpdateUserBodyPrivateMetadata
        from ..models.update_user_body_public_metadata import UpdateUserBodyPublicMetadata
        from ..models.update_user_body_unsafe_metadata import UpdateUserBodyUnsafeMetadata

        d = src_dict.copy()

        def _parse_external_id(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        external_id = _parse_external_id(d.pop("external_id", UNSET))

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

        primary_email_address_id = d.pop("primary_email_address_id", UNSET)

        notify_primary_email_address_changed = d.pop("notify_primary_email_address_changed", UNSET)

        primary_phone_number_id = d.pop("primary_phone_number_id", UNSET)

        primary_web3_wallet_id = d.pop("primary_web3_wallet_id", UNSET)

        def _parse_username(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        username = _parse_username(d.pop("username", UNSET))

        def _parse_profile_image_id(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        profile_image_id = _parse_profile_image_id(d.pop("profile_image_id", UNSET))

        def _parse_password(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        password = _parse_password(d.pop("password", UNSET))

        password_digest = d.pop("password_digest", UNSET)

        _password_hasher = d.pop("password_hasher", UNSET)
        password_hasher: Union[Unset, PasswordHasher]
        if isinstance(_password_hasher, Unset):
            password_hasher = UNSET
        else:
            password_hasher = PasswordHasher(_password_hasher)

        def _parse_skip_password_checks(data: object) -> Union[None, Unset, bool]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, bool], data)

        skip_password_checks = _parse_skip_password_checks(d.pop("skip_password_checks", UNSET))

        def _parse_sign_out_of_other_sessions(data: object) -> Union[None, Unset, bool]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, bool], data)

        sign_out_of_other_sessions = _parse_sign_out_of_other_sessions(d.pop("sign_out_of_other_sessions", UNSET))

        totp_secret = d.pop("totp_secret", UNSET)

        backup_codes = cast(List[str], d.pop("backup_codes", UNSET))

        _public_metadata = d.pop("public_metadata", UNSET)
        public_metadata: Union[Unset, UpdateUserBodyPublicMetadata]
        if isinstance(_public_metadata, Unset):
            public_metadata = UNSET
        else:
            public_metadata = UpdateUserBodyPublicMetadata.from_dict(_public_metadata)

        _private_metadata = d.pop("private_metadata", UNSET)
        private_metadata: Union[Unset, UpdateUserBodyPrivateMetadata]
        if isinstance(_private_metadata, Unset):
            private_metadata = UNSET
        else:
            private_metadata = UpdateUserBodyPrivateMetadata.from_dict(_private_metadata)

        _unsafe_metadata = d.pop("unsafe_metadata", UNSET)
        unsafe_metadata: Union[Unset, UpdateUserBodyUnsafeMetadata]
        if isinstance(_unsafe_metadata, Unset):
            unsafe_metadata = UNSET
        else:
            unsafe_metadata = UpdateUserBodyUnsafeMetadata.from_dict(_unsafe_metadata)

        def _parse_delete_self_enabled(data: object) -> Union[None, Unset, bool]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, bool], data)

        delete_self_enabled = _parse_delete_self_enabled(d.pop("delete_self_enabled", UNSET))

        def _parse_create_organization_enabled(data: object) -> Union[None, Unset, bool]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, bool], data)

        create_organization_enabled = _parse_create_organization_enabled(d.pop("create_organization_enabled", UNSET))

        def _parse_create_organizations_limit(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        create_organizations_limit = _parse_create_organizations_limit(d.pop("create_organizations_limit", UNSET))

        created_at = d.pop("created_at", UNSET)

        update_user_body = cls(
            external_id=external_id,
            first_name=first_name,
            last_name=last_name,
            primary_email_address_id=primary_email_address_id,
            notify_primary_email_address_changed=notify_primary_email_address_changed,
            primary_phone_number_id=primary_phone_number_id,
            primary_web3_wallet_id=primary_web3_wallet_id,
            username=username,
            profile_image_id=profile_image_id,
            password=password,
            password_digest=password_digest,
            password_hasher=password_hasher,
            skip_password_checks=skip_password_checks,
            sign_out_of_other_sessions=sign_out_of_other_sessions,
            totp_secret=totp_secret,
            backup_codes=backup_codes,
            public_metadata=public_metadata,
            private_metadata=private_metadata,
            unsafe_metadata=unsafe_metadata,
            delete_self_enabled=delete_self_enabled,
            create_organization_enabled=create_organization_enabled,
            create_organizations_limit=create_organizations_limit,
            created_at=created_at,
        )

        return update_user_body
