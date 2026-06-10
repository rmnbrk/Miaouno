from pygame import Surface, Color
from pygame.font import Font

from ui.component import UIComponent
from ui.constants import BLACK, DEFAULT_FONT_SIZE
from utils.assets_manager import AssetsManager


class UIText(UIComponent):
    def __init__(self,
                 text: str,
                 text_color: Color | None = BLACK,
                 font: str | None = None,
                 font_size: int = DEFAULT_FONT_SIZE,
                 parent: "UIComponent | None" = None,
                 x: int = 0,
                 y: int = 0,
                 width: int = 0,
                 height: int = 0,
                 background: Color | Surface = None,
                 border: Color | None = None,
                 border_width: int = 0,
                 border_radius: int | tuple[int, int, int, int] = 0,
                 focusable: bool = False,
                 enabled: bool = True,
                 z_index: int = 0,
                 h_align: str = "left",      # left | center | right
                 v_align: str = "top"
                 ):
        super().__init__(parent, x, y, width, height, background, border, border_width, border_radius, focusable, enabled, z_index)

        self.text_color = text_color
        self.font = AssetsManager.get_font(font) if font else Font(None, font_size)

        self.text_surface = self.font.render(text, True, self.text_color)
        if not width: self.width = self.text_surface.get_width()
        if not height: self.height = self.text_surface.get_height()

        self.h_align = h_align
        self.v_align = v_align

    def set_text(self, text: str):
        self.text_surface = self.font.render(text, True, self.text_color)

    def render_self(self, surface: Surface):
        super().render_self(surface)

        gx, gy = self.global_pos
        tw, th = self.text_surface.get_size()

        # Horizontal
        if self.h_align == "center":
            tx = gx + (self.width - tw) // 2
        elif self.h_align == "right":
            tx = gx + self.width - tw
        else:  # left
            tx = gx

        # Vertical
        if self.v_align == "center":
            ty = gy + (self.height - th) // 2
        elif self.v_align == "bottom":
            ty = gy + self.height - th
        else:  # top
            ty = gy

        surface.blit(self.text_surface, (tx, ty))
