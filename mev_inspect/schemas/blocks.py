from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel

from .utils import CamelModel, Web3Model


class TraceType(Enum):
    call = "call"
    create = "create"
    delegate_call = "delegateCall"
    reward = "reward"
    suicide = "suicide"


class Trace(CamelModel):
    action: dict
    block_hash: str
    block_number: int
    result: Optional[dict]
    subtraces: int
    trace_address: List[int]
    transaction_hash: Optional[str]
    transaction_position: Optional[int]
    type: TraceType
    error: Optional[str]


class Block(Web3Model):
    block_number: int
    calls: List[Trace]
    data: dict
    logs: List[dict]
    receipts: dict
    transaction_hashes: List[str]
    txs_gas_data: Dict[str, dict]

    def get_filtered_calls(self, hash: str) -> List[Trace]:
        return [call for call in self.calls if call.transaction_hash == hash]


class NestedTrace(BaseModel):
    trace: Trace
    subtraces: List["NestedTrace"]


NestedTrace.update_forward_refs()
