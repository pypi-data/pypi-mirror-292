from enum import Enum


class AllowlistIdentifierObject(str, Enum):
    ALLOWLIST_IDENTIFIER = "allowlist_identifier"

    def __str__(self) -> str:
        return str(self.value)
