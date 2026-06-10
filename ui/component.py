from pygame import Color, Surface
import pygame
from pygame.rect import Rect
from pygame.event import Event

from ui.focus_manager import UIFocusManager


class UIComponent:
    def __init__(
            self,
            parent: "UIComponent | None" = None,
            x: int = 0,
            y: int = 0,
            width: int = 0,
            height: int = 0,
            background: Color | Surface = None,
            border: Color | None = None,
            border_width: int = 1,
            border_radius: int | tuple[int, int, int, int] = 0,
            focusable: bool = False,
            enabled: bool = True,
            z_index: int = 0,
            padding: int = 0,          # 👈 NOUVEAU
    ):
        self.parent = parent
        self.children: list[UIComponent] = []
        if parent:
            parent.children.append(self)

        self.x = x
        self.y = y
        self.width = width
        self.height = height

        self.background = background

        self.border = border
        self.border_width = border_width
        self.border_radius = border_radius

        self.focusable = focusable
        self.enabled = enabled
        self._pressed = False

        self.z_index = z_index

        self.padding = padding

        if isinstance(self.background, Surface):
            if not self.width:
                self.width = self.background.get_width()
            if not self.height:
                self.height = self.background.get_height()

        self.scrollable = False
        self.scroll_y = 0
        self.scroll_speed = 30
        self.content_height = height

    # -------------------------------------------------

    def clear_children(self):
        self.children = []

    def update_content_height(self):
        if not self.children:
            self.content_height = self.height
            return

        max_bottom = 0
        for child in self.children:
            bottom = child.y + child.height
            max_bottom = max(max_bottom, bottom)

        self.content_height = max_bottom + self.padding * 2

    # -------------------------------------------------

    @property
    def global_pos(self):
        if self.parent:
            px, py = self.parent.global_pos
            return px + self.x, py + self.y
        return self.x, self.y

    @property
    def can_scroll(self) -> bool:
        return self.scrollable and self.content_height > self.height

    # -------------------------------------------------

    def handle_events(self, events: list[Event]):
        if not self.enabled:
            return

        for child in self.children:
            child.handle_events(events)

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.hovered:
                    self._pressed = True
                    if self.focusable:
                        UIFocusManager.set(self)
                else:
                    if UIFocusManager.is_focused(self):
                        UIFocusManager.clear()

            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if self._pressed and self.hovered:
                    self.on_click()
                self._pressed = False

            if self.can_scroll and event.type == pygame.MOUSEWHEEL and self.hovered:
                self.scroll_y += event.y * self.scroll_speed
                self.scroll_y = max(
                    min(self.scroll_y, 0),
                    self.height - self.content_height
                )

    # -------------------------------------------------

    def on_click(self):
        pass

    # -------------------------------------------------

    def render(self, surface):
        gx, gy = self.global_pos

        outer_rect = Rect(
            gx - self.border_width,
            gy - self.border_width,
            self.width + self.border_width * 2,
            self.height + self.border_width * 2
        )

        inner_rect = Rect(
            gx + self.padding,
            gy + self.padding,
            self.width - self.padding * 2,
            self.height - self.padding * 2
        )

        if self.border:
            pygame.draw.rect(
                surface,
                self.border,
                outer_rect,
                width=self.border_width,
                border_radius=self.border_radius
            )

        if self.scrollable:
            previous_clip = surface.get_clip()
            surface.set_clip(inner_rect)

            self.render_self(surface)
            self.render_children(surface)

            surface.set_clip(previous_clip)
        else:
            self.render_self(surface)
            self.render_children(surface)

    # -------------------------------------------------

    def render_self(self, surface: Surface):
        gx, gy = self.global_pos
        rect = Rect(gx, gy, self.width, self.height)

        if isinstance(self.border_radius, tuple):
            radius_kwargs = {
                "border_top_left_radius": max(0, self.border_radius[0] - self.border_width),
                "border_top_right_radius": max(0, self.border_radius[1] - self.border_width),
                "border_bottom_right_radius": max(0, self.border_radius[2] - self.border_width),
                "border_bottom_left_radius": max(0, self.border_radius[3] - self.border_width),
            }
        else:
            radius_kwargs = {
                "border_radius": max(0, self.border_radius - self.border_width)
            }

        if isinstance(self.background, Color):
            pygame.draw.rect(
                surface,
                self.background,
                rect,
                width=0,
                **radius_kwargs
            )
        elif isinstance(self.background, Surface):
            surface.blit(self.background, rect.topleft)

    # -------------------------------------------------

    def render_children(self, surface):
        self.children.sort(key=lambda c: c.z_index)

        for child in self.children:
            child_x_backup = child.x
            child_y_backup = child.y

            child.x += self.padding

            if self.scrollable:
                child.y += self.scroll_y + self.padding
            else:
                child.y += self.padding

            child.render(surface)

            child.x = child_x_backup
            child.y = child_y_backup

    # -------------------------------------------------

    @property
    def hovered(self) -> bool:
        x, y = self.global_pos
        mx, my = pygame.mouse.get_pos()
        return x <= mx <= x + self.width and y <= my <= y + self.height
