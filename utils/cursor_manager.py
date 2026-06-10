from enum import Enum

class CursorState(Enum):
    NORMAL = "cursor_paw_normal"
    HOVERED = "cursor_paw_pointer"
    FORBIDEN = "forbiden_cursor_paw_pointer"

class CursorManager:
    state: CursorState = CursorState.NORMAL

    @staticmethod
    def set(state: CursorState):
        CursorManager.state = state

    @staticmethod
    def reset():
        CursorManager.state = CursorState.NORMAL