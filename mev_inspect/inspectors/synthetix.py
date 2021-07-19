import json
from typing import Optional, Tuple

from mev_inspect.config import load_config
from mev_inspect.schemas import NestedTrace, Trace, TraceType
from mev_inspect.schemas.actions import Action, SynthetixBurn

from .base import Inspector

config = load_config()
SYNTHETIX_ABI = json.loads(config["ABI"]["Synthetix"])
SYNTHETIX_PROXY_TOKEN_ADDRESS = "0xC011a73ee8576Fb46F5E1c5751cA3B9Fe0af2a6F"
BURN_SYNTHS_FUNCTION = "burnSynths"


class SynthetixInspector(Inspector):
    def __init__(self, w3):
        self.token_contract = w3.eth.contract(
            abi=SYNTHETIX_ABI,
            address=SYNTHETIX_PROXY_TOKEN_ADDRESS,
        )

    def inspect(self, nested_trace: NestedTrace) -> Optional[Action]:
        trace = nested_trace.trace

        if self._is_token_call(trace):
            decoded = self._try_token_decode(trace.action["input"])

            if decoded is None:
                return None

            (func, inputs) = decoded

            if func.fn_name == BURN_SYNTHS_FUNCTION:
                return SynthetixBurn(
                    trace=trace,
                    amount=inputs["amount"],
                )

        return None

    @staticmethod
    def _is_token_call(trace: Trace) -> bool:
        return (
            trace.type == TraceType.call
            and trace.action["to"] == SYNTHETIX_PROXY_TOKEN_ADDRESS.lower()
        )

    def _try_token_decode(self, data: str) -> Optional[Tuple]:
        try:
            return self.token_contract.decode_function_input(data=data)
        except ValueError:
            return None
