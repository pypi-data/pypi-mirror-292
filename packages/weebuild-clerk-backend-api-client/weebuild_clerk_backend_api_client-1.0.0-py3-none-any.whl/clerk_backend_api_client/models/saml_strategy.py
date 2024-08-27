from enum import Enum


class SAMLStrategy(str, Enum):
    SAML = "saml"

    def __str__(self) -> str:
        return str(self.value)
