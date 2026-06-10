import threading
from abc import ABC, abstractmethod
from enum import Enum, auto

from common.data import PlayerData
from core.card import Card
from utils.observer import Subject
from utils.structures import LinkedList


class SessionState(Enum):
    LOBBY = auto()
    IN_GAME = auto()
    STOPPED = auto()


class GameSession(Subject, ABC):
    def __init__(self):
        super().__init__()

        self._id: str | None = None
        self._session_state = SessionState.LOBBY

        # Lobby
        self._lobby_players: list[PlayerData] = []
        self._players_lock = threading.Lock()
        self._max_player_count: int | None = None

        # Etat du jeu partagé
        self._state_lock = threading.Lock()
        self.current_player_id = None
        self.top_card = None
        self.game_players = None
        self.direction = None
        self.can_counter_uno = None

        # Main du joueur (privée)
        self._hand_lock = threading.Lock()
        self._hand = LinkedList()

        # Dernière erreur qui a eu lieu
        self._last_error: str | None = None

        self._winner_id = None


    def _safe_notify(self):
        try:
            self.notify_observers()
        except Exception as e:
            print("GameSession : observer error ->", e)

    # ---------- Méthodes abstraites ----------

    @abstractmethod
    def create(self, *args, **kwargs):
        pass

    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def stop(self):
        pass

    @abstractmethod
    def play_card(self, card_index: int, chosen_color=None, say_uno=False):
        pass

    @abstractmethod
    def draw_card(self):
        """Request to draw a card from the deck for the current player."""
        pass

    # ---------- Getter ----------

    def get_id(self):
        return self._id

    def get_current_player_id(self):
        with self._state_lock:
            return self.current_player_id

    def get_session_state(self):
        with self._state_lock:
            return self._session_state

    def is_turn(self) -> bool:
        with self._state_lock:
            return self.current_player_id == self._id

    def get_winner_id(self):
        return self._winner_id

    # ---------- Hand ----------

    def get_hand(self) -> tuple[Card, ...]:
        with self._hand_lock:
            return tuple(self._hand)

    # ---------- Lobby ----------

    def add_player(self, player_id: str, player_name: str):
        with self._players_lock:
            self._lobby_players.append(PlayerData(player_id, player_name))
        self._safe_notify()

    def remove_player(self, player_id: str):
        with self._players_lock:
            self._lobby_players = [
                p for p in self._lobby_players if p.id != player_id
            ]
        self._safe_notify()

    def get_lobby_players(self):
        with self._players_lock:
            return tuple(self._lobby_players)

    def get_game_players(self):
        return self.game_players

    def clear_players(self):
        with self._players_lock:
            self._lobby_players.clear()
        self._safe_notify()

    def get_max_player_count(self):
        return self._max_player_count

    # ---------- Méthodes qui sont déclenchées en recevant des messages réseaux ----------

    def on_game_start(self):
        with self._state_lock:
            self._session_state = SessionState.IN_GAME
            self.current_player_id = None
            self.top_card = None
            self.game_players = None
            self.direction = None
            self.can_counter_uno = None

        with self._hand_lock:
            self._hand.clear()

        self._safe_notify()

    def on_game_end(self, data):
        print(f"[SESSION] Game ended => Winner : {data["winner_id"]}")
        self._winner_id = data["winner_id"]

        self._safe_notify()

    def on_update_game_state(self, data: dict):
        state = data.get("state")
        if not isinstance(state, dict):
            return

        with self._state_lock:
            self.current_player_id = state.get("current_player_id")
            self.top_card = state.get("top_card")
            self.game_players = state.get("players")
            self.direction = state.get("direction")
            self.can_counter_uno = state.get("can_counter_uno")

        extra = f" | current={state.get('current_player_id')} top={state.get('top_card')} dir={state.get('direction')}"
        print(f"[HOST_SESSION->NET] Received updated game sate -> {extra}")
        self._safe_notify()

    def on_update_hand(self, data: dict):
        cards = data.get("cards")
        if not isinstance(cards, list):
            return

        with self._hand_lock:
            self._hand.clear()
            for c in cards:
                self._hand.append(Card.from_dict(c))

        print(f"[SESSION] Received updated private hand => {len(cards)}")
        self._safe_notify()

    # ---------- Errors ----------
    def on_game_error(self, reason: str):
        self._last_error = reason
        self._safe_notify()
