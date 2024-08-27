from enum import Enum


class Web3SignatureStrategy(str, Enum):
    WEB3_COINBASE_SIGNATURE = "web3_coinbase_signature"
    WEB3_METAMASK_SIGNATURE = "web3_metamask_signature"

    def __str__(self) -> str:
        return str(self.value)
