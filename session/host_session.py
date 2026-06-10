from threading import Lock

from core.player import Player
from core.uno import Uno
from core.card import Color
from network.host import Host
from network.messages import MessageType, build_message
from session.game_session import GameSession, SessionState


class HostSession(GameSession):
    def __init__(self):
        super().__init__()
        self.host: Host | None = None
        self._uno: Uno | None = None

        self.players_by_id: dict[str, Player] = {}
        self._players_lock = Lock()
        self._game_lock = Lock()
        self.player_names: dict[str, str] = {}

    # ---------- Cycle de vie ----------

    def create(self, host_name: str, max_player_count: int):
        if self.host:
            return

        self._max_player_count = max_player_count
        self.host = Host(self, host_name, max_player_count)
        self._id = self.host.id

        self.add_player(self.host.id, self.host.name)

    def start(self):
        if self.host:
            self.host.run()

    def stop(self):
        if not self.host:
            return

        self.host.close()
        self.host = None

        with self._state_lock:
            self._session_state = SessionState.STOPPED

        self._safe_notify()

    def start_game(self) -> bool:
        with self._game_lock:
            if self._session_state != SessionState.LOBBY:
                return False

            self.players_by_id.clear()

            uno_players = []
            for p in self.get_lobby_players():
                pl = Player()
                self.players_by_id[p.id] = pl
                self.player_names[p.id] = p.name  # 👈 ici
                uno_players.append(pl)

            self._uno = Uno(tuple(uno_players))
            self._uno.start_game()

            # Logs d'initialisation de la partie
            try:
                players_info = ", ".join([f"{p.id}:{p.name}" for p in self.get_lobby_players()])
            except Exception:
                players_info = str([p.id for p in self.get_lobby_players()])
            top = self._uno.get_top_card()
            print(f"[HOST_SESSION] Game started with players: {players_info}")
            if top:
                print(f"[HOST_SESSION] First top card: {top.color.value} {top.value.value}")
            current_index = None
            try:
                current_index = next(i for i, pl in enumerate(self._uno.players) if pl is self._uno.get_current_player())
            except Exception:
                pass
            print(f"[HOST_SESSION] First current player index: {current_index}, direction: {self._uno.direction}")

            self._session_state = SessionState.IN_GAME
            self._sync_from_uno_locked()

            # ORDRE STRICT
            self.send_to_players(MessageType.GAME_START)
            self.send_to_players(
                MessageType.GAME_STATE_UPDATE,
                state=self.serialize_game_state(),
            )

            for pid in self.players_by_id:
                self.send_private_hand(pid)

        self._safe_notify()
        return True

    # ---------- Actions ----------

    def play_card(self, card_index: int, chosen_color=None, say_uno=False):
        return self._apply_play(self._id, card_index, chosen_color, say_uno)

    def draw_card(self):
        return self._apply_draw(self._id)

    def on_game_action_play(self, player_id: str, data: dict):
        success, reason = self._apply_play(
            player_id,
            data["card_index"],
            data.get("chosen_color"),
            data.get("say_uno", False),
        )

        if not success and self.host:
            self.host.send_to(
                player_id,
                build_message(MessageType.GAME_ERROR, reason=reason),
            )

    def on_game_action_draw(self, player_id: str):
        success, reason = self._apply_draw(player_id)
        if not success and self.host:
            self.host.send_to(
                player_id,
                build_message(MessageType.GAME_ERROR, reason=reason),
            )

    def _apply_play(self, player_id: str, card_index: int, chosen_color, say_uno):
        with self._game_lock:
            if self._session_state != SessionState.IN_GAME:
                return False, "Game not running"

            player = self.players_by_id.get(player_id)
            if not player:
                return False, "Unknown player"

            if player is not self._uno.get_current_player():
                return False, "Not your turn"

            # Convert chosen_color (string) to Color enum if provided
            color_enum = None
            if chosen_color is not None:
                try:
                    color_enum = Color(chosen_color) if not isinstance(chosen_color, Color) else chosen_color
                except ValueError:
                    return False, "Invalid color selection"

            # Log avant action
            try:
                card_preview = player.hand.get(card_index)
                preview_txt = f"{card_preview.color.value} {card_preview.value.value}"
            except Exception:
                preview_txt = f"index={card_index} (unavailable)"
            before_pending = getattr(self._uno, "pending_draw", 0)
            print(f"[HOST_SESSION] Play by {player_id}: {preview_txt}, chosen={getattr(color_enum,'value',None)} | pending_draw before={before_pending}")

            try:
                self._uno.play_card(player, card_index, color_enum, say_uno)
            except ValueError as e:
                print(f"[HOST_SESSION] Play rejected for {player_id}: {e}")
                return False, str(e)

            after_pending = getattr(self._uno, "pending_draw", 0)
            print(f"[HOST_SESSION] Play applied. pending_draw after={after_pending}")

            self._sync_from_uno_locked()

            if self._uno.winner:
                self._session_state = SessionState.STOPPED

                winner_id = None
                for pid, player in self.players_by_id.items():
                    if player == self._uno.winner:
                        winner_id = pid

                self.send_to_players(
                    MessageType.GAME_END,
                    winner_id=winner_id
                )

                self._winner_id = winner_id
                self._safe_notify()

        return True, None

    def _apply_draw(self, player_id: str):
        with self._game_lock:
            if self._session_state != SessionState.IN_GAME:
                return False, "Game not running"

            player = self.players_by_id.get(player_id)
            if not player:
                return False, "Unknown player"

            if player is not self._uno.get_current_player():
                return False, "Not your turn"

            before_pending = getattr(self._uno, "pending_draw", 0)
            print(f"[HOST_SESSION] Draw request by {player_id} | pending_draw before={before_pending}")

            try:
                # Draw one card as a standard draw action or full penalty draw
                self._uno.player_must_draw(player)
            except ValueError as e:
                print(f"[HOST_SESSION] Draw rejected for {player_id}: {e}")
                return False, str(e)

            after_pending = getattr(self._uno, "pending_draw", 0)
            print(f"[HOST_SESSION] Draw applied | pending_draw after={after_pending}")

            self._sync_from_uno_locked()

        return True, None

    # ---------- Synchronisation ----------

    def _sync_from_uno_locked(self):
        self.current_player_id = next(
            pid for pid, p in self.players_by_id.items()
            if p is self._uno.get_current_player()
        )

        top = self._uno.get_top_card()
        self.top_card = {
            "color": top.color.value,
            "value": top.value.value,
        }

        self.game_players = [
            {
                "id": pid,
                "name": self.player_names.get(pid),
                "card_count": p.hand.get_size(),
            }
            for pid, p in self.players_by_id.items()
        ]

        self.direction = self._uno.direction
        self.can_counter_uno = self._uno.can_counter_uno

        try:
            pending = getattr(self._uno, "pending_draw", 0)
            players_counts = ", ".join([f"{pid}:{p.hand.get_size()}" for pid, p in self.players_by_id.items()])
            print(
                f"[HOST_SESSION] STATE -> current={self.current_player_id}, top={self.top_card['color']} {self.top_card['value']}, dir={self.direction}, pending_draw={pending} | cards=({players_counts})"
            )
        except Exception:
            pass

        self.send_to_players(
            MessageType.GAME_STATE_UPDATE,
            state=self.serialize_game_state(),
        )

        for pid in self.players_by_id:
            self.send_private_hand(pid)

    def serialize_game_state(self) -> dict:
        return {
            "current_player_id": self.current_player_id,
            "top_card": self.top_card,
            "players": self.game_players,
            "direction": self.direction,
            "can_counter_uno": self.can_counter_uno,
        }

    # ---------- Gestion réseau ----------

    def send_to_players(self, message_type: MessageType, **payload):
        extra = ""
        for key, value in payload.items():
            extra += f" | {key}={value}"

        print(f"[HOST_SESSION->NET] Broadcast {message_type}{extra}")

        if self.host:
            self.host.broadcast(build_message(message_type, **payload))

    def send_private_hand(self, player_id: str):
        player = self.players_by_id.get(player_id)
        if not player:
            return

        payload = {
            "cards": [
                {
                    "color": player.hand.get(i).color.value,
                    "value": player.hand.get(i).value.value,
                }
                for i in range(player.hand.get_size())
            ]
        }

        try:
            print(f"[HOST_SESSION->NET] Private hand to {player_id}: {len(payload['cards'])} cards")
        except Exception:
            pass

        if player_id == self._id:
            self.on_update_hand(payload)
        else:
            self.host.send_to(
                player_id,
                build_message(MessageType.PRIVATE_HAND_UPDATE, **payload),
            )
