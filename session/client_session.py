import threading

from common.data import HostData
from network.client import Client
from network.messages import build_message, MessageType
from session.game_session import GameSession, SessionState


class ClientSession(GameSession):
    def __init__(self):
        super().__init__()
        self.client: Client | None = None

        self.available_games: dict[str, HostData] = {}
        self._games_lock = threading.Lock()

        self._connected = False

    # ---------- Cycle de vie ----------

    def create(self, client_name: str):
        if self.client:
            return
        self.client = Client(self, client_name)
        self._id = self.client.id

    def start(self):
        if self.client and self._connected:
            self.client.run()

    def stop(self):
        if not self.client:
            return

        try:
            self.client.disconnect()
        finally:
            self.client = None
            self._connected = False
            self._reset_state()

            with self._games_lock:
                self.available_games.clear()

            self._safe_notify()

    def _reset_state(self):
        with self._state_lock:
            self._session_state = SessionState.LOBBY
            self.current_player_id = None
            self.top_card = None
            self.game_players = None
            self.direction = None
            self.can_counter_uno = None

        with self._hand_lock:
            self._hand.clear()

    # ---------- Découverte des parties ----------

    def discover_games(self):
        if self.client and not self._connected:
            self.client.discover()

    def add_available_game(
        self,
        host_id: str,
        ip: str,
        host_name: str,
        max_player_count: int,
    ):
        with self._games_lock:
            if host_id in self.available_games:
                return
            self.available_games[host_id] = HostData(
                ip, host_name, max_player_count
            )

        self._safe_notify()

    def get_available_games(self):
        with self._games_lock:
            return dict(self.available_games)

    # ---------- Connexion ----------

    def connect(self, host_id: str) -> bool:
        if not self.client:
            return False

        success, reason = self.client.connect_host(host_id)
        if not success:
            print("[CLIENT_SESSION] Connection failed ->", reason)
            return False

        with self._games_lock:
            host = self.available_games.get(host_id)
            if host:
                self._max_player_count = host.max_player_count

        self._connected = True
        self._reset_state()
        self._safe_notify()
        return True

    # ---------- Action de la partie ----------

    def play_card(self, card_index: int, chosen_color=None, say_uno=False):
        print("[CLIENT_SESSION->NET] Request playing card")

        if (
            not self.client
            or not self._connected
            or self.get_session_state() != SessionState.IN_GAME
        ):
            return

        if card_index < 0:
            return

        self.client.send(
            build_message(
                MessageType.GAME_ACTION_PLAY_CARD,
                card_index=card_index,
                chosen_color=chosen_color,
                say_uno=say_uno,
            )
        )

    def draw_card(self):
        print("[CLIENT_SESSION->NET] Request draw card")

        if (
            not self.client
            or not self._connected
            or self.get_session_state() != SessionState.IN_GAME
        ):
            return

        self.client.send(
            build_message(
                MessageType.GAME_ACTION_DRAW,
            )
        )
