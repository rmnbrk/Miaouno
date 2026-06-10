import socket
import threading
import uuid
from typing import TYPE_CHECKING

from network.constants import DISCOVERY_PORT, GAME_PORT
from network.messages import MessageType, parse_message, build_message
from utils.observer import Subject

if TYPE_CHECKING:
    from session.client_session import ClientSession


class Client(Subject):
    def __init__(self, session: "ClientSession", name: str):
        super().__init__()
        self.session = session
        self.id = str(uuid.uuid4())
        self.name = name

        self.socket: socket.socket | None = None

        self.running_event = threading.Event()
        self.discovering_event = threading.Event()

    def discover(self):
        if self.discovering_event.is_set():
            return
        self.running_event.set()
        threading.Thread(target=self.discover_hosts, daemon=True).start()

    def discover_hosts(self, interval: float = 1.0):
        self.discovering_event.set()

        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind(("", DISCOVERY_PORT))
            s.settimeout(interval)

            print("[CLIENT] Searching hosts on LAN")

            while self.running_event.is_set() and self.discovering_event.is_set():
                try:
                    data, address = s.recvfrom(1024)
                except socket.timeout:
                    continue

                parsed = parse_message(data.decode())
                if parsed and parsed["type"] == MessageType.HOST_ANNOUNCE:
                    self.session.add_available_game(
                        parsed["host_id"],
                        address[0],
                        parsed["host_name"],
                        parsed["max_player_count"]
                    )

    def connect_host(self, host_id: str) -> tuple[bool, str]:
        if host_id not in self.session.get_available_games():
            return False, "Host not found"

        host = self.session.get_available_games()[host_id]
        print(f"[CLIENT] Connecting to {host.name} ({host.ip}:{GAME_PORT})")

        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1.0)
            s.connect((host.ip, GAME_PORT))

            buffer = ""
            while "\n" not in buffer:
                chunk = s.recv(4096).decode()
                if not chunk:
                    s.close()
                    return False, "Host closed connection"
                buffer += chunk

            raw, _ = buffer.split("\n", 1)
            data = parse_message(raw)

        except OSError:
            return False, "Connection failed"

        if not data:
            s.close()
            return False, "Invalid response from host"

        if data["type"] == MessageType.JOIN_REJECT:
            s.close()
            return False, data["reason"]

        if data["type"] != MessageType.JOIN_ACCEPT:
            s.close()
            return False, "Unexpected message from host"

        self.socket = s
        self.discovering_event.clear()

        join_msg = build_message(
            MessageType.JOIN,
            player_id=self.id,
            player_name=self.name
        ) + "\n"

        s.settimeout(1.0)

        for _ in range(10):
            try:
                s.sendall(join_msg.encode())
                buffer = ""
                while "\n" not in buffer:
                    buffer += s.recv(4096).decode()

                msg = parse_message(buffer.split("\n", 1)[0])
                if msg and msg["type"] == MessageType.JOIN_CONFIRM:
                    s.settimeout(None)
                    print("[CLIENT] Joined game")
                    return True, "Joined game"

            except socket.timeout:
                continue
            except OSError:
                break

        s.close()
        return False, "Join failed"

    def run(self):
        if not self.socket:
            return
        self.running_event.set()
        threading.Thread(target=self.network_loop, daemon=True).start()

    def network_loop(self):
        buffer = ""

        while self.running_event.is_set():
            try:
                chunk = self.socket.recv(4096).decode()
                if not chunk:
                    break

                buffer += chunk

                while "\n" in buffer:
                    raw, buffer = buffer.split("\n", 1)
                    message = parse_message(raw)
                    if message:
                        self.handle_message(message)

            except OSError:
                break

        self.disconnect()

    def handle_message(self, data: dict):
        match data["type"]:
            case MessageType.PRE_GAME_STATE:
                self.session.clear_players()
                for player in data["players"]:
                    self.session.add_player(
                        player["player_id"],
                        player["player_name"]
                    )

            case MessageType.GAME_START:
                self.session.on_game_start()

            case MessageType.GAME_END:
                self.session.on_game_end(data)

            case MessageType.GAME_STATE_UPDATE:
                self.session.on_update_game_state(data)

            case MessageType.PRIVATE_HAND_UPDATE:
                self.session.on_update_hand(data)

            case MessageType.GAME_ERROR:
                reason = data.get("reason", "Action invalide")
                self.session.on_game_error(reason)
                print(f"[CLIENT] : GAME_ERROR -> {reason}")

            case _:
                print(
                    f"[CLIENT] : Unknown message type : {data['type']}"
                )

    def send(self, message: str):
        if not self.socket or not self.running_event.is_set():
            return
        try:
            self.socket.sendall((message + "\n").encode())
        except OSError:
            self.disconnect()

    def disconnect(self):
        self.running_event.clear()
        self.discovering_event.clear()

        if self.socket:
            try:
                self.socket.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            self.socket.close()
            self.socket = None

        print("[CLIENT] Disconnected")
