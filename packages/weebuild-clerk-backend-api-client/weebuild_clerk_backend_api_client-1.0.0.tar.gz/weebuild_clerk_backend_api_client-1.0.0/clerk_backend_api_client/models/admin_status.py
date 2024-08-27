from enum import Enum


class AdminStatus(str, Enum):
    VERIFIED = "verified"

    def __str__(self) -> str:
        return str(self.value)
