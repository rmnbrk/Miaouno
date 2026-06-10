from core.card import Color, Card, Value
from core.player import Player
from utils.structures import Queue, Stack, LinkedList
import random

class Uno:
    def __init__(self, players: tuple[Player, ...]):
        if len(players) < 2:
            raise ValueError("Il faut au moins 2 joueurs pour jouer")
        if len(players) > 10:
            raise ValueError("Maximum 10 joueurs")

        self.players = list(players)
        self.deck = Queue()  # Pioche
        self.discard_pile = Stack()  # Défausse
        self.current_player_index = 0
        self.direction = 1  # 1 = sens horaire, -1 = sens anti-horaire
        self.game_over = False
        self.winner = None
        self.can_counter_uno = False
        # Pénalité en attente liée à des +2/+4 empilés
        self.pending_draw = 0

        self.create_deck()
        self.deal_initial_cards()

    def create_uno_deck(self):
        deck = Queue()  # Création structure → O(1)
        colors = [Color.RED, Color.BLUE, Color.GREEN, Color.YELLOW]  # Liste de 4 éléments → O(1)

        for color in colors:  # Boucle exécutée 4 fois (constante) → O(1)
            deck.enqueue(Card(color, Value.ZERO))  # enqueue() → O(1)

            for _ in range(2):  # Boucle exécutée 2 fois → O(1)
                for value in [
                    Value.ONE, Value.TWO, Value.THREE, Value.FOUR,
                    Value.FIVE, Value.SIX, Value.SEVEN, Value.EIGHT, Value.NINE,
                    Value.SKIP, Value.REVERSE, Value.DRAW_TWO
                ]:  # Boucle sur 12 valeurs → O(1)
                    deck.enqueue(Card(color, value))  # enqueue() → O(1)
        # Total pour les couleurs : 4 * (1 + 2 * 12) = 100 itérations O(1) → O(1)

        for _ in range(4):  # Boucle exécutée 4 fois → O(1)
            deck.enqueue(Card(Color.WILD, Value.WILD))  # enqueue() → O(1)
            deck.enqueue(Card(Color.WILD, Value.WILD_DRAW_FOUR))  # enqueue() → O(1)
        # Total : 8 itérations O(1) → O(1)

        return deck  # O(1)

    def create_deck(self):
        self.deck = self.create_uno_deck()  # Appel fonction → O(1) (taille fixe de 108 cartes)

        cards = []  # Création liste → O(1)
        while not self.deck.is_empty():  # Boucle n fois (n = nb cartes total) → O(n)
            cards.append(self.deck.dequeue())  # append() + dequeue() → O(1)

        random.shuffle(cards)  # Mélange de n éléments → O(n)

        for card in cards:  # Boucle n fois → O(n)
            self.deck.enqueue(card)  # enqueue() → O(1)

    def deal_initial_cards(self):
        for _ in range(7):
            for player in self.players:
                if not self.deck.is_empty():
                    card = self.deck.dequeue()
                    player.hand.append(card)

    def start_game(self):
        if self.deck.is_empty():
            return

        self.current_player_index = 1 % len(self.players)

        first_card = self.deck.dequeue()

        while first_card.color == Color.WILD:
            self.deck.enqueue(first_card)
            first_card = self.deck.dequeue()

        self.discard_pile.push(first_card)

        if first_card.value == Value.SKIP:
            self.next_player()

        elif first_card.value == Value.REVERSE:
            if len(self.players) > 2:
                self.direction *= -1
            self.next_player()

        elif first_card.value == Value.DRAW_TWO:
            # Le premier joueur (current) a une pénalité en attente et pourra empiler ou piocher
            self.pending_draw += 2

    def get_top_card(self):
        if self.discard_pile.is_empty():
            return None
        return self.discard_pile.peek()

    def draw_card(self, player: Player, count=1):
        """count: nb de cartes à piocher (par défaut : 1)"""
        for _ in range(count):
            if self.deck.is_empty():
                self.reshuffle_discard_pile()

            if not self.deck.is_empty():
                card = self.deck.dequeue()
                player.hand.append(card)

        if player.hand.get_size() > 1:
            player.said_uno = False

    def reshuffle_discard_pile(self):
        if self.discard_pile.is_empty(): # Test → O(1)
            return

        # garder la carte du dessus
        top_card = self.discard_pile.pop() # pop() de Stack → O(1)

        cards = [] # Création d'une liste → O(1)
        while not self.discard_pile.is_empty(): # Condition vérifiée à chaque itération → O(1)
            cards.append(self.discard_pile.pop()) # append() sur liste → O(1) + pop() de Stack → O(1)
        # Chaque itération => O(1) + O(1) = O(1)

        random.shuffle(cards) # Mélange sur n éléments → O(n)

        for card in cards: # Boucle n fois
            self.deck.enqueue(card) # enqueue() de Queue → O(1)
        # Total de la boucle => O(n)

        # on la remet
        self.discard_pile.push(top_card) # push() de Stack → O(1)

    def say_uno(self, player: Player):
        if player != self.get_current_player():
            raise ValueError("Ce n'est pas le tour de ce joueur")

        if player.hand.get_size() != 1:
            raise ValueError("Vous devez avoir exactement 1 carte pour crier UNO")

        player.said_uno = True
        self.can_counter_uno = False

    def contre_uno(self, challenger: Player):
        if not self.can_counter_uno:
            raise ValueError("Impossible de contrer maintenant")

        # trouver le joueur précédent
        previous_player_index = (self.current_player_index - self.direction) % len(self.players)
        previous_player = self.players[previous_player_index]

        if previous_player.hand.get_size() == 1 and not previous_player.said_uno:
            self.draw_card(previous_player, 2)
            self.can_counter_uno = False
            return True
        else:
            return False

    def play_card(self, player: Player, card_index: int, chosen_color: Color = None, say_uno: bool = False):
        if self.game_over:
            raise ValueError("La partie est terminée")  # Test booléen → O(1)

        if player != self.get_current_player():
            raise ValueError("Ce n'est pas le tour de ce joueur")  # Accès tableau + comparaison → O(1)

        if card_index < 0 or card_index >= player.hand.get_size():
            raise IndexError("Index de carte invalide")  # get_size() sur LinkedList → O(1)

        # Récupérer la carte envisagée
        card = player.hand.get(card_index)  # Parcours LinkedList jusqu'à l'index → O(n)
        top_card = self.get_top_card()  # peek sur Stack → O(1)

        # Si une pénalité de pioche est en attente, seul un +2 ou +4 peut être joué pour empiler
        if self.pending_draw > 0:
            if card.value not in (Value.DRAW_TWO, Value.WILD_DRAW_FOUR):
                raise ValueError("Vous devez soit empiler (+2/+4), soit piocher la pénalité en attente")  # Comparaison → O(1)
            # En mode empilement, on autorise +2/+4 quelle que soit la couleur/valeur du dessus
        else:
            # Valider la jouabilité standard (couleur/valeur/joker)
            if not card.is_playable_on(top_card):
                raise ValueError(
                    "Cette carte ne peut pas être jouée sur "
                    + f"{top_card.color.value} {top_card.value.value}"
                )  # Test méthode sur carte → O(1)

        # Retirer la carte de la main du joueur
        played_card = player.hand.delete_at(card_index)  # Suppression dans LinkedList → O(n)

        # Gestion des jokers (choix de couleur obligatoire, et ne peut pas rester WILD)
        if played_card.color == Color.WILD:
            if chosen_color is None or chosen_color == Color.WILD:
                # Réinsérer la carte pour ne pas perdre l'état si erreur
                player.hand.insert_at(min(card_index, player.hand.get_size()), played_card)  # Insertion dans LinkedList → O(n)
                raise ValueError(
                    "Vous devez choisir une couleur pour le joker (RED, BLUE, GREEN ou YELLOW)"
                )
            played_card = Card(chosen_color, played_card.value)  # Création objet → O(1)

        # Poser la carte sur la défausse
        self.discard_pile.push(played_card)  # push sur Stack → O(1)

        # Gestion de l'annonce UNO en fonction de la nouvelle taille de main
        if player.hand.get_size() == 1:  # get_size() → O(1)
            if say_uno:
                player.said_uno = True  # Affectation → O(1)
                self.can_counter_uno = False  # Affectation → O(1)
            else:
                player.said_uno = False  # Affectation → O(1)
                self.can_counter_uno = True  # Affectation → O(1)

        # Victoire si plus de cartes
        if player.hand.get_size() == 0:  # get_size() → O(1)
            self.game_over = True  # Affectation → O(1)
            self.winner = player  # Affectation → O(1)
            return  # O(1)

        # Effets de la carte puis passage au joueur suivant
        self.apply_card_effect(played_card)  # Appel méthode → O(1)
        self.next_player()  # Calcul modulo + affectation → O(1)

    def apply_card_effect(self, card: Card):
        if card.value == Value.SKIP:
            self.next_player()

        elif card.value == Value.REVERSE:
            self.direction *= -1 #inverse

        elif card.value == Value.DRAW_TWO:
            # Empile la pénalité, la pioche effective se fera quand un joueur décide de piocher
            self.pending_draw += 2

        elif card.value == Value.WILD_DRAW_FOUR:
            # Empile la pénalité, la pioche effective se fera quand un joueur décide de piocher
            self.pending_draw += 4

    def get_current_player(self):
        return self.players[self.current_player_index]

    def next_player(self):
        self.current_player_index = (self.current_player_index + self.direction) % len(self.players)
        # Dès qu'on change de joueur, on ne peut plus contrer l'UNO
        self.can_counter_uno = False

    def can_play_any_card(self, player: Player):
        top_card = self.get_top_card()
        for i in range(player.hand.get_size()):
            if player.hand.get(i).is_playable_on(top_card):
                return True
        return False

    def get_playable_cards(self, player: Player):
        top_card = self.get_top_card()
        playable = []
        for i in range(player.hand.get_size()):
            if player.hand.get(i).is_playable_on(top_card):
                playable.append(i)
        return playable

    def player_must_draw(self, player: Player):
        """Fait piocher les cartes nécessaires.
        - S'il y a une pénalité en attente (pending_draw > 0), le joueur pioche tout et conserve le tour (il pourra jouer ensuite).
        - Sinon, pioche standard d'une carte et fin de tour.
        """
        if player != self.get_current_player():
            raise ValueError("Ce n'est pas le tour de ce joueur")

        if self.pending_draw > 0:
            self.draw_card(player, self.pending_draw)
            self.pending_draw = 0
            # Tour conservé (draw then may play)
            return

        # Pioche standard
        self.draw_card(player, 1)
        # Après avoir pioché sa carte standard, le joueur termine son tour
        self.next_player()