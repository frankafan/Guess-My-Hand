import random
import numpy as np
from CardGame import Card, Deck, Player
import csv

ALL_SUITS = ["Hearts", "Diamonds", "Clubs", "Spades"]
ALL_VALUES = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
CARD_VALUE = {
    "A": 1,
    "J": 11,
    "Q": 12,
    "K": 13,
}

TEAMMATE_NAME = {
    "North": "South",
    "East": "West",
    "South": "North",
    "West": "East",
}

# determines for how many rounds a player should
# give the card with the best seed until they start
# playing unlikely cards
SEED_ROUNDS = 2
SAVE_SEED_SCORE_DATA = False
USE_UNLIKELY_CARD_STRATEGY = False


LAMBDA1 = 0.5
LAMBDA2 = 0


def get_seed(card: Card):
    return int(CARD_VALUE.get(card.value, card.value)) + 13 * (
        list(card.map.keys()).index(card.suit)
    )


def get_possible_cards():
    possible_cards = []
    for card in [Card(suit, value) for suit in ALL_SUITS for value in ALL_VALUES]:
        if card not in possible_cards:
            possible_cards.append(card)

    return possible_cards


def get_shuffle(card: Card) -> list[Card]:
    """Returns an **unprocessed** shuffled deck based off a card's seed"""
    possible_cards = get_possible_cards()
    seed = get_seed(card)
    np.random.seed(seed)

    shuffled_cards = possible_cards.copy()
    np.random.shuffle(shuffled_cards)

    # TODO: process a shuffle here based off which cards have been played at this point
    # useful for when the player wants to see the actual quality's
    # of a shuffle when choosing the unlikeliest card

    return shuffled_cards


def card_with_best_seed(player: Player) -> Card:
    played_cards = sum(list(player.exposed_cards.values()), [])
    highest_score = 0
    card_to_play = None

    for card in player.hand:
        shuffled_cards = get_shuffle(card)

        for c in shuffled_cards:
            if c in played_cards:
                shuffled_cards.remove(c)

        combination = shuffled_cards[: 12 - len(player.played_cards)]

        score = 0
        for c in combination:
            # we don't get points for having a card in the permutation that
            # we would play ~ 1pt / game optimization
            if c in player.hand and c != card:
                score += 1
        if score > highest_score:
            highest_score = score
            card_to_play = card

    # only add the seed score if the Player.add_seed_score() exists
    # if SAVE_SEED_SCORE_DATA and len(player.played_cards) < 12:
    # player.add_seed_score(
    #     [
    #         player.name,
    #         len(player.played_cards) + 1,
    #         highest_score / (12 - len(player.played_cards)),
    #     ]
    # )

    # TODO: plays random card - we can optimize this
    return card_to_play or player.hand[0]


def card_with_best_seed_improved(player: Player) -> Card:
    played_cards = sum(list(player.exposed_cards.values()), [])
    highest_score = 0
    card_to_play = None

    for card in player.hand:
        shuffled_cards = get_shuffle(card)

        for c in shuffled_cards:
            if c in played_cards:
                shuffled_cards.remove(c)

        combination = shuffled_cards[: 12 - len(player.played_cards)]

        score = 0
        for c in combination:
            # we don't get points for having a card in the permutation that
            # we would play ~ 1pt / game optimization
            if c in player.hand and c != card:
                score += 1
                if c in get_card_indication_freq(player):
                    score -= get_card_indication_freq(player)[c] * LAMBDA1
                score -= LAMBDA2 * len(player.exposed_cards[player.name])

        if score > highest_score:
            highest_score = score
            card_to_play = card

    if SAVE_SEED_SCORE_DATA and len(player.played_cards) < 12:
        player.add_seed_score(
            [
                player.name,
                len(player.played_cards) + 1,
                highest_score / (12 - len(player.played_cards)),
            ]
        )

    # TODO: plays random card - we can optimize this
    return card_to_play or player.hand[0]


def get_teammate_shuffle(player, teammate_last_card):
    played_cards = sum(list(player.exposed_cards.values()), [])
    possible_cards = get_possible_cards()

    seed = get_seed(teammate_last_card)
    np.random.seed(seed)
    shuffled_cards = possible_cards.copy()
    np.random.shuffle(shuffled_cards)

    for c in shuffled_cards:
        if c in played_cards + player.hand:
            shuffled_cards.remove(c)

    return shuffled_cards


def get_teammate_last_card(player):
    teammate_last_card = None
    if len(player.exposed_cards[TEAMMATE_NAME[player.name]]) > 0:
        teammate_last_card = player.exposed_cards[TEAMMATE_NAME[player.name]][-1]

    if not teammate_last_card:
        raise Exception("should not happen")
        return random.sample(cards, 13 - round)

    return teammate_last_card


def get_exposed_cards(player) -> set:
    """Returns a set of all exposed cards"""
    exposed_cards = set()
    for player_cards in player.exposed_cards.values():
        for card in player_cards:
            exposed_cards.add(card)

    return exposed_cards


def remove_impossible_cards(player, combination: list[Card]) -> list[Card]:
    """Receives teammate's combination
    Removes impossible cards from the combination
    Impossible cards are cards that have been dealt or are in my hand"""
    cards_to_guess = []
    exposed_cards = get_exposed_cards(player)

    for c in combination:
        if c not in player.hand and c not in exposed_cards:
            cards_to_guess.append(c)

    return cards_to_guess


def corrected_cVal(player, idx):
    """Calculate the corrected cVal out of a specific guess
    The corrected cVal deducts one point for every correct card our player guessed that has since been played
    """
    original = player.cVals[idx]

    teammates_exposed = player.exposed_cards[TEAMMATE_NAME[player.name]]

    # how many of our teammate's cards we guessed in that round
    # have since been played (exposed)
    exposed_guesses = set(player.guesses[idx]).intersection(set(teammates_exposed))

    # original cVal - correct but exposed cards
    return original - len(exposed_guesses)


def get_most_likely_cards(player, cards):
    """
    Returns a list of tuple(Card, probability: float),
    with the cards that are most likely in the hands of our teammate first
    """

    likelyhood = dict()
    seen = dict()

    # keep track of how many times we've seen each card
    for card in cards:
        seen[card] = 0

    for idx, guess in enumerate(player.guesses):
        valid_cards = remove_impossible_cards(player, guess)
        cVal = corrected_cVal(player, idx)

        # calculate average probability of each guessed card being in our teammate's hand
        for valid_card in valid_cards:
            seen_count = seen[valid_card]
            if seen_count == 0:
                # first time we're seeing this card
                # its probability is the cVal from our guess divided
                # by the number of all possible cards from that guess
                likelyhood[valid_card] = cVal / len(valid_cards)
            else:
                prob = likelyhood[valid_card]
                # calculate the average probability out of all our guesses
                likelyhood[valid_card] = (
                    prob * seen_count + cVal / len(valid_cards)
                ) / (seen_count + 1)

            seen[valid_card] = seen_count + 1

    return sorted(
        [(k, v) for k, v in likelyhood.items()], key=lambda x: x[1], reverse=True
    )


def add_likely_cards(player, combination, cards):
    most_likely = get_most_likely_cards(player, cards)

    likelies = []

    while len(combination) + len(likelies) < 13 - len(player.played_cards):
        if len(most_likely) > 0:
            best_card = most_likely.pop(0)[0]
            likelies.append(best_card)
        # if we don't have any likely cards
        # just add a random card to the list
        else:
            random_card = remove_impossible_cards(player, cards)[0]
            likelies.append(random_card)

    return combination + likelies


def unlikeliest_card(player: Player, deck: Deck) -> Card:
    # how many times have we shown each card
    shown = dict()
    for card in player.hand:
        shown[card] = 0

    for idx, played_card in enumerate(player.played_cards):
        combination = get_shuffle(played_card)[: 12 - idx]

        for card in combination:
            if card in shown:
                shown[card] += 1

    # order the cards depedening on how often they showed up
    unlikely_cards = sorted([(k, v) for k, v in shown.items()], key=lambda x: x[1])

    return unlikely_cards[0][0]


def get_card_indication_freq(player: Player):
    all_cards = get_possible_cards()
    card_probabilities = {
        card: 0 for card in remove_impossible_cards(player, all_cards)
    }

    for idx, played_card in enumerate(player.exposed_cards[TEAMMATE_NAME[player.name]]):
        shuffled_cards = get_teammate_shuffle(player, played_card)
        combination = shuffled_cards[: 12 - idx]

        for card in combination:
            if card in card_probabilities:
                card_probabilities[card] += 1

    return card_probabilities


def get_card_probabilities(
    player: Player, cards: list[Card], round: int
) -> dict[Card, float]:
    all_cards = get_possible_cards()
    card_probabilities = {
        card: [] for card in remove_impossible_cards(player, all_cards)
    }

    for idx, guess in enumerate(player.guesses):
        valid_guesses = remove_impossible_cards(player, list(set(guess)))
        cVal = corrected_cVal(player, idx)

        for card in card_probabilities.keys():
            if card in valid_guesses:
                card_probabilities[card].append(cVal / len(valid_guesses))
            else:
                card_probabilities[card].append(
                    (len(card_probabilities) - len(valid_guesses) - cVal)
                    / (len(card_probabilities) - len(valid_guesses))
                )

    return card_probabilities


def playing(player: Player, deck: Deck):
    """
    Player 3 strategy
    """

    if not player.hand:
        return None

    if not USE_UNLIKELY_CARD_STRATEGY:
        card_to_play = card_with_best_seed_improved(player)
    else:
        if len(player.guesses) < SEED_ROUNDS:
            card_to_play = card_with_best_seed(player)
        else:
            # play the card my teammate is unlikeliest to guess
            card_to_play = unlikeliest_card(player, deck)

    return player.hand.index(card_to_play)

    # raise Exception("This should never happen")


def guessing(player, cards, round):
    """
    Player 3 Guess
    """

    if (
        not USE_UNLIKELY_CARD_STRATEGY
    ):  # Set to False because this strategy is not optimized yet
        card_p = get_card_probabilities(player, cards, round)
        card_freq = get_card_indication_freq(player)

        combined_prob = dict()

        valid_cards = remove_impossible_cards(player, get_possible_cards())
        for card in valid_cards:
            average_prob = sum(card_p[card]) / len(card_p[card]) if card_p[card] else 0
            combined_prob[card] = average_prob + card_freq[card] * (0.4 - round * 0.03)

        combination = sorted(
            combined_prob, key=lambda c: combined_prob[c], reverse=True
        )
        combination = combination[: 13 - round]
    else:
        if len(player.guesses) < SEED_ROUNDS:
            teammate_last_card = get_teammate_last_card(player)
            shuffled_cards = get_teammate_shuffle(player, teammate_last_card)
            combination = shuffled_cards[: 13 - len(player.played_cards)]
            combination = remove_impossible_cards(player, combination)
            combination = add_likely_cards(player, combination, cards)
        else:
            combination = add_likely_cards(player, [], cards)

        if round == 13 and SAVE_SEED_SCORE_DATA:
            # to save seed scores, make sure Player.seed_scores exists
            # def __init__():
            #     self.seed_scores = []
            # def add_seed_score(self, score):
            #     self.seed_scores.append(score)
            with open(f"seed_scores.csv", mode="a", newline="") as f:
                writer = csv.writer(f)
                # this fails unless player.seed_scores exists
                # writer.writerows(player.seed_scores)

    return combination
