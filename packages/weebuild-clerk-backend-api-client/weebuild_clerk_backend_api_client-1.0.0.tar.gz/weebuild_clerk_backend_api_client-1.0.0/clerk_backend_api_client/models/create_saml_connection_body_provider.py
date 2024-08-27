from enum import Enum


class CreateSAMLConnectionBodyProvider(str, Enum):
    SAML_CUSTOM = "saml_custom"
    SAML_GOOGLE = "saml_google"
    SAML_MICROSOFT = "saml_microsoft"
    SAML_OKTA = "saml_okta"

    def __str__(self) -> str:
        return str(self.value)
