from enum import Enum


class UpsertTemplateTemplateType(str, Enum):
    EMAIL = "email"
    SMS = "sms"

    def __str__(self) -> str:
        return str(self.value)
