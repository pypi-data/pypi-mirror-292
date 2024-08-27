from enum import Enum


class Web3WalletObject(str, Enum):
    WEB3_WALLET = "web3_wallet"

    def __str__(self) -> str:
        return str(self.value)
