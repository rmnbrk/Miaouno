from session.client_session import ClientSession
from session.game_session import GameSession
from session.host_session import HostSession
from states.game_state_manager import GameStateManager


class GameContext:
    def __init__(self):
        self.state_manager = GameStateManager()
        self.session: GameSession | None = None

    def start_client(self, player_name: str):
        self.stop_session()
        self.session = ClientSession()
        self.session.create(player_name)

    def start_host(self, host_name: str, max_player_count: int):
        self.stop_session()
        self.session = HostSession()
        self.session.create(host_name, max_player_count)
        self.session.start()

    def stop_session(self):
        if self.session:
            self.session.stop()
            self.session = None
