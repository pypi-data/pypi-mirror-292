from enum import Enum


class RevertTemplateTemplateType(str, Enum):
    EMAIL = "email"
    SMS = "sms"

    def __str__(self) -> str:
        return str(self.value)
