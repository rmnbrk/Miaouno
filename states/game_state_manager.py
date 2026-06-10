from states.game_state import GameState
from utils.structures import Stack, T


class GameStateManager:
    def __init__(self):
        self._states = Stack[GameState]()

    def get_size(self):
        return len(self._states)

    def is_empty(self):
        return self._states.is_empty()

    def current_state(self):
        return self._states.peek()

    def push(self, state: GameState):
        self._states.push(state)

    def pop(self):
        return self._states.pop()

    def clear(self):
        while not self._states.is_empty():
            self._states.pop()
