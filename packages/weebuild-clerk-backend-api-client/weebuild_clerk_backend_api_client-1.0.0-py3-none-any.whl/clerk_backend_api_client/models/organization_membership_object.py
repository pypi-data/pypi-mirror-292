from enum import Enum


class OrganizationMembershipObject(str, Enum):
    ORGANIZATION_MEMBERSHIP = "organization_membership"

    def __str__(self) -> str:
        return str(self.value)
