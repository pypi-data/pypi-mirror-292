from enum import Enum


class TestingTokenObject(str, Enum):
    TESTING_TOKEN = "testing_token"

    def __str__(self) -> str:
        return str(self.value)
