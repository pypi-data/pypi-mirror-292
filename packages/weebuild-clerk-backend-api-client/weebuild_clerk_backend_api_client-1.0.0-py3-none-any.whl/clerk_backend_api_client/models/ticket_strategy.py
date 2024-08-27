from enum import Enum


class TicketStrategy(str, Enum):
    TICKET = "ticket"

    def __str__(self) -> str:
        return str(self.value)
