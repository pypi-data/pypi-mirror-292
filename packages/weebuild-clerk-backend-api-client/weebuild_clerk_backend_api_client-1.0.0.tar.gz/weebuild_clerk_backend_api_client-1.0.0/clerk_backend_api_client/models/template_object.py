from enum import Enum


class TemplateObject(str, Enum):
    TEMPLATE = "template"

    def __str__(self) -> str:
        return str(self.value)
