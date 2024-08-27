from enum import Enum


class CreateSessionTokenFromTemplateResponse200Object(str, Enum):
    TOKEN = "token"

    def __str__(self) -> str:
        return str(self.value)
