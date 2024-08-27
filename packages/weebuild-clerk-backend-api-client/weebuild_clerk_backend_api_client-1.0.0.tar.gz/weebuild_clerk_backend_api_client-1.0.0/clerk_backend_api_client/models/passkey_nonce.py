from enum import Enum


class PasskeyNonce(str, Enum):
    NONCE = "nonce"

    def __str__(self) -> str:
        return str(self.value)
