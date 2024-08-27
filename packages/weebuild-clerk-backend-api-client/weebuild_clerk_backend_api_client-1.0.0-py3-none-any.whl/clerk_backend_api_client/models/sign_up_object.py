from enum import Enum


class SignUpObject(str, Enum):
    SIGN_UP_ATTEMPT = "sign_up_attempt"

    def __str__(self) -> str:
        return str(self.value)
