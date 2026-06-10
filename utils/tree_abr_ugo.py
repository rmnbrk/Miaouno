from typing import TypeVar, Generic

from utils.structures import Queue

T = TypeVar("T")

class Arbre(Generic[T]):
    def __init__(self, valeur: T):
        self.valeur = valeur
        self.fils_gauche: Arbre[T] | None = None
        self.fils_droit: Arbre[T] | None = None


def inserer(arbre: Arbre[T] | None, valeur: T) -> Arbre[T]:
    """Insère une valeur dans l'arbre"""
    if arbre is None:
        return Arbre(valeur)

    if valeur < arbre.valeur:
        arbre.fils_gauche = inserer(arbre.fils_gauche, valeur)
    elif valeur > arbre.valeur:
        arbre.fils_droit = inserer(arbre.fils_droit, valeur)

    return arbre

def supprimer(arbre: Arbre[T] | None, valeur: T) -> Arbre[T] | None:
    if arbre is None:
        return None

    if valeur < arbre.valeur:
        arbre.fils_gauche = supprimer(arbre.fils_gauche, valeur)
    elif valeur > arbre.valeur:
        arbre.fils_droit = supprimer(arbre.fils_droit, valeur)

    else:
        if arbre.fils_gauche is None:
            return arbre.fils_droit
        elif arbre.fils_droit is None:
            return arbre.fils_gauche

        successeur_val = minimum(arbre.fils_droit)
        arbre.valeur = successeur_val
        arbre.fils_droit = supprimer(arbre.fils_droit, successeur_val)

    return arbre

def recherche(arbre: Arbre[T] | None, valeur: T) -> bool:
    """Recherche une valeur dans l'arbre et renvoie True si elle s'y trouve, False sinon"""
    if arbre is None:
        return False

    if arbre.valeur == valeur:
        return True

    if valeur < arbre.valeur:
        return recherche(arbre.fils_gauche, valeur)
    else:
        return recherche(arbre.fils_droit, valeur)

def parcours_prefixe(arbre: Arbre[T]):
    """Parcours préfixe"""
    if arbre is None:
        return
    print(arbre.valeur)
    parcours_prefixe(arbre.fils_gauche)
    parcours_prefixe(arbre.fils_droit)

def parcours_infixe(arbre: Arbre[T]):
    """Parcours infixe. Renvoie les valeurs de l'arbre triées"""
    if arbre is None:
        return

    parcours_infixe(arbre.fils_gauche)
    print(arbre.valeur)
    parcours_infixe(arbre.fils_droit)

def parcours_suffixe(arbre: Arbre[T]):
    """Parcours suffixe"""
    if arbre is None:
        return
    parcours_suffixe(arbre.fils_gauche)
    parcours_suffixe(arbre.fils_droit)
    print(arbre.valeur)


def parcours_largeur(arbre: Arbre[T] | None):
    """
    Parcours en largeur qui visite l'arbre niveau par niveau. Utilise une file.
    """
    if arbre is None:
        return

    file = Queue[Arbre[T]]()
    file.enqueue(arbre)

    while not file.is_empty():
        courant = file.dequeue()

        print(courant.valeur)

        if courant.fils_gauche is not None:
            file.enqueue(courant.fils_gauche)

        if courant.fils_droit is not None:
            file.enqueue(courant.fils_droit)

def maximum(arbre: Arbre[T]) -> T | None:
    """Retourne la valeur maximum qui se trouve dans l'arbre.
    On exploite le fait que ce soit un ABR pour trouver plus facilement,
    au lieu de parcourir l'intégralité de l'arbre."""
    if arbre is None:
        return None

    courant = arbre
    while courant.fils_droit is not None:
        courant = courant.fils_droit
    return courant.valeur


def minimum(arbre: Arbre[T] | None) -> T | None:
    """Retourne la valeur minimum qui se trouve dans l'arbre.
        On exploite le fait que ce soit un ABR pour trouver plus facilement,
        au lieu de parcourir l'intégralité de l'arbre."""
    if arbre is None:
        return None

    if arbre.fils_gauche is None:
        return arbre.valeur

    return minimum(arbre.fils_gauche)

def hauteur(arbre: Arbre[T] | None) -> int:
    """Renvoie la hauteur de l'arbre"""
    if arbre is None:
        return 0
    return 1 + max(hauteur(arbre.fils_gauche), hauteur(arbre.fils_droit))

def taille(arbre: Arbre[T] | None) -> int:
    """Renvoie la taille de l'arbre (Nombre de noeuds)"""
    if arbre is None:
        return 0
    return 1 + taille(arbre.fils_gauche) + taille(arbre.fils_droit)
