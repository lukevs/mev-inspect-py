from enum import Enum
from typing import Dict, List, Optional, Union
from typing_extensions import Literal

from hexbytes import HexBytes

from .utils import CamelModel, Web3Model


class BlockCallType(str, Enum):
    call = "call"
    create = "create"
    create2 = "create2"
    delegate_call = "delegateCall"
    reward = "reward"
    suicide = "suicide"


NON_CALL_TYPES = Union[
    Literal[BlockCallType.create],
    Literal[BlockCallType.create2],
    Literal[BlockCallType.delegate_call],
    Literal[BlockCallType.reward],
    Literal[BlockCallType.suicide],
]


class CallAction(CamelModel):
    to: str
    input: HexBytes

    def get_function_selector(self) -> str:
        return self.input[:10].decode()


class GenericBlockCall(CamelModel):
    action: dict
    block_hash: str
    block_number: int
    result: Optional[dict]
    subtraces: int
    trace_address: List[int]
    transaction_hash: Optional[str]
    transaction_position: Optional[int]
    type: NON_CALL_TYPES
    error: Optional[str]


class CallBlockCall(CamelModel):
    action: CallAction
    block_hash: str
    block_number: int
    result: Optional[dict]
    subtraces: int
    trace_address: List[int]
    transaction_hash: Optional[str]
    transaction_position: Optional[int]
    type: Literal[BlockCallType.call]
    error: Optional[str]


BlockCall = Union[CallBlockCall, GenericBlockCall]


class Block(Web3Model):
    block_number: int
    calls: List[BlockCall]
    data: dict
    logs: List[dict]
    receipts: dict
    transaction_hashes: List[str]
    txs_gas_data: Dict[str, dict]

    def get_filtered_calls(self, hash: str) -> List[BlockCall]:
        return [call for call in self.calls if call.transaction_hash == hash]
