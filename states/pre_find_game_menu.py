from pygame import Color

from constants import SCREEN_WIDTH
from game_context import GameContext
from session.client_session import ClientSession
from states.game_state_manager import GameStateManager
from states.find_game_menu import FindGameMenuClient
from states.menu import Menu
from ui.button import UIButton
from ui.constants import ROSE_2, WHITE, BLACK
from ui.text import UIText
from ui.text_input import UITextInput
from utils.assets_manager import AssetsManager


class PreFindGameMenu(Menu):
    def __init__(self, context: GameContext):
        super().__init__(context)
        
        self.title = UIText(parent=self.root, text="Trouver une partie", text_color=BLACK, font="lilita_one_xl",
                            x=1280 // 2, y=50, )
        self.title.x = 1280 / 2 - self.title.width / 2

        # Nom du joueur
        self.player_label = UIText(parent=self.root, x=SCREEN_WIDTH // 2, y=275, text="Nom du joueur :",
                                   font="lilita_one_m", text_color=BLACK)
        self.player_label.x -= 250
        self.player_name_input = UITextInput(parent=self.root, x=SCREEN_WIDTH // 2, y=325, width=500, height=50,
                                             background=ROSE_2, text_color=BLACK, border_radius=12, font="lilita_one_m")
        self.player_name_input.x -= self.player_name_input.width / 2

        self.continue_btn = UIButton(parent=self.root, text="Continuer", background=ROSE_2, text_color=Color(0, 0, 0),
                                     hover_background=WHITE, hover_text_color=ROSE_2,
                                     font="lilita_one_m", border_radius=12, x=1280 // 2 - 180, y=525, width=320,
                                     height=80, on_click=self.find_game)

        self.back_btn = UIButton(parent=self.root, on_click=lambda: self.context.state_manager.pop(), x=30, y=30,
                                 background=AssetsManager.get_image("arrow_back"), border_radius=12)

    def find_game(self):
        if len(self.player_name_input.value) > 0:
            self.context.start_client(self.player_name_input.value)
            if isinstance(self.context.session, ClientSession):
                self.context.session.discover_games()
                self.context.state_manager.push(FindGameMenuClient(self.context))

    def update(self, events, dt):
        super().update(events, dt)
        self.root.handle_events(events)

    def render(self, screen):
        self.root.render(screen)
