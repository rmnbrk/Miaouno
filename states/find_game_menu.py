from constants import SCREEN_WIDTH
from game_context import GameContext
from session.client_session import ClientSession
from states.error_menu import ErrorMenu
from states.menu import Menu
from states.wait_players_menu import WaitPlayersMenu
from ui.button import UIButton
from ui.component import UIComponent
from ui.constants import ROSE_2, ROSE_1, BLACK, WHITE
from ui.text import UIText


class FindGameMenuClient(Menu):
    def __init__(self, context: GameContext):
        super().__init__(context)
        self.context.session.add_observer(self)

        self.subtitle = UIText(parent=self.root, text="Parties trouvées :", text_color=BLACK, font="lilita_one_l", x=1280 // 2, y=50)
        self.subtitle.x = 1280 / 2 - self.subtitle.width / 2

        self.games_list = UIComponent(parent=self.root, background=ROSE_2, width=500, height=500, border_radius=12, y=175)
        self.games_list.x = SCREEN_WIDTH / 2 - self.games_list.width / 2

    def init_games_list(self):
        if isinstance(self.context.session, ClientSession):
            games = self.context.session.get_available_games()
            i = 0
            for host_id, game in games.items():
                button = UIButton(parent=self.root, background=ROSE_1, hover_background=WHITE, x=SCREEN_WIDTH // 2, y=200 + i * 25, width=450, height=90, text=f"Partie de {game.name}",
                                  text_color=BLACK, font="lilita_one_m", on_click=lambda h=host_id: self.connect(h), border_radius=12)
                button.x -= button.width / 2

    def connect(self, host_id: str):
        if isinstance(self.context.session, ClientSession):
            success = self.context.session.connect(host_id)
            if success:
                self.context.session.start()
                self.context.state_manager.push(WaitPlayersMenu(self.context))
            else:
                self.context.state_manager.push(ErrorMenu(self.context, "Erreur lors de la connexion", ""))

    def refresh(self):
        self.init_games_list()

    def update(self, events, dt):
        super().update(events, dt)
        self.root.handle_events(events)

    def render(self, screen):
        self.root.render(screen)
