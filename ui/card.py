from typing import Callable

from pygame import Surface
from core.card import Color, Card
from ui.button import UIButton
from ui.component import UIComponent
from ui.constants import WHITE
from utils.assets_manager import AssetsManager
import ui
from utils.cursor_manager import CursorManager, CursorState

match_colors = {
    "red": ui.constants.RED,
    "blue": ui.constants.BLUE,
    "green": ui.constants.GREEN,
    "yellow": ui.constants.YELLOW,
    "wild": ui.constants.WILD
}

class UICard(UIButton):
    def __init__(
            self,
            card: Card,
            on_click: Callable[..., None],
            parent: "UIComponent | None" = None,
            x: int = 0,
            y: int = 0,
            width: int = 100,
            height: int = 140,
            border: Color | None = WHITE,
            border_width: int = 3,
            border_radius: int = 15,
            focusable: bool = True,
            enabled: bool = True,
            z_index: int = 0):

        super().__init__(
            parent=parent,
            x=x,
            y=y,
            width=width,
            height=height,
            background=match_colors[card.color.value],
            border=border,
            border_width=border_width,
            border_radius=border_radius,
            focusable=focusable,
            enabled=enabled,
            z_index=z_index,
            on_click=on_click
        )

        self.card = card
        self.symbol = None

        self.load_symbol()

    def load_symbol(self):
        file_name = self.card.value.value
        self.symbol = AssetsManager.get_image(file_name)

    def set_card(self, new_card: Card):
        self.card = new_card
        self.background = match_colors[new_card.color.value]
        self.load_symbol()

    def set_playable(self, value):
        self.enabled = value

    def render_self(self, surface: Surface):
        super().render_self(surface)

        if not self.enabled and self.hovered:
            CursorManager.set(CursorState.FORBIDEN)

        if self.symbol:
            gx, gy = self.global_pos

            symbol_x = gx + (self.width - self.symbol.get_width()) // 2
            symbol_y = gy + (self.height - self.symbol.get_height()) // 2

            surface.blit(self.symbol, (symbol_x, symbol_y))
