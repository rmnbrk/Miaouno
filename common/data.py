from dataclasses import dataclass


@dataclass
class PlayerData:
    id: str
    name: str

    def to_dict(self):
        return {
            "player_id": self.id,
            "player_name": self.name
        }


@dataclass
class HostData:
    ip: str
    name: str
    max_player_count: int

    def to_dict(self):
        return {
            "host_ip": self.ip,
            "host_name": self.name
        }