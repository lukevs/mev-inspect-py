from abc import ABC, abstractmethod
from typing import Optional

from mev_inspect.schemas import Action, NestedTrace


class Inspector(ABC):
    @abstractmethod
    def inspect(self, trace: NestedTrace) -> Optional[Action]:
        pass
