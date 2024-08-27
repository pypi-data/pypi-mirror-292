from enum import Enum


class InvitationStatus(str, Enum):
    ACCEPTED = "accepted"
    PENDING = "pending"
    REVOKED = "revoked"

    def __str__(self) -> str:
        return str(self.value)
