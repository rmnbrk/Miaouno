from pygame import Surface
from pygame.event import Event

from states.menu import Menu
from ui.button import UIButton
from ui.component import UIComponent
from ui.constants import ROSE_2, WHITE
from utils.assets_manager import AssetsManager


class EndGameMenu(Menu):
    def __init__(self, context, winner: bool):
        super().__init__(context)
        bg = AssetsManager.get_image("victory") if winner else AssetsManager.get_image("defeat")
        result = UIComponent(parent=self.root, background=bg)
        result.x = self.root.width / 2 - result.width / 2

        main_menu_btn = UIButton(parent=self.root, text="Retourner à l'écran d'accueil", font="lilita_one_m",
                                 background=ROSE_2,
                                 on_click=self.go_to_main_menu, y=450, border_radius=12,
                                 hover_background=WHITE, hover_text_color=ROSE_2)
        main_menu_btn.x = self.root.width / 2 - main_menu_btn.width / 2

    def go_to_main_menu(self):
        # Tant qu'il y a des états autres que le Main Menu, on dépile
        while self.context.state_manager.get_size() != 1:
            self.context.state_manager.pop()

    def update(self, events: list[Event], dt: float):
        self.root.handle_events(events)

    def render(self, screen: Surface):
        self.root.render(screen)
