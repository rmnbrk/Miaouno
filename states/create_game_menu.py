from pygame import Color

from common.constants import MAX_PLAYER_COUNT
from constants import SCREEN_WIDTH
from states.game_state_manager import GameStateManager
from states.menu import Menu
from states.wait_players_menu import WaitPlayersMenu
from ui.button import UIButton
from ui.component import UIComponent
from ui.constants import ROSE_2, WHITE, BLACK
from ui.text import UIText
from ui.text_input import UITextInput
from utils.assets_manager import AssetsManager


class CreateGameMenu(Menu):
    def __init__(self, context):
        super().__init__(context)
        self.title = UIText(parent=self.root, text="Créer une partie", text_color=BLACK, font="lilita_one_xl",
                            x=1280 // 2, y=50)
        self.title.x = 1280 / 2 - self.title.width / 2

        # Nom du joueur
        self.player_label = UIText(parent=self.root, x=SCREEN_WIDTH // 2, y=200, text="Nom du joueur :",
                                   font="lilita_one_m", text_color=BLACK)
        self.player_label.x -= 250
        self.player_name_input = UITextInput(parent=self.root, x=SCREEN_WIDTH // 2, y=250, width=500, height=50,
                                             background=ROSE_2, text_color=BLACK, border_radius=12, font="lilita_one_m")
        self.player_name_input.x -= self.player_name_input.width / 2

        # Nombre de joueurs .max
        self.max_player_label = UIText(parent=self.root, x=SCREEN_WIDTH // 2, y=350, text="Nombre de joueurs .max :",
                                   font="lilita_one_m", text_color=BLACK)
        self.max_player_label.x -= 250
        self.max_players_input = UITextInput(parent=self.root, x=SCREEN_WIDTH // 2, y=400, width=500, height=50,
                                             background=ROSE_2, text_color=BLACK, border_radius=12, font="lilita_one_m",
                                             validator=lambda s: s.isdigit() and 2 <= int(s) <= MAX_PLAYER_COUNT or s == "")
        self.max_players_input.x -= self.max_players_input.width / 2

        self.create_game_btn = UIButton(
            parent=self.root, text="Créer", background=ROSE_2, text_color=Color(0, 0, 0),
            hover_background=WHITE, hover_text_color=ROSE_2,
            font="lilita_one_m", border_radius=12, x=1280 // 2 - 180, y=525, width=320,
            height=80, on_click=self.create_game
        )

        self.back_btn = UIButton(parent=self.root, on_click=self.back, x=30, y=30,
                                 background=AssetsManager.get_image("arrow_back"), border_radius=12)

    def back(self):
        self.context.state_manager.pop()

    def create_game(self):
        if len(self.player_name_input.value) > 0 and len(self.max_players_input.value):
            self.context.start_host(self.player_name_input.value, int(self.max_players_input.value))
            self.context.state_manager.push(WaitPlayersMenu(self.context))

    def update(self, events, dt):
        self.root.handle_events(events)

    def render(self, screen):
        self.root.render(screen)
