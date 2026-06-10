from pygame import Surface
from pygame.event import Event

from constants import SCREEN_WIDTH, SCREEN_HEIGHT
from core.card import Card, Value, Color
from core.player import Player
from states.end_game_menu import EndGameMenu
from states.menu import Menu
from ui.card import UICard
from ui.text import UIText
from ui.button import UIButton
from ui.component import UIComponent
from ui.constants import RED, BLUE, GREEN, YELLOW, ROSE_2, ROSE_1, WHITE, WILD
from utils.assets_manager import AssetsManager


class GamePlay(Menu):
    def __init__(self, context):
        super().__init__(context)
        self.top_container = None
        # S'abonner aux mises à jour de session pour rafraîchir l'UI au bon moment
        self.context.session.add_observer(self)
        # Overlay de sélection de couleur (si ouvert)
        self._color_overlay = None
        self._pending_card_index = None
        self.players = []

        self.init_helper_text()
        self.init_cards()
        self.init_top_card()
        self.display_players()
        self.display_uno_direction()

    def init_helper_text(self):
        if self.context.session.is_turn():
            UIText(parent=self.root, text="C'est votre tour", font="lilita_one_m", x=20, y=120)
        else:
            UIText(parent=self.root, text="Ce n'est pas votre tour", font="lilita_one_m", x=20, y=120)

    def init_top_card(self):
        top = self.context.session.top_card
        if not top:
            return
        try:
            card = Card.from_dict(top)
        except Exception:
            return
        top_width, top_height = 140, 186
        x = int((SCREEN_WIDTH - top_width) / 2)
        y = 210
        try:
            verso_img = AssetsManager.get_image("verso")
            for i in range(3):
                draw_card = UICard(
                    parent=self.root,
                    x=int(x - verso_img.get_width() - 20) - 90 + i * 10,
                    y=y + i * 10,
                    card=Card(Color.WILD, Value.VERSO),
                    width=top_width,
                    height=top_height,
                    on_click=self.on_click_draw,
                    border=WHITE,
                )
                draw_card.set_playable(self.context.session.is_turn())
        except Exception:
            pass

        UICard(
            parent=self.root,
            card=card,
            x=x,
            y=y,
            width=top_width,
            height=top_height,
            on_click=lambda: None,
        )

    def init_cards(self):
        card_width = 100
        card_height = 140
        spacing_x = 20
        spacing_y = 30
        cards_per_row = 9

        cards_container = UIComponent(
            parent=self.root,
            y=500,
            width=self.root.width,
            height=card_height + spacing_y
        )
        cards_container.scrollable = True
        cards_container.scroll_speed = card_height + spacing_y

        hand = self.context.session.get_hand()

        for i, card in enumerate(hand):
            row = i // cards_per_row
            col = i % cards_per_row

            line_count = min(cards_per_row, len(hand) - row * cards_per_row)
            total_width = line_count * card_width + (line_count - 1) * spacing_x
            start_x = (cards_container.width - total_width) // 2

            x = start_x + col * (card_width + spacing_x)
            y = row * (card_height + spacing_y)

            ui_card = UICard(
                parent=cards_container,
                card=card,
                x=x,
                y=y,
                on_click=lambda idx=i, c=card: self.on_click_card(idx, c)
            )

            ui_card.set_playable(
                card.is_playable_on(Card.from_dict(self.context.session.top_card))
                and self.context.session.is_turn()
            )

        cards_container.update_content_height()

    def on_click_card(self, index: int, card: Card):
        if not self.context.session.is_turn():
            return
        # Si joker (wild ou +4) on ouvre sélecteur de couleur
        if card.color == Color.WILD:
            self.open_color_picker(index)
            return
        # Sinon, on joue directement
        self.context.session.play_card(index, None, False)

    def open_color_picker(self, card_index: int):
        # Ferme overlay existant
        self.close_color_picker()
        self._pending_card_index = card_index

        overlay_w, overlay_h = 520, 200  # un peu plus grand

        # Overlay centré à l'écran
        self._color_overlay = UIComponent(
            parent=self.root,
            x=(SCREEN_WIDTH - overlay_w) // 2,
            y=(SCREEN_HEIGHT - overlay_h) // 2,
            width=overlay_w,
            height=overlay_h,
            background=ROSE_2,
            border_radius=12
        )

        # Texte titre
        UIText(
            parent=self._color_overlay,
            text="Choisissez la couleur à jouer",
            font="lilita_one_m",
            x=20,
            y=25,
        )

        # Boutons
        btn_w, btn_h = 80, 80
        gap = 20
        total_btn_width = 4 * btn_w + 3 * gap

        start_x = (overlay_w - total_btn_width) // 2
        y = 90  # sous le texte

        colors = [
            ("red", RED),
            ("blue", BLUE),
            ("green", GREEN),
            ("yellow", YELLOW),
        ]

        for i, (name, color) in enumerate(colors):
            UIButton(
                parent=self._color_overlay,
                x=start_x + i * (btn_w + gap),
                y=y,
                width=btn_w,
                height=btn_h,
                background=color,
                border_width=2,
                border_radius=12,
                on_click=lambda c=name: self._pick_color(c)
            )

    def _pick_color(self, color_str: str):
        if self._pending_card_index is not None:
            self.context.session.play_card(self._pending_card_index, color_str, False)
        self.close_color_picker()

    def close_color_picker(self):
        if self._color_overlay:
            try:
                self.root.children.remove(self._color_overlay)
            except ValueError:
                pass
            self._color_overlay = None
            self._pending_card_index = None

    def on_click_draw(self):
        # On permet le fait de tirer une carte de la pioche que si c'est notre tour
        if self.context.session.is_turn():
            try:
                self.context.session.draw_card()
            except AttributeError:
                pass

    def display_players(self) -> None:
        """Affiche les joueurs avec leur nom"""
        self.players = self.context.session.get_game_players()
        print(self.players)

        self.top_container = UIComponent(
            parent=self.root,
            width=SCREEN_WIDTH,
            height=105,
            background=ROSE_2
        )

        UIText(
            parent=self.top_container,
            text="Joueurs :",
            font="lilita_one_m",
            x=40,
            y=35
        )

        max_per_row = 5
        spacing_x = 120
        item_width = 120
        y = 25

        players = self.players[:max_per_row]
        count = len(players)

        total_width = count * item_width + (count - 1) * spacing_x
        start_x = (SCREEN_WIDTH - total_width) // 2

        for i, player in enumerate(players):
            x = start_x + i * (item_width + spacing_x)

            player_name = UIText(
                parent=self.top_container,
                text=f"{player["name"]} : {player["card_count"]}",
                font="lilita_one_m",
                font_size=40,
                x=x,
                y=y,
                width=item_width,
                height=50,
                background=ROSE_1,
                border_radius=12,
                h_align="center",
                v_align="center"
            )

    def display_counter_uno_button(self) -> None:
        try:
            contre_uno_img = AssetsManager.get_image("contre_uno")
            UIButton(
                parent=self.root,
                x=265,
                y=215,
                width=50,
                height=50,
                background=contre_uno_img,
                border_width=0,
                on_click=lambda: print("Counter uno")
            )
        except Exception:
            pass

    def display_uno_button(self) -> None:
        try:
            uno_img = AssetsManager.get_image("uno")
            UIButton(
                parent=self.root,
                x=750,
                y=215,
                width=50,
                height=50,
                background=uno_img,
                border_width=0,
                on_click=lambda: print("Uno")
            )
        except Exception:
            pass

    def display_uno_direction(self) -> None:
        x = SCREEN_WIDTH - 300
        y = 35
        width = 50
        height = 50

        UIText(parent=self.top_container, x=x, y=y, text="Sens du jeu : ", font="lilita_one_m")

        direction = self.context.session.direction
        if direction == 1:
            clockwise_img = AssetsManager.get_image("clockwise")
            UIComponent(
                parent=self.root,
                x=x + 150,
                width=width,
                height=height,
                background=clockwise_img,
                border_width=0,
            )
        elif direction == -1:
            anticlockwise_img = AssetsManager.get_image("anticlockwise")
            UIComponent(
                parent=self.root,
                x=x + 125,
                width=width,
                height=height,
                background=anticlockwise_img,
                border_width=0,
            )

    def refresh(self):
        self.root.clear_children()

        if self.context.session.get_winner_id():
            is_winner = self.context.session.get_winner_id() == self.context.session.get_id()
            self.context.state_manager.pop()
            self.context.state_manager.push(EndGameMenu(self.context, is_winner))

        self.init_helper_text()
        self.init_cards()
        self.init_top_card()
        self.display_players()
        self.display_uno_direction()

    def update(self, events: list[Event], dt: float):
        super().update(events, dt)
        self.root.handle_events(events)

    def render(self, screen: Surface):
        self.root.render(screen)
