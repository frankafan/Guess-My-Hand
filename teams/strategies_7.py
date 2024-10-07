import random
import numpy as np
from CardGame import Card, Deck, Player
import numpy as np

# G7 is the best

flag = 0

SUITS = ["Clubs", "Diamonds", "Hearts", "Spades"]
VALUES = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
NUM_CARDS = len(SUITS) * len(VALUES)

# This is deprecated but for the sake of structure i'll leave it
CARD_PROBABILITIES = {num:1/39 for num in range(NUM_CARDS)}

# Create a dictionary that maps 0-51 to (value, suit)
NUM_TO_CARD = {
    i: (SUITS[i // 13], VALUES[i % 13])  # i % 13 gives the card value, i // 13 gives the suit
    for i in range(NUM_CARDS)
}

REV_CARD_TO_NUM = {value:key for key, value in NUM_TO_CARD.items()}

#Stores guesses by player and round 
player_guesses = {}

# Assumptions:

# guessed_cards is a dict mapping turn number/round number -> player -> list of guessed cards that turn
# probability dict map indexed based on certain ordering -> probability of it being in your partners hand. 

def normalize(probability_dict):
    total_prob = sum(probability_dict.values())
    if total_prob > 0:
        for card in probability_dict:
            probability_dict[card] /= total_prob

def update_prob_based_on_correct_answers(probability_dict, guessed_cards, correct_answers):
    """
    Updates the probabilities for the cards in the guessed_cards list.

    Args:
        probability_dict (dict): A dictionary where keys are integers (0-51) representing cards
                                and probabilities.
        guessed_cards (list): A list of card indices representing the guessed cards.
        
    Returns:
        None: The probability_dict is updated in-place.
    """
    #print(f"Number of correct answers {correct_answers}")
    #print(correct_answers)

    perc_correct = correct_answers / len(guessed_cards)  # Factor to boost guessed cards
    perc_wrong =  1 - perc_correct
    #print(f"Perc of correct answers {perc_correct}")
    for card in guessed_cards:
            probability_dict[card] *= perc_correct

    non_guessed_cards = [card for card in probability_dict if card not in guessed_cards]

    for card in non_guessed_cards:
        probability_dict[card] *= perc_wrong

    normalize_probabilities()
    print(probability_dict)

def playing(player, deck):

    global flag

    turn = len(player.played_cards) + 1

    print("Turn: ", turn)

    flag =  (turn % 2)

    print("Flag: ", flag)
    if flag == 0:
        flag = 1
        print("Max First: Updated flag: ", flag)
        return max_first(player, deck)
    else:
        flag = 0
        print("Min first: Updated flag: ", flag)
        return min_first(player, deck)

def max_first(player, deck):
    """
    Max First strategy.
    
    This strategy always plays the highest-value card in the player's hand.
    
    Parameters:
    player (Player): The current player object.
    deck (Deck): The current deck object.
    
    Returns:
    int or None: The index of the card to be played, or None if no card can be played.
    """
    if not player.hand:
        return None
    
    value_order = deck.values
    max_index = 0
    max_value = -1

    for i, card in enumerate(player.hand):
        value = value_order.index(card.value)
        if value > max_value:
            max_value = value
            max_index = i
    
    return max_index

def normalize_probabilities():
    total = sum(CARD_PROBABILITIES.values())
    if total > 0:
        for card in CARD_PROBABILITIES:
            CARD_PROBABILITIES[card] /= total
    else:
        # This is after all the cards have been played - so no exception
        CARD_PROBABILITIES[0] = 1

def zero_probabilities(cards):
    for card in cards:
        suit = card.suit
        val = card.value
        num = REV_CARD_TO_NUM[(suit, val)]
        CARD_PROBABILITIES[num] = 0.0
    normalize_probabilities()

def min_first(player, deck):
    """
    Min First strategy.
    
    This strategy always plays the lowest-value card in the player's hand.
    
    Parameters:
    player (Player): The current player object.
    deck (Deck): The current deck object.
    
    Returns:
    int or None: The index of the card to be played, or None if no card can be played.
    """
    if not player.hand:
        return None
    
    value_order = deck.values
    min_index = 0
    min_value = len(value_order)
    
    for i, card in enumerate(player.hand):
        value = value_order.index(card.value)
        if value < min_value:
            min_value = value
            min_index = i
    
    return min_index

def update_card_probablities_based_on_seen_cards(player):
    """
    Update the probability of each card in the deck.
    """

    full_deck_size = 52
    
    global card_probability

    remaining_cards = full_deck_size - len(player.played_cards) - len(player.hand)

    for card in player.played_cards:
        card_probability[card] = 0

    for card in player.hand:
        card_probability[card] = 0

    # else, set its probability to 1 / # of cards remaining in the deck
    for key in card_probability:
        if key not in player.played_cards:
            card_probability[key] = 1 / remaining_cards


    for key in card_probability:
        card_probability[key] = 1 / 13

def zero_probabilities(prob_dict, cards):
    for card in cards:
        suit = card.suit
        val = card.value
        num = REV_CARD_TO_NUM[(suit, val)]
        prob_dict[num] = 0.0
    return normalize_probabilities(prob_dict)

def guessing(player, cards, round):
    global player_guesses
    if round == 1:
        global CARD_PROBABILITIES
        CARD_PROBABILITIES = {num:1/39 for num in range(NUM_CARDS)}
        zero_probabilities(player.hand)
        
    normalize_probabilities()
    exposed_cards = [i for j in list(player.exposed_cards.values()) for i in j]
    card_probs = zero_probabilities(card_probs, exposed_cards)
    card_probs = zero_probabilities(card_probs, player.played_cards)

    if round > 1:
        print(f"After round {round}, number of cvals : {player.cVals}")
    
    if round > 1: # We have c values 
        correct_answers = player.cVals[-1]
        previous_guesses = player_guesses[player.name].get(round - 1, [])
        print(correct_answers)
        print(len(previous_guesses))
        previous_guess_indices = [REV_CARD_TO_NUM[(card.suit, card.value)] for card in previous_guesses]
        update_prob_based_on_correct_answers(CARD_PROBABILITIES, previous_guess_indices, correct_answers)

    choice = np.random.choice(
        list(card_probs.keys()),
        13 - round,
        p=list(card_probs.values()),
        replace=False)
    card_choices = [NUM_TO_CARD[card] for card in choice]
    card_choices_obj = [Card(card[0], card[1]) for card in card_choices]

    if player.name not in player_guesses:
        player_guesses[player.name] = {}  # Initialize if not present

    player_guesses[player.name][round] = card_choices_obj

    return card_choices_obj
    card_probs = {num:1/39 for num in range(NUM_CARDS)}
    card_probs = zero_probabilities(card_probs, player.hand)

    exposed_cards = [i for j in list(player.exposed_cards.values()) for i in j]
    zero_probabilities(exposed_cards)
    zero_probabilities(player.played_cards)

    if round > 1:
        print(f"After round {round}, number of cvals : {player.cVals}")
    
    if round > 1: # We have c values 
        correct_answers = player.cVals[-1]
        previous_guesses = player_guesses[player.name].get(round - 1, [])
        print(correct_answers)
        print(len(previous_guesses))
        previous_guess_indices = [REV_CARD_TO_NUM[(card.suit, card.value)] for card in previous_guesses]
        update_prob_based_on_correct_answers(CARD_PROBABILITIES, previous_guess_indices, correct_answers)

    choice = np.random.choice(
        list(CARD_PROBABILITIES.keys()),
        13 - round,
        p=list(CARD_PROBABILITIES.values()),
        replace=False)
    card_choices = [NUM_TO_CARD[card] for card in choice]
    card_choices_obj = [Card(card[0], card[1]) for card in card_choices]

    if player.name not in player_guesses:
        player_guesses[player.name] = {}  # Initialize if not present

    player_guesses[player.name][round] = card_choices_obj

    return card_choices_obj
