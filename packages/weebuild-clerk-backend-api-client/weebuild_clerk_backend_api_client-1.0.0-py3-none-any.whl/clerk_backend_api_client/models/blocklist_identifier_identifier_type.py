from enum import Enum


class BlocklistIdentifierIdentifierType(str, Enum):
    EMAIL_ADDRESS = "email_address"
    PHONE_NUMBER = "phone_number"
    WEB3_WALLET = "web3_wallet"

    def __str__(self) -> str:
        return str(self.value)
