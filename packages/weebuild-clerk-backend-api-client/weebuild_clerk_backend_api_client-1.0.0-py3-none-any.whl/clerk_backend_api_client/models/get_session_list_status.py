from enum import Enum


class GetSessionListStatus(str, Enum):
    ABANDONED = "abandoned"
    ACTIVE = "active"
    ENDED = "ended"
    EXPIRED = "expired"
    REMOVED = "removed"
    REPLACED = "replaced"
    REVOKED = "revoked"

    def __str__(self) -> str:
        return str(self.value)
