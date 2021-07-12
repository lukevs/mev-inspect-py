from typing import List, Optional

from pydantic import BaseModel


class Block(BaseModel):
    block_number: int
    calls: List[dict]
    data: dict
    logs: List[dict]
    receipts: dict
    transaction_hashes: List[str]

    def get_filtered_calls(self, hash: str) -> List[dict]:
        return [
            call for call in self.calls
            if call["transactionHash"] == hash
        ]
