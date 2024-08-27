from enum import Enum


class InvitationObject(str, Enum):
    INVITATION = "invitation"

    def __str__(self) -> str:
        return str(self.value)
