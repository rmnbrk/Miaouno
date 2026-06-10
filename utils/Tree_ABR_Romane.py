from utils.structures import Stack, Queue
from typing import TypeVar, Generic

T = TypeVar("T")

# Arbre Binaire de Recherche (ABR) - Romane
# Basé sur le cours de Monsieur Kheddouci Hamamache

class BinaryNode(Generic[T]):
    def __init__(self, value: T):
        self.val = value
        self.fg: BinaryNode[T] | None = None # Fils Gauche
        self.fd: BinaryNode[T] | None = None # Fils Droit

class BinarySearchTree(Generic[T]):
    def __init__(self):
        self.root: BinaryNode[T] | None = None

    def insert(self, val: T) -> None:
        """Fonction planter"""
        if self.root is None:
            self.root = BinaryNode(val)
            return

        ptr_noeud = self.root
        plante = False
        while not plante:
            if val <= ptr_noeud.val:
                if ptr_noeud.fg is None:
                    ptr_noeud.fg = BinaryNode(val)
                    plante = True
                else:
                    ptr_noeud = ptr_noeud.fg
            else:
                if ptr_noeud.fd is None:
                    ptr_noeud.fd = BinaryNode(val)
                    plante = True
                else:
                    ptr_noeud = ptr_noeud.fd

    def size(self, node: BinaryNode[T] | None) -> int:
        if node is None:
            return 0
        return 1 + self.size(node.fg) + self.size(node.fd)

    def height(self, node: BinaryNode[T] | None) -> int:
        if node is None:
            return -1
        return 1 + max(self.height(node.fg), self.height(node.fd))

    def search(self, node: BinaryNode[T] | None, value: T) -> bool:
        if node is None:
            return False
        if node.val == value:
            return True
        return self.search(node.fg, value) or self.search(node.fd, value)

    def get_min(self, node: BinaryNode[T] | None) -> T:
        if node is None:
            return float('inf')  # dans le cours -> MAX_INTEGER = + l'infini
        if node.fg is None:
            return node.val
        return self.get_min(node.fg)

    def get_max(self, node: BinaryNode[T] | None) -> T:
        if node is None:
            return float('-inf')  # - l'infini
        if node.fd is None:
            return node.val
        return self.get_max(node.fd)

    def delete(self, value: T):
        """Pour utiliser plus facielemnt delete_recursive"""
        self.root = self.delete_recursive(self.root, value)

    def delete_recursive(self, node: BinaryNode[T] | None, value: T) -> BinaryNode[T] | None:
        if node is None: return None

        if value < node.val:
            node.fg = self.delete_recursive(node.fg, value)
        elif value > node.val:
            node.fd = self.delete_recursive(node.fd, value)
        else:
            if node.fg is None: return node.fd
            if node.fd is None: return node.fg

            temp_val = self.get_min(node.fd)
            node.val = temp_val
            node.fd = self.delete_recursive(node.fd, temp_val)
        return node

    # Parcours récursifs
    def prefix(self, node: BinaryNode[T] | None):
        if node:
            print(node.val, end=" ")
            self.prefix(node.fg)
            self.prefix(node.fd)

    def infix(self, node: BinaryNode[T] | None):
        if node:
            self.infix(node.fg)
            print(node.val, end=" ")
            self.infix(node.fd)

    def postfix(self, node: BinaryNode[T] | None):
        if node:
            self.postfix(node.fg)
            self.postfix(node.fd)
            print(node.val, end=" ")

    # Parcours itératifs qui utilisent la Pile et la File que nous avons codé avant
    def prefix_iterative(self):
        if self.root is None: return
        stack = Stack[BinaryNode[T]]()  # Utilise notre Stack
        stack.push(self.root)
        while len(stack) > 0:
            n = stack.pop()
            print(n.val, end=" ")
            if n.fd: stack.push(n.fd)
            if n.fg: stack.push(n.fg)

    def level_iterative(self):
        if self.root is None: return
        queue = Queue()  # Utilise notre Queue
        queue.enqueue(self.root)
        while not queue.is_empty():
            n = queue.dequeue()
            print(n.val, end=" ")
            if n.fg: queue.enqueue(n.fg)
            if n.fd: queue.enqueue(n.fd)