from enum import Enum
from typing import List, Optional

from pydantic import BaseModel


class ABIDescriptionType(Enum):
    function = "function"
    constructor = "constructor"
    fallback = "fallback"
    event = "event"
    receive = "receive"


class ABIDescriptionInput(BaseModel):
    name: str
    type: str


class ABIDescription(BaseModel):
    type: ABIDescriptionType
    name: Optional[str]
    inputs: Optional[List[ABIDescriptionInput]]


ABI = List[ABIDescription]
