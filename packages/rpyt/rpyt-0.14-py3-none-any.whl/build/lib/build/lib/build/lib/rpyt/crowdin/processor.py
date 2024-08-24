from abc import ABC, abstractmethod
from typing import Any

from rpyt.crowdin.common import DialogueEntry


class Processor(ABC):
    def __init__(self, **kwargs: Any):
        pass

    @abstractmethod
    def dump(self, dialogue_entry: DialogueEntry):
        pass

    @abstractmethod
    def load(self, value: Any) -> str:
        pass
