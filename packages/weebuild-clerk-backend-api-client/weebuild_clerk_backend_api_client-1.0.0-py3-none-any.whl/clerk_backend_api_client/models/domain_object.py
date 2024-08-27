from enum import Enum


class DomainObject(str, Enum):
    DOMAIN = "domain"

    def __str__(self) -> str:
        return str(self.value)
