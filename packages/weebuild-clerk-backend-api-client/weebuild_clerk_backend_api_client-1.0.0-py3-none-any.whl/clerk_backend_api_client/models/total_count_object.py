from enum import Enum


class TotalCountObject(str, Enum):
    TOTAL_COUNT = "total_count"

    def __str__(self) -> str:
        return str(self.value)
