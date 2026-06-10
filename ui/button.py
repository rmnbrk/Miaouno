from typing import Callable
from pygame import Color, Surface

from ui.component import UIComponent
from ui.constants import BLACK
from ui.text import UIText
from utils.cursor_manager import CursorManager, CursorState


class UIButton(UIComponent):
    def __init__(self,
                 on_click: Callable[..., None],
                 text: str | None = None,
                 text_color: Color | None = BLACK,
                 hover_text_color: Color | None = BLACK,
                 font: str | None = None,
                 parent: "UIComponent | None" = None,
                 x: int = 0,
                 y: int = 0,
                 width: int = 0,
                 height: int = 0,
                 background: Color | Surface = None,
                 hover_background: Color | Surface = None,
                 border: Color | None = None,
                 border_width: int = 0,
                 border_radius: int | tuple[int, int, int, int] = 0,
                 focusable: bool = False,
                 enabled: bool = True,
                 z_index: int = 0
                 ):
        super().__init__(parent, x, y, width, height, background, border, border_width, border_radius,
                         focusable, enabled, z_index)

        self._on_click_callback = on_click

        self.default_background = background
        self.hover_background = hover_background
        self.default_text_color = text_color
        self.hover_text_color = hover_text_color

        if text:
            self.text = UIText(parent=self, text=text, text_color=text_color, font=font)

            if not self.width:
                self.width = self.text.width + 60
            if not self.height:
                self.height = self.text.height + 30

            self.text.x = (self.width - self.text.width) / 2
            self.text.y = (self.height - self.text.height) / 2
        else:
            self.text = None

    def on_click(self):
        if self._on_click_callback:
            self._on_click_callback()

    def render_self(self, surface):
        if self.hovered:
            CursorManager.set(CursorState.HOVERED)
            if self.hover_background:
                self.background = self.hover_background
        else:
            self.background = self.default_background

        if self.text and self.hover_text_color:
            self.text.color = (self.hover_text_color if self.hovered else self.default_text_color)

        super().render_self(surface)
