from enum import Enum


class PasskeyStatus(str, Enum):
    VERIFIED = "verified"

    def __str__(self) -> str:
        return str(self.value)
