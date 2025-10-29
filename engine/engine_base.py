from typing import Self
from abc import ABC, abstractmethod
import runner.codec as codec


class EngineBase(ABC):
    @abstractmethod
    def on_move(self, move: codec.Move) -> None: ...

    @abstractmethod
    def get_move(self) -> codec.Move: ...

    @abstractmethod
    def get_friendly(self) -> codec.Player: ...

    @classmethod
    @abstractmethod
    def make(cls, params: codec.Params) -> Self: ...
