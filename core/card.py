from enum import Enum

class Color(Enum):
    RED = "red"
    BLUE = "blue"
    GREEN = "green"
    YELLOW = "yellow"
    WILD = "wild"

class Value(Enum):
    ZERO = "0"
    ONE = "1"
    TWO = "2"
    THREE = "3"
    FOUR = "4"
    FIVE = "5"
    SIX = "6"
    SEVEN = "7"
    EIGHT = "8"
    NINE = "9"
    SKIP = "skip"
    REVERSE = "reverse"
    DRAW_TWO = "+2"
    WILD = "wild"
    WILD_DRAW_FOUR = "+4"
    VERSO = "verso"

class Card:
    def __init__(self, color: Color, value: Value):
        self.color = color
        self.value = value

    def is_playable_on(self, top_card):
        return (
            self.color == top_card.color
            or self.value == top_card.value
            or self.color == Color.WILD
        )

    def to_dict(self):
        return {
            "color": self.color.value,
            "value": self.value.value
        }

    @staticmethod
    def from_dict(data):
        return Card(Color(data["color"]), Value(data["value"]))
