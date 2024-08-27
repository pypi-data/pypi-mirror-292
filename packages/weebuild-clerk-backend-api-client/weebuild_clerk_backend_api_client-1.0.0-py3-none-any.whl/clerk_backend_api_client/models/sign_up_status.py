from enum import Enum


class SignUpStatus(str, Enum):
    ABANDONED = "abandoned"
    COMPLETE = "complete"
    MISSING_REQUIREMENTS = "missing_requirements"

    def __str__(self) -> str:
        return str(self.value)
