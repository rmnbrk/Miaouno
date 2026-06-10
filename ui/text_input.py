from collections.abc import Callable

import pygame
from pygame import Color, Surface
from pygame.event import Event
from pygame.rect import Rect
from pygame_textinput import TextInputVisualizer, TextInputManager

from ui.component import UIComponent
from ui.constants import BLACK
from ui.focus_manager import UIFocusManager
from utils.assets_manager import AssetsManager
from utils.cursor_manager import CursorManager, CursorState


class UITextInput(UIComponent):
    def __init__(self,
                 text_color: Color | None = BLACK,
                 font: str | None = None,
                 focus_border_color: Color | None = BLACK,
                 validator: Callable[..., bool] = lambda x: True,
                 parent: "UIComponent | None" = None,
                 x: int = 0,
                 y: int = 0,
                 width: int = 0,
                 height: int = 0,
                 background: Color | Surface = None,
                 border: Color | None = None,
                 border_width: int = 1,
                 border_radius: int | tuple[int, int, int, int] = 0,
                 enabled: bool = True,
                 z_index: int = 0
                 ):
        super().__init__(parent, x, y, width, height, background, border, border_width, border_radius,
                         True, enabled, z_index)

        self.text_manager = TextInputManager(validator=validator)
        self.text_input = TextInputVisualizer(manager=self.text_manager, font_object=AssetsManager.get_font(font),
                                              font_color=text_color,
                                              antialias=True)

        self.focus_border_color = focus_border_color

    @property
    def value(self):
        return self.text_input.value

    def handle_events(self, events: list[Event]):
        super().handle_events(events)

        if UIFocusManager.is_focused(self):
            self.text_input.update(events)

        if self.hovered:
            CursorManager.set(CursorState.HOVERED)

    def render(self, surface: Surface):
        super().render_self(surface)

        gx, gy = self.global_pos
        surface.blit(self.text_input.surface, (gx + 8, gy + 8))

        # Bordure focus
        if UIFocusManager.is_focused(self):
            pygame.draw.rect(
                surface,
                self.focus_border_color,
                Rect(gx, gy, self.width, self.height),
                5,
                border_radius=self.border_radius,
            )
