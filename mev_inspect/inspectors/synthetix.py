from typing import Dict, List, Optional

from pydantic import parse_obj_as
from web3 import Web3

from mev_inspect.abi import get_abi
from mev_inspect.schemas import (
    BlockCall,
    BlockCallType,
    ABIFunctionDescription,
)

from .base import Inspector


SYNTHETIX_PROXY_TOKEN_ADDRESS = "0xC011a73ee8576Fb46F5E1c5751cA3B9Fe0af2a6F"


class SynthetixInspector(Inspector):
    def __init__(self, w3: Web3) -> None:
        self._w3 = w3

        synthetix_abi = get_abi("Synthetix")
        if synthetix_abi is None:
            raise RuntimeError("No ABI found")

        self._synthetix_abi = synthetix_abi
        self._synthetix_functions_by_selector: Dict[str, ABIFunctionDescription] = {
            description.get_selector(): description
            for description in self._synthetix_abi
            if isinstance(description, ABIFunctionDescription)
        }

    def inspect(self, calls: List[dict]):
        typed_calls = [parse_obj_as(BlockCall, call) for call in calls]  # type: ignore
        return self._inspect(typed_calls)

    def _inspect(self, calls: List[BlockCall]):
        for call in calls:
            if (
                call.type == BlockCallType.call
                and call.action.to == SYNTHETIX_PROXY_TOKEN_ADDRESS.lower()
            ):
                function_selector = call.action.get_function_selector()
                function: Optional[
                    ABIFunctionDescription
                ] = self._synthetix_functions_by_selector.get(function_selector)

                if function is not None:
                    print(function)
