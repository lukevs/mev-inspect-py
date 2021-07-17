from typing import List

from pydantic import BaseModel

from .blocks import Trace


class Action(BaseModel):
    trace: Trace


class UnknownAction(BaseModel):
    internal_actions: List[Action]
