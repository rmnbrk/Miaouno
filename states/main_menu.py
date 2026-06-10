from pygame import Color

from game_context import GameContext
from states.create_game_menu import CreateGameMenu
from states.menu import Menu
from states.pre_find_game_menu import PreFindGameMenu
from states.game_state_manager import GameStateManager
from ui.button import UIButton
from ui.component import UIComponent
from ui.constants import ROSE_2, WHITE
from utils.assets_manager import AssetsManager


class MainMenu(Menu):
    def __init__(self, context: GameContext):
        super().__init__(context)
        self.title = UIComponent(parent=self.root, background=AssetsManager.get_image("logo"), y=-30)
        self.title.x = 1280 / 2 - self.title.width / 2

        self.new_game_btn = UIButton(parent=self.root, on_click=self.create_game,
                                     x=1280 // 2 - 180, y=425, width=320, height=80,
                                     background=ROSE_2, hover_background=WHITE,
                                     text="Créer une nouvelle partie", text_color=Color(0, 0, 0),
                                     hover_text_color=ROSE_2, font="lilita_one_m", border_radius=15)

        self.find_game_btn = UIButton(parent=self.root,
                                      on_click=self.find_game,
                                      x=1280 // 2 - 180, y=525, width=320, height=80,
                                      background=ROSE_2, hover_background=WHITE,
                                      text="Trouver une partie", text_color=Color(0, 0, 0),
                                      hover_text_color=ROSE_2, font="lilita_one_m", border_radius=15)

    def create_game(self):
        self.context.state_manager.push(CreateGameMenu(self.context))

    def find_game(self):
        self.context.state_manager.push(PreFindGameMenu(self.context))

    def update(self, events, dt):
        super().update(events, dt)
        self.root.handle_events(events)

    def render(self, screen):
        self.root.render(screen)
