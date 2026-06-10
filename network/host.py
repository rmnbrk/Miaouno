import socket
import threading
import uuid
from typing import TYPE_CHECKING

from network.constants import GAME_PORT, DISCOVERY_PORT
from common.constants import MAX_PLAYER_COUNT
from network.messages import build_message, MessageType, parse_message

if TYPE_CHECKING:
    from session.host_session import HostSession


class Host:
    def __init__(
        self,
        session: "HostSession",
        name: str,
        max_player_count: int = MAX_PLAYER_COUNT,
        ip: str = "0.0.0.0",
        port: int = GAME_PORT,
    ):
        self.session = session
        self.id = str(uuid.uuid4())
        self.name = name
        self.ip = ip
        self.port = port

        self.max_player_count = max_player_count

        self.clients: dict[str, socket.socket] = {}
        self.clients_lock = threading.Lock()

        self.running_event = threading.Event()

    @property
    def player_count(self):
        return len(self.clients) + 1

    def run(self):
        print("[HOST] Starting")
        self.running_event.set()
        threading.Thread(target=self.connection_listen_loop, daemon=True).start()
        threading.Thread(target=self.discover_send_loop, daemon=True).start()

    def close(self):
        print("[HOST] Stopping")
        self.running_event.clear()

        with self.clients_lock:
            sockets = list(self.clients.values())

        for sock in sockets:
            try:
                sock.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            sock.close()

    def connection_listen_loop(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((self.ip, self.port))
            s.listen()
            s.settimeout(0.5)

            print(f"[HOST] Listening on port {self.port}")

            while self.running_event.is_set():
                try:
                    client_socket, addr = s.accept()
                except socket.timeout:
                    continue

                if self.player_count >= self.max_player_count:
                    msg = build_message(
                        MessageType.JOIN_REJECT, reason="Server full"
                    ) + "\n"
                    client_socket.sendall(msg.encode())
                    client_socket.close()
                    continue

                msg = build_message(MessageType.JOIN_ACCEPT) + "\n"
                client_socket.sendall(msg.encode())

                threading.Thread(
                    target=self.connected_client_loop,
                    args=(client_socket, addr),
                    daemon=True,
                ).start()

    def connected_client_loop(self, client_socket: socket.socket, client_address):
        print("[HOST] Client connected ->", client_address)

        buffer = ""
        player_id = None

        client_socket.settimeout(0.5)

        try:
            while self.running_event.is_set():
                try:
                    data = client_socket.recv(4096).decode()
                    if not data:
                        break

                    buffer += data

                    while "\n" in buffer:
                        raw, buffer = buffer.split("\n", 1)
                        msg = parse_message(raw)
                        if not msg:
                            continue

                        # --- JOIN obligatoire en premier ---
                        if msg["type"] == MessageType.JOIN:
                            if player_id is not None:
                                continue

                            player_id = msg["player_id"]
                            self.session.add_player(
                                player_id, msg["player_name"]
                            )

                            with self.clients_lock:
                                self.clients[player_id] = client_socket

                            confirm = (
                                build_message(MessageType.JOIN_CONFIRM) + "\n"
                            )
                            client_socket.sendall(confirm.encode())

                            self.broadcast_state()
                            continue

                        # --- autres messages ---
                        self.handle_message(player_id, msg)

                except socket.timeout:
                    continue

        finally:
            client_socket.close()
            if player_id:
                with self.clients_lock:
                    self.clients.pop(player_id, None)
                self.session.remove_player(player_id)
                self.broadcast_state()

            print("[HOST] Client disconnected ->", client_address)

    def discover_send_loop(self):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            while self.running_event.is_set():
                if self.player_count < self.max_player_count:
                    msg = build_message(
                        MessageType.HOST_ANNOUNCE,
                        host_id=self.id,
                        host_name=self.name,
                        max_player_count=self.max_player_count,
                    )
                    s.sendto(msg.encode(), ("255.255.255.255", DISCOVERY_PORT))

                s.settimeout(0.5)
                try:
                    s.recvfrom(1)
                except socket.timeout:
                    pass

    def send_to(self, player_id: str, message: str):
        with self.clients_lock:
            sock = self.clients.get(player_id)

        if not sock:
            return

        try:
            sock.sendall((message + "\n").encode())
        except OSError:
            self.remove_player(player_id)

    def broadcast(self, message: str):
        with self.clients_lock:
            items = list(self.clients.items())

        dead = []
        for pid, sock in items:
            try:
                sock.sendall((message + "\n").encode())
            except OSError:
                dead.append(pid)

        for pid in dead:
            self.remove_player(pid)

    def broadcast_state(self):
        state = build_message(
            MessageType.PRE_GAME_STATE,
            players=[p.to_dict() for p in self.session.get_lobby_players()],
        )
        self.broadcast(state)

    def remove_player(self, player_id: str):
        with self.clients_lock:
            sock = self.clients.pop(player_id, None)

        if sock:
            try:
                sock.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            sock.close()

        self.session.remove_player(player_id)

    def handle_message(self, player_id: str, message):
        if not player_id:
            return

        match message["type"]:
            case MessageType.GAME_ACTION_PLAY_CARD:
                self.session.on_game_action_play(player_id, message)
            case MessageType.GAME_ACTION_DRAW:
                self.session.on_game_action_draw(player_id)
