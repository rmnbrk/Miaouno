from pygame import Surface
from pygame.event import Event

from constants import SCREEN_WIDTH, SCREEN_HEIGHT
from states.game_state import GameState
from ui.component import UIComponent
from ui.constants import ROSE_1
from utils.observer import Observer
from threading import Event as ThreadEvent


class Menu(GameState, Observer):
    def __init__(self, context):
        super().__init__(context)
        self.root = UIComponent(width=SCREEN_WIDTH, height=SCREEN_HEIGHT, background=ROSE_1)
        self.needs_refresh = ThreadEvent()

    def notify(self):
        """
            Le modèle nous informe qu'il y a besoin d'un refresh.
            On ne modifie pas l'affichage directement, car Pygame n'est pas thread safe.
            L'affichage sera modifié à la frame suivante
        """
        self.needs_refresh.set()

    def refresh(self):
        pass

    def update(self, events: list[Event], dt: float):
        if self.needs_refresh.is_set():
            self.needs_refresh.clear()
            self.refresh()

    def render(self, screen: Surface):
        pass
