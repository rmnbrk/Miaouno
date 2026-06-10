import json
from enum import Enum


class MessageType(str, Enum):
    # Discovery / lobby
    HOST_ANNOUNCE = "HOST_ANNOUNCE"
    JOIN = "JOIN"
    JOIN_ACCEPT = "JOIN_ACCEPT"
    JOIN_REJECT = "JOIN_REJECT"
    JOIN_CONFIRM = "JOIN_CONFIRM"
    PRE_GAME_STATE = "PRE_GAME_STATE"

    # Cycle de vie
    GAME_START = "GAME_START"
    GAME_END = "GAME_END"
    GAME_ERROR = "GAME_ERROR"

    # Actions (client vers host)
    GAME_ACTION_PLAY_CARD = "GAME_ACTION_PLAY_CARD"
    GAME_ACTION_DRAW = "GAME_ACTION_DRAW"
    GAME_ACTION_SAY_UNO = "GAME_ACTION_SAY_UNO"
    GAME_ACTION_CONTRE_UNO = "GAME_ACTION_CONTRE_UNO"

    # État du jeu (host vers clients)
    GAME_STATE_UPDATE = "GAME_STATE_UPDATE"
    PRIVATE_HAND_UPDATE = "PRIVATE_HAND_UPDATE"


# Schémas des messages
MESSAGE_SCHEMAS = {
    MessageType.HOST_ANNOUNCE: {
        "host_id": str,
        "host_name": str,
        "max_player_count": int
    },

    MessageType.JOIN: {
        "player_id": str,
        "player_name": str
    },

    MessageType.JOIN_ACCEPT: {},
    MessageType.JOIN_REJECT: {},
    MessageType.JOIN_CONFIRM: {},

    MessageType.PRE_GAME_STATE: {
        "players": list
    },

    MessageType.GAME_ACTION_PLAY_CARD: {
        "card_index": int,
        "chosen_color": (str, type(None)),
        "say_uno": bool
    },

    MessageType.GAME_START: {},

    MessageType.GAME_ACTION_DRAW: {},

    MessageType.GAME_STATE_UPDATE: {
        "state": dict
    },

    MessageType.PRIVATE_HAND_UPDATE: {
        "cards": list
    },

    MessageType.GAME_END: {
        "winner_id": str
    },

    MessageType.GAME_ERROR: {
        "reason": str
    }
}


def validate_message(payload: dict, schema: dict) -> bool:
    """Vérifie que les champs attendus sont présents et du bon type"""
    for key, expected_type in schema.items():
        if key not in payload:
            return False
        if not isinstance(payload[key], expected_type):
            return False
    return True


def build_message(msg_type: MessageType, **payload) -> str:
    schema = MESSAGE_SCHEMAS.get(msg_type)
    if schema is None:
        raise ValueError(f"Unknown message type: {msg_type}")

    if not validate_message(payload, schema):
        raise ValueError(
            f"Invalid payload for {msg_type}: {payload}, expected {schema}"
        )

    return json.dumps({
        "type": msg_type.value,
        **payload
    })

def parse_message(raw: str) -> dict | None:
    """Parse un message JSON reçu (sans le \\n)"""
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return None

    if not isinstance(data, dict):
        return None

    try:
        msg_type = MessageType(data.get("type"))
    except (ValueError, TypeError):
        return None

    schema = MESSAGE_SCHEMAS.get(msg_type)
    if schema is None:
        return None

    # On enlève "type" pour valider le payload
    payload = {k: v for k, v in data.items() if k != "type"}

    if not validate_message(payload, schema):
        return None

    data["type"] = msg_type
    return data
