import random
from CardGame import Card
from copy import copy
import numpy as np



def playing(player, deck):
    global seeds
    # Determine the random seed to use based on the number of cards already played
    random_seed_index = len(player.played_cards)
    # print(f"Random seed index in playing is {random_seed_index}.")
    random_seed = seeds[random_seed_index]
    # print(f"Playing: Random seed is: {random_seed}.")

    # Get the random mapping for the entire deck
    card_mapping = randomize_card_mapping(copy(deck.copyCards), random_seed)

    # Find the card in the player's hand that has the maximum random mapping value

    # Find the card in the player's hand that has the maximum random mapping value
    try:
        max_card = max(player.hand, key=lambda card: card_mapping[card])
    except KeyError as e:
        print(f"\nKeyError: {e} - This card is not found in the card_mapping dictionary")

    # set max card as the maximum index card in the player hand using convert_card_to_index
    if (len(player.played_cards) + 1) % 2 == 1:
        max_card = max(player.hand, key=lambda card: convert_card_to_index(card))
    else:
        max_card = min(player.hand, key=lambda card: convert_card_to_index(card))
    return player.hand.index(max_card)

    
def guessing(player, cards, round):
    """
    Update available guesses and probabilities and return the top guesses by probability
    """
    
    # Initialize available guesses and probabilities
    available_guesses = np.ones(DECK_SIZE, dtype=bool)
    probabilities = np.full(DECK_SIZE, PAR_PROBABILITY, dtype=float)

    # Update available guesses and probabilities
    available_guesses = update_available_guesses(player, available_guesses, cards, round)
    probabilities = update_probabilities(player, round, available_guesses, probabilities)
    
    # Set unavailable cards to zero probability
    probabilities[~available_guesses] = 0

    # print the number of zero entries in probabilities:
    # print(f"Number of non-zero entries in probabilities: {52 - np.count_nonzero(probabilities == 0)}")

    # Return top guesses by probability
    candidate_guesses = probabilities.argsort()[::-1][:13-round]
    guesses = [card for card in cards if convert_card_to_index(card) in candidate_guesses]
    return guesses


def update_available_guesses(player, available_guesses, cards, round):
    """
    Update available guesses by removing cards in hand, played and exposed cards,
    as well as cards outside of partner's min/max
    """
    global seeds

    to_remove = player.hand + player.played_cards + player.exposed_cards['North'] + player.exposed_cards['East'] + player.exposed_cards['South'] + player.exposed_cards['West']
    for card in to_remove:
        card_idx = convert_card_to_index(card)
        available_guesses[card_idx] = False
    
    for i, guess in enumerate(player.guesses):
        if player.cVals[i] == 0:
            for card in guess:
                card_idx = convert_card_to_index(card)
                available_guesses[card_idx] = False

    for i in range(1, round+1):
        random_seed_index = i - 1
        # print(f"Random seed index in guessing is {random_seed_index}.")
        random_seed = seeds[random_seed_index]
        # print(f"Random seed in guessing is {random_seed}.")
        card_mapping = randomize_card_mapping(copy(cards), random_seed)
        #print(f"Guessing: Round {i} random seed: {random_seed}")
        partner_card = player.exposed_cards[PARTNERS[player.name]][i-1]
        # removed_cards = [card for card in copy(cards) if card_mapping[card] > card_mapping[partner_card]]
        if i % 2 == 1:
            removed_cards = [card for card in copy(cards) if convert_card_to_index(card) > convert_card_to_index(partner_card)]
        else:
            removed_cards = [card for card in copy(cards) if convert_card_to_index(card) < convert_card_to_index(partner_card)]
        
        for removed_card in removed_cards:
            card_idx = convert_card_to_index(removed_card)
            available_guesses[card_idx] = False
    
    return available_guesses


def update_probabilities(player, round, available_guesses, probabilities):
    """
    Update probabilities by various strategies
    """
    # Set unavailable cards to zero probability
    probabilities[~available_guesses] = 0

    # Update probabilities based on previous rounds' guesses and cVals
    partner_name = partner[player.name]
    opponents_names = opponents[player.name]

    opponents_exposed = player.exposed_cards[opponents_names[0]] + player.exposed_cards[opponents_names[1]]
    partner_exposed = player.exposed_cards[partner_name]

    for i in range(round - 1):
        numerator = player.cVals[i]
        denominator = OPENING_HAND_SIZE - 1 - i

        for card in player.guesses[i]:
            if card in partner_exposed:
                numerator -= 1
                denominator -= 1
            if card in opponents_exposed:
                denominator -= 1
        
        for card in player.guesses[i]:
            if card not in partner_exposed and card not in opponents_exposed:
                card_idx = convert_card_to_index(card)
                accuracy = numerator / denominator if denominator > 0 else 0
                if probabilities[card_idx] != 0 and probabilities[card_idx] != 1:
                    probabilities[card_idx] = accuracy

    for i in range(len(player.guesses) - 1):
        remaining_guess_1 = set(player.guesses[i]).difference(set(opponents_exposed + partner_exposed))
        remaining_guess_2 = set(player.guesses[i+1]).difference(set(opponents_exposed + partner_exposed))
        remaining_cval_1 = player.cVals[i] - len(set(player.guesses[i]).intersection(set(partner_exposed)))
        remaining_cval_2 = player.cVals[i+1] - len(set(player.guesses[i+1]).intersection(set(partner_exposed)))
        # if all guess_1 is a subset of guess_2 (plus one other card) and c_calue is one more:
        if remaining_guess_1.issubset(remaining_guess_2) and remaining_guess_1 != remaining_guess_2:
            difference_2 = remaining_cval_2 - remaining_cval_1
            len_set_difference_2 = len(remaining_guess_2.difference(remaining_guess_1))
            for card in remaining_guess_2:
                if card not in remaining_guess_1:
                    card_idx = convert_card_to_index(card)
                    if probabilities[card_idx] != 0 and probabilities[card_idx] != 1:
                        probabilities[card_idx] = difference_2/len_set_difference_2
        elif remaining_guess_2.issubset(remaining_guess_1) and remaining_guess_1 != remaining_guess_2:
            difference_1 = remaining_cval_1 - remaining_cval_2
            len_set_difference_1 = len(remaining_guess_1.difference(remaining_guess_2))
            for card in remaining_guess_1:
                if card not in remaining_guess_2:
                    card_idx = convert_card_to_index(card)
                    if probabilities[card_idx] != 0 and probabilities[card_idx] != 1:
                        probabilities[card_idx] = difference_1/len_set_difference_1

    return probabilities


def convert_card_to_index(card):
    """
    Convert Card object to an index ranking by value then suit
    """
    suit_idx = suit_to_idx[card.suit]
    value_idx = value_to_idx[card.value]
    return value_idx * 4 + suit_idx


def convert_index_to_card(index):
    """
    Convert index to Card object
    """
    suit_idx = index % 4
    value_idx = index // 4
    suit = list(suit_to_idx.keys())[suit_idx]
    value = list(value_to_idx.keys())[value_idx]
    return Card(suit, value)


def randomize_card_mapping(deck_cards, seed):
    """
    Randomizes the mapping of the entire deck to indices using the given seed.
    """
    random.seed(seed)
    
    # Shuffle the deck cards using the provided seed
    shuffled_indices = list(range(DECK_SIZE))
    random.shuffle(shuffled_indices)
    
    # Create a mapping of each card in the deck to a random index
    card_to_random_map = {card: shuffled_indices[i] for i, card in enumerate(copy(deck_cards))}
    return card_to_random_map

"""
Static global variables
"""
seeds = list(range(1000))     
DECK_SIZE = 52
OPENING_HAND_SIZE = 13
PAR_PROBABILITY = 1/3

suit_to_idx = {"Diamonds": 0, "Clubs": 1, "Hearts": 2, "Spades": 3}
value_to_idx = {
    "2": 0,
    "3": 1,
    "4": 2,
    "5": 3,
    "6": 4,
    "7": 5,
    "8": 6,
    "9": 7,
    "10": 8,
    "J": 9,
    "Q": 10,
    "K": 11,
    "A": 12,
}
partner = {"North": "South", "East": "West", "South": "North", "West": "East"}
opponents = {
    "North": ["East", "West"],
    "East": ["South", "North"],
    "South": ["West", "East"],
    "West": ["North", "South"]
}

PARTNERS = {
    'North': 'South',
    'East': 'West',
    'South': 'North',
    'West': 'East',
}