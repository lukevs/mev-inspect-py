from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, validator

from mev_inspect.utils import hex_to_int
from .utils import CamelModel, Web3Model


class CallResult(CamelModel):
    gas_used: int

    @validator("gas_used", pre=True)
    def maybe_hex_to_int(v):
        if isinstance(v, str):
            return hex_to_int(v)
        return v


class CallAction(Web3Model):
    to: str
    from_: str
    input: str
    value: int
    gas: int

    @validator("value", "gas", pre=True)
    def maybe_hex_to_int(v):
        if isinstance(v, str):
            return hex_to_int(v)
        return v

    class Config:
        fields = {"from_": "from"}


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
    traces: List[Trace]
    data: dict
    logs: List[dict]
    receipts: dict
    transaction_hashes: List[str]
    txs_gas_data: Dict[str, dict]

    def get_filtered_traces(self, hash: str) -> List[Trace]:
        return [trace for trace in self.traces if trace.transaction_hash == hash]


class NestedTrace(BaseModel):
    trace: Trace
    subtraces: List["NestedTrace"]


NestedTrace.update_forward_refs()
