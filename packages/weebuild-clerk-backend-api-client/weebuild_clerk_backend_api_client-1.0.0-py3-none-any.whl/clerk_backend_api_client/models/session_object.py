from enum import Enum


class SessionObject(str, Enum):
    SESSION = "session"

    def __str__(self) -> str:
        return str(self.value)
