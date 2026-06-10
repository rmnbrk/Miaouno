from typing import TypeVar, Generic

T = TypeVar("T")

class Node(Generic[T]):
    """Nœud pour la liste chainée"""
    value: T
    next: "Node[T] | None"

    def __init__(self, value: T):
        self.value = value
        self.next = None

#liste chaînée (linked list)
class LinkedList(Generic[T]):
    head: Node[T] | None
    size: int

    def __init__(self):
        self.head = None
        self.size = 0

    def is_empty(self) -> bool:
        """Renvoie True si la liste est vide"""
        return self.head is None

    def get_size(self) -> int:
        """Renvoie la taille de la liste"""
        return self.size

    def insert_at(self, index: int, value: T) -> None:
        """Insère un maillon avec la valeur demandée à l'index souhaité"""
        if index < 0 or index > self.size:
            raise IndexError("Index out of bounds")

        new_node = Node(value)

        if index == 0:
            new_node.next = self.head
            self.head = new_node
        else:
            current = self.head
            for _ in range(index - 1):
                current = current.next
            new_node.next = current.next
            current.next = new_node
        self.size += 1

    def delete_at(self, index: int) -> T:
        """Supprime le maillon à l'index souhaité et renvoie sa valeur"""
        if index < 0 or index >= self.size:
            raise IndexError("Index out of bounds")

        if index == 0:
            value = self.head.value
            self.head = self.head.next
        else:
            current = self.head
            for _ in range(index - 1):
                current = current.next

            value = current.next.value
            current.next = current.next.next

        self.size -= 1
        return value

    def append(self, value: T) -> None:
        """Ajoute un élément à la fin de la liste"""
        new_node = Node(value)

        if self.head is None:
            self.head = new_node
        else:
            current = self.head
            while current.next is not None:
                current = current.next
            current.next = new_node

        self.size += 1

    def get(self, index: int) -> T:
        """Retourne l'élément à l'index demandé"""
        if index < 0 or index >= self.size:
            raise IndexError("Index out of bounds")

        current = self.head
        for _ in range(index):
            current = current.next
        return current.value

    def clear(self) -> None:
        """Vide la liste"""
        self.head = None
        self.size = 0

    def __str__(self):
        value = "["
        current = self.head
        while current:
            value += ", " + str(current.value)
            current = current.next
        value += "]"
        return value

    def __iter__(self):
        current = self.head
        while current is not None:
            yield current.value
            current = current.next

    def __len__(self):
        return self.size

#pile FILO (stack)
class Stack(Generic[T]):
    def __init__(self):
        self._items = LinkedList[T]()

    def is_empty(self) -> bool:
        return self._items.is_empty()

    def push(self, value: T) -> None:
        self._items.insert_at(0, value)

    def pop(self) -> T:
        if self.is_empty():
            raise IndexError("Can't pop, the stack is empty")
        return self._items.delete_at(0)

    def peek(self) -> T:
        if self.is_empty():
            raise IndexError("Can't peek, the stack is empty")
        return self._items.get(0)

    def clear(self) -> None:
        self._items.clear()

    def __len__(self):
        return self._items.get_size()

    def __str__(self):
        return str(self._items)


#file FIFO (queue)
class Queue(Generic[T]):
    def __init__(self):
        self.stack1 = Stack[T]()
        self.stack2 = Stack[T]()

    def is_empty(self) -> bool:
        return self.stack1.is_empty() and self.stack2.is_empty()

    def get_size(self) -> int:
        return len(self.stack1) + len(self.stack2)

    def transfere(self) -> None:
        """transfere la pile 1 dans la pile 2 si la 2 est vide"""
        if len(self.stack2) == 0:
            size = len(self.stack1)
            for i in range(size):
                self.stack2.push(self.stack1.pop())

    def enqueue(self, value: T) -> None:
        """enfile"""
        self.stack1.push(value)

    def dequeue(self) -> T | None:
        """défile"""
        if self.is_empty():
            raise IndexError("File vide")
        #return self.items.pop(0)

        self.transfere()

        return self.stack2.pop()

    def front(self) -> T:
        """retourne l'élément du début"""
        if self.is_empty():
            raise IndexError("File vide")
        self.transfere()
        return self.stack2.peek()

    def rear(self) -> T:
        """Retourne l'élément de la fin"""
        if self.is_empty():
            raise IndexError("File vide")

        if self.stack1.is_empty():
            # stack1 vide donc bottom de stack2
            return self.stack2._items.get(self.stack2._items.get_size() - 1)
        else:
            # top de stack1
            return self.stack1.peek()

    def clear(self) -> None:
        self.stack1.clear()
        self.stack2.clear()
