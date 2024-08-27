from enum import Enum


class SignInTokenObject(str, Enum):
    SIGN_IN_TOKEN = "sign_in_token"

    def __str__(self) -> str:
        return str(self.value)
