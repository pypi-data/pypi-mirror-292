from enum import Enum


class PasswordHasher(str, Enum):
    ARGON2I = "argon2i"
    ARGON2ID = "argon2id"
    AWSCOGNITO = "awscognito"
    BCRYPT = "bcrypt"
    BCRYPT_PEPPERED = "bcrypt_peppered"
    BCRYPT_SHA256_DJANGO = "bcrypt_sha256_django"
    HMAC_SHA256_UTF16_B64 = "hmac_sha256_utf16_b64"
    MD5 = "md5"
    PBKDF2_SHA1 = "pbkdf2_sha1"
    PBKDF2_SHA256 = "pbkdf2_sha256"
    PBKDF2_SHA256_DJANGO = "pbkdf2_sha256_django"
    PBKDF2_SHA512 = "pbkdf2_sha512"
    PHPASS = "phpass"
    SCRYPT_FIREBASE = "scrypt_firebase"
    SCRYPT_WERKZEUG = "scrypt_werkzeug"
    SHA256 = "sha256"
    SHA256_SALTED = "sha256_salted"

    def __str__(self) -> str:
        return str(self.value)
