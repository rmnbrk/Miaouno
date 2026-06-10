from abc import abstractmethod, ABC

from pygame import Surface
from pygame.event import Event

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from game_context import GameContext


class GameState(ABC):
    def __init__(self, context: "GameContext"):
        self.context = context

    @abstractmethod
    def update(self, events: list[Event], dt: float):
        pass

    @abstractmethod
    def render(self, screen: Surface):
        pass

    def __str__(self):
        return self.__class__.__name__
