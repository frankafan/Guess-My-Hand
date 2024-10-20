import random
from copy import copy


class Card:
    def __init__(self, suit, value):
        self.suit = suit
        self.value = value
        self.map = {"Hearts": "♥", "Diamonds": "♦", "Clubs": "♣", "Spades": "♠"}
        self.rmap = {"♥": "Hearts", "♦": "Diamonds", "♣": "Clubs", "♠": "Spades"}

    def __str__(self):
        return f"{self.value} of {self.suit}"
    

    def __hash__(self):
        return hash((self.suit, self.value))

    def __eq__(self, other):
        return (self.suit, self.value) == (other.suit, other.value)

    def __repr__(self):
        return str(self)

    # Override __eq__ for equality comparison
    # allows us to use
    #   `card in cards`
    # instead of
    #   `str(card) in [str(c) for c in cards]`
    def __eq__(self, other):
        if isinstance(other, Card):
            return self.suit == other.suit and self.value == other.value
        return False

    # Override __hash__ for hashability 
    # required for user defined __eq__
    def __hash__(self):
        return hash((self.suit, self.value)) 

    def __repr__(self):
        return f"{self.value} of {self.suit}"

    def __eq__(self, other):
        if isinstance(other, Card):
            return self.suit == other.suit and self.value == other.value
        return False

    def __hash__(self):
        return hash((self.suit, self.value))


class Deck:
    def __init__(self, seed=42):
        self.suits = ["Hearts", "Diamonds", "Clubs", "Spades"] 
        self.values = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
        self.cards = [Card(suit, value) for suit in self.suits for value in self.values]
        self.copyCards = copy(self.cards)
        random.seed(seed)
        self.newseed = random.randint(0, 10000)
        random.seed(seed)
        random.shuffle(self.cards)

    def draw(self):
        if len(self.cards) > 0:
            return self.cards.pop()
        return None

class Player:
    def __init__(self, name, strategy):
        self.name: str = name
        self.hand: list[Card] = []
        self.played_cards: list[Card] = []
        self.strategy = strategy
        self.guesses = []
        self.exposed_cards = {"North": [], "East": [], "South": [], "West": []}
        self.cVals = []
        self.seed_scores = []
    

    def add_seed_score(self, score):
        self.seed_scores.append(score)


    def draw(self, deck):
        card = deck.draw()
        if card:
            self.hand.append(card)

    def play_card(self, index):
        if 0 <= index < len(self.hand):
            card = self.hand.pop(index)
            self.played_cards.append(card)
            return card
        return None

    def update_exposed_cards(self, player_name, card):
        self.exposed_cards[player_name].append(card)

    def __str__(self) -> str:
        return f"Player({self.name})"
    
    def __repr__(self) -> str:
        return str(self)
