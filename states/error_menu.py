from pygame import Color

from states.game_state import GameState

from ui.button import UIButton
from ui.component import UIComponent
from ui.constants import ROSE_2, ROSE_1, WHITE, BLACK
from ui.text import UIText


class ErrorMenu(GameState):
    def __init__(self, context, name: str, description: str):
        super().__init__(context)
        self.root = UIComponent(width=1280, height=720, background=ROSE_1)

        self.title = UIText(parent=self.root, text=name, text_color=BLACK, font="lilita_one_l",
                            x=1280 // 2, y=50)
        self.title.x = 1280 / 2 - self.title.width / 2

        self.subtitle = UIText(parent=self.root, text=description, text_color=BLACK, font="lilita_one_m",
                            x=1280 // 2, y=180)
        self.subtitle.x = 1280 / 2 - self.subtitle.width / 2

        self.create_game_btn = UIButton(parent=self.root, text="Revenir à la liste des parties", background=ROSE_2, text_color=Color(0, 0, 0),
                                        hover_background=WHITE, hover_text_color=ROSE_2,
                                        font="lilita_one_m", border_radius=12, x=1280 // 2 - 180, y=525, width=320,
                                        height=80, on_click=lambda: self.context.state_manager.pop())

    def update(self, events, dt):
        self.root.handle_events(events)

    def render(self, screen):
        self.root.render(screen)
