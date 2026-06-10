from utils.structures import LinkedList


class Player:
    def __init__(self):
        self.hand: LinkedList = LinkedList()
        self.said_uno = False
