from enum import Enum


class AdminStrategy(str, Enum):
    ADMIN = "admin"

    def __str__(self) -> str:
        return str(self.value)
