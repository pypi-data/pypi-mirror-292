from enum import Enum


class ActorTokenObject(str, Enum):
    ACTOR_TOKEN = "actor_token"

    def __str__(self) -> str:
        return str(self.value)
