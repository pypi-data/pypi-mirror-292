from enum import Enum


class SAMLAccountObject(str, Enum):
    SAML_ACCOUNT = "saml_account"

    def __str__(self) -> str:
        return str(self.value)
