from enum import Enum


class OrganizationSettingsObject(str, Enum):
    ORGANIZATION_SETTINGS = "organization_settings"

    def __str__(self) -> str:
        return str(self.value)
