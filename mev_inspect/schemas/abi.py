from enum import Enum
from typing import List, Union
from typing_extensions import Literal

from pydantic import BaseModel


class ABIDescriptionType(str, Enum):
    function = "function"
    constructor = "constructor"
    fallback = "fallback"
    event = "event"
    receive = "receive"


NON_FUNCTION_DESCRIPTION_TYPES = Union[
    Literal[ABIDescriptionType.constructor],
    Literal[ABIDescriptionType.fallback],
    Literal[ABIDescriptionType.event],
    Literal[ABIDescriptionType.receive],
]


class ABIDescriptionInput(BaseModel):
    name: str
    type: str


class ABIGenericDescription(BaseModel):
    type: NON_FUNCTION_DESCRIPTION_TYPES


class ABIFunctionDescription(BaseModel):
    type: Literal[ABIDescriptionType.function]
    name: str
    inputs: List[ABIDescriptionInput]


ABIDescription = Union[ABIFunctionDescription, ABIGenericDescription]
ABI = List[ABIDescription]
