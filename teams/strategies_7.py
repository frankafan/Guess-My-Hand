import logging
import random
import math
import numpy as np
from CardGame import Card, Deck, Player

logging.basicConfig(filename='group7.log', 
                    level=logging.DEBUG,  # Set to DEBUG to capture all messages
                    filemode='w',  # Clear the log file each time the program runs
                    format='%(message)s',)  # Only the message will be logged

logging.disable(logging.CRITICAL)

# G7 is the best


SUITS = ["Clubs", "Diamonds", "Hearts", "Spades"]
VALUES = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
NUM_CARDS = len(SUITS) * len(VALUES)
TEAMMATE = {"North": "South", "South": "North", "East": "West", "West": "East"}

# Create a dictionary that maps 0-51 to (value, suit)
NUM_TO_CARD = {
    i: (SUITS[i // 13], VALUES[i % 13])  # i % 13 gives the card value, i // 13 gives the suit
    for i in range(NUM_CARDS)
}

REV_CARD_TO_NUM = {value:key for key, value in NUM_TO_CARD.items()}

# These were found by testing to be optimal
MU = 500
SIGMA = 100

# Will play risky for this number of rounds
RISKY_MM_CUTOFF = 9
WRONG = 0

def gaussian_pdf(x, mu, sigma):
    return (1 / (sigma * math.sqrt(2 * math.pi))) * math.exp(-0.5 * ((x - mu) / sigma) ** 2)


def update_prob_based_on_correct_answers(player,probability_dict, guessed_cards, correct_answers, round):
    """
    Updates the probabilities for the cards in the guessed_cards list.

    Args:
        probability_dict (dict): A dictionary where keys are integers (0-51) representing cards
                                and probabilities.
        guessed_cards (list): A list of card indices representing the guessed cards.
        
    Returns:
        None: The probability_dict is updated in-place.
    """

    perc_correct = correct_answers / len(guessed_cards)  # Factor to boost guessed cards
    perc_wrong =  1 - perc_correct
    var_rounds = round/13
    var_round = var_rounds**2
    for card in guessed_cards:
            probability_dict[card] *= perc_correct

    non_guessed_cards = [card for card in probability_dict if card not in guessed_cards]

    for card in non_guessed_cards:
        probability_dict[card] *= perc_wrong

    normalize_probabilities(player)


def playing(player, deck):
   
    turn = len(player.played_cards) + 1
    round = turn
    if round == 1:
        player.last_min_played = -1
        player.last_max_played = 52
    if round < RISKY_MM_CUTOFF:
        return risky_min_max(player,deck)
    else:
        flag =  (turn % 2)
        if flag == 0:
            flag = 1
            return max_first(player, deck)
        else:
            flag = 0 
            return min_first(player, deck)


def risky_min_max(player, deck):
    if not player.hand:
        return None

    # Find highest card
    highest_card = -1
    for i, card in enumerate(player.hand):
        card_value = REV_CARD_TO_NUM[(card.suit, card.value)]
        if card_value > highest_card:
            highest_card = card_value
            max_index = i

    # Find lowest card
    lowest_card = 52
    for i, card in enumerate(player.hand):
        card_value = REV_CARD_TO_NUM[(card.suit, card.value)]
        if card_value < lowest_card:
            lowest_card = card_value
            min_index = i

    if (lowest_card - player.last_min_played < player.last_max_played - highest_card):
        player.last_max_played = highest_card
        return max_index
    else:
        player.last_min_played = lowest_card
        return min_index

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
    
    max_index = 0 

    highest_card = -1
    for i, card in enumerate(player.hand):
        card_value = REV_CARD_TO_NUM[(card.suit, card.value)]
        if card_value > highest_card:
            highest_card = card_value
            max_index = i
    return max_index

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

    lowest_card = 52
    for i, card in enumerate(player.hand):
        card_value = REV_CARD_TO_NUM[(card.suit, card.value)]
        if card_value < lowest_card:
            lowest_card = card_value
            min_index = i
    
    return min_index

def normalize_probabilities(player):
    total = sum(player.card_probabilities.values())
    if total > 0:
        for card in player.card_probabilities:
            player.card_probabilities[card] /= total
    else:
        # This is after all the cards have been played - so no exception
        player.card_probabilities[0] = 1

def zero_probabilities(player, cards):
    # print(cards)
    for card in cards:
        suit = card.suit
        val = card.value
        num = REV_CARD_TO_NUM[(suit, val)]
        player.card_probabilities[num] = 0.0
    normalize_probabilities(player)

def zero_below_card(player, card):
    # for each card below the card, set probability to 0
    suit = card.suit
    val = card.value
    num = REV_CARD_TO_NUM[(suit, val)]

    logging.debug(f"The lowest card number is (in number form) {num}")

    for i in range(num):
        player.card_probabilities[i] = 0.0
        logging.debug(f"Setting probability of card {i} to 0")
    normalize_probabilities(player)

def zero_above_card(player, card):
    # for each card above the card, set probability to 0
    suit = card.suit
    val = card.value
    num = REV_CARD_TO_NUM[(suit, val)]

    logging.debug(f"The highest card number is (in number form) {num}")
    
    for i in range(num, 52):
        player.card_probabilities[i] = 0.0
        logging.debug(f"Setting probability of card {i} to 0")
    normalize_probabilities(player)

def choose_cards(player, round, max_probs=False):
    if round == 13:
        return []
    if not max_probs:
        choices = np.random.choice(
            list(player.card_probabilities.keys()),
            13 - round,
            p=list(player.card_probabilities.values()),
            replace=False)
    else:
        choices = sorted(player.card_probabilities.keys(), key=lambda x:player.card_probabilities[x])[-(13 - round):]
    card_choices = [NUM_TO_CARD[card] for card in choices]
    card_choices_obj = [Card(card[0], card[1]) for card in card_choices]
    return card_choices_obj


def guessing(player, cards, round):
    if round == 1:
        player.player_guesses = {}
        player.card_probabilities = {num:gaussian_pdf(num, MU, SIGMA) for num in range(NUM_CARDS)}
        # player.card_probabilities = {num:1/39 for num in range(NUM_CARDS)}
        zero_probabilities(player, player.hand)
        player.last_min_zeroed = -1
        player.last_max_zeroed = 52
        
    exposed_cards = [i for j in list(player.exposed_cards.values()) for i in j]
    zero_probabilities(player, exposed_cards)
    zero_probabilities(player, player.played_cards)

    last_exposed_card = player.exposed_cards[TEAMMATE[player.name]][-1]
    last_exposed_card_index = REV_CARD_TO_NUM[(last_exposed_card.suit, last_exposed_card.value)]

    # # if even round, guess the highest card

    if round >= RISKY_MM_CUTOFF: 
        if round % 2 == 0:
            logging.debug(f"Zeroing highest card and above")
            zero_above_card(player, last_exposed_card)
        else:
            logging.debug(f"Zeroing below card and above")
            zero_below_card(player, last_exposed_card)

    # we guess min or max based on if the number is closer to the last min or the last max
    else:
        if (last_exposed_card_index - player.last_min_zeroed < player.last_max_zeroed - last_exposed_card_index):
            player.last_min_zeroed = last_exposed_card_index
            zero_below_card(player, last_exposed_card)
        else: 
            player.last_max_zeroed = last_exposed_card_index
            zero_above_card(player, last_exposed_card)

    if round > 1: # We have c values 
        correct_answers = player.cVals[-1]
        previous_guesses = player.player_guesses[player.name].get(round - 1, [])
        previous_guess_indices = [REV_CARD_TO_NUM[(card.suit, card.value)] for card in previous_guesses]
        update_prob_based_on_correct_answers(player, player.card_probabilities, previous_guess_indices, correct_answers, round)
            
    card_choices_obj = choose_cards(player, round, max_probs=True)

    if player.name not in player.player_guesses:
        player.player_guesses[player.name] = {}  # Initialize if not present

    player.player_guesses[player.name][round] = card_choices_obj


    return card_choices_obj
