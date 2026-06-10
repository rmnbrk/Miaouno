import time

from common.constants import MAX_PLAYER_COUNT
from constants import SCREEN_WIDTH
from session.game_session import SessionState
from session.host_session import HostSession
from states.gameplay import GamePlay
from states.menu import Menu
from ui.button import UIButton
from ui.component import UIComponent
from ui.constants import ROSE_2, ROSE_1, BLACK, WHITE
from ui.text import UIText


class WaitPlayersMenu(Menu):
    def __init__(self, context):
        super().__init__(context)
        self._last_state = None

        self.context.session.add_observer(self)

        self.container = UIComponent(parent=self.root, background=ROSE_2, width=400, height=425, border_radius=12,
                                     y=150, border=BLACK, border_width=5)
        self.container.x = SCREEN_WIDTH / 2 - self.container.width / 2
        self.container.scrollable = True

        self.subtitle = UIText(parent=self.root,
                               text=f"En attente de joueurs ... (1/{self.context.session.get_max_player_count()})",
                               text_color=BLACK, font="lilita_one_l", x=1280 // 2, y=50)
        self.subtitle.x = 1280 / 2 - self.subtitle.width / 2

        self.init_players_list()

        if isinstance(self.context.session, HostSession):
            self.init_host_buttons()

    def init_players_list(self):
        players = self.context.session.get_lobby_players()
        i = 0
        self.container.clear_children()
        for player in players:
            UIText(parent=self.container, x=12, y=12 + i * 75, width=375, height=50, border_radius=12,
                   text=player.name, font="lilita_one_m", text_color=BLACK, background=ROSE_1, v_align="center", h_align="center")
            i += 1
        self.container.update_content_height()

    def init_host_buttons(self):
        launch_btn = UIButton(parent=self.root, text="Lancer la partie", font="lilita_one_m", background=ROSE_2,
                              hover_background=WHITE, hover_text_color=ROSE_1, on_click=self.launch_game, y=610,
                              border_radius=12)
        launch_btn.x = self.root.width / 2 - launch_btn.width / 2

    def launch_game(self):
        if isinstance(self.context.session, HostSession) and len(self.context.session.get_lobby_players()) >= 2:
            self.context.session.start_game()

    def refresh(self):
        state = self.context.session.get_session_state()

        if state != self._last_state:
            self._last_state = state

            if state == SessionState.IN_GAME:
                self.context.state_manager.push(GamePlay(self.context))
                return

        if state == SessionState.LOBBY:
            self.subtitle.set_text(
                f"En attente de joueurs ... "
                f"({len(self.context.session.get_lobby_players())}/"
                f"{self.context.session.get_max_player_count()})"
            )
            self.init_players_list()

    def update(self, events, dt):
        super().update(events, dt)
        self.root.handle_events(events)

    def render(self, screen):
        self.root.render(screen)
