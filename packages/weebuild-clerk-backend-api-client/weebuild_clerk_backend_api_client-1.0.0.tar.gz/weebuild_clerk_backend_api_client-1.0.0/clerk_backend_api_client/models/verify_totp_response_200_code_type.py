from enum import Enum


class VerifyTOTPResponse200CodeType(str, Enum):
    BACKUP_CODE = "backup_code"
    TOTP = "totp"

    def __str__(self) -> str:
        return str(self.value)
