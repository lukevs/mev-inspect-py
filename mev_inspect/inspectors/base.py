from abc import ABC, abstractmethod
from typing import List


class Inspector(ABC):
    @abstractmethod
    def inspect(self, calls: List[dict]):
        pass
