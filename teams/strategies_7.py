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

"""
Add the following lines of code to Card Game for the code to work:

def __hash__(self):
        return hash((self.suit, self.value))

def __eq__(self, other):
        return (self.suit, self.value) == (other.suit, other.value)
        
"""
# G7 is the best

#Stores guesses by player and round 
player_guesses = {}

SUITS = ["Clubs", "Diamonds", "Hearts", "Spades"]
VALUES = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
NUM_CARDS = len(SUITS) * len(VALUES)
CARD_PROBABILITIES = {num:1/39 for num in range(NUM_CARDS)}
TEAMMATE = {"North": "South", "South": "North", "East": "West", "West": "East"}

# Create a dictionary that maps 0-51 to (value, suit)
NUM_TO_CARD = {
    i: (SUITS[i // 13], VALUES[i % 13])  # i % 13 gives the card value, i // 13 gives the suit
    for i in range(NUM_CARDS)
}

REV_CARD_TO_NUM = {value:key for key, value in NUM_TO_CARD.items()}

MU = 25.5
SIGMA = 100

def gaussian_pdf(x, mu, sigma):
    return (1 / (sigma * math.sqrt(2 * math.pi))) * math.exp(-0.5 * ((x - mu) / sigma) ** 2)


def update_prob_based_on_correct_answers(player,probability_dict, guessed_cards, correct_answers):
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

    normalize_probabilities(player)
    print(player.name)
    print(probability_dict)

def normalize(probability_dict):
    total_prob = sum(probability_dict.values())
    if total_prob > 0:
        for card in probability_dict:
            probability_dict[card] /= total_prob

def playing(player, deck):
   
    turn = len(player.played_cards) + 1

    flag =  (turn % 2)

    if flag == 0:
        flag = 1
        return max_first(player, deck)
    else:
        flag = 0 
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

    highest_card = -1
    for i, card in enumerate(player.hand):
        card_value = REV_CARD_TO_NUM[(card.suit, card.value)]
        if card_value > highest_card:
            highest_card = card_value
            max_index = i
    print(highest_card, NUM_TO_CARD[highest_card])
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
    global player_guesses
    if round == 1:
        # global player.card_probabilities
        player.card_probabilities = {num:gaussian_pdf(num, MU, SIGMA) for num in range(NUM_CARDS)}
        zero_probabilities(player, player.hand)
        
    normalize_probabilities(player)
    exposed_cards = [i for j in list(player.exposed_cards.values()) for i in j]
    zero_probabilities(player, exposed_cards)
    zero_probabilities(player, player.played_cards)

    last_exposed_card = player.exposed_cards[TEAMMATE[player.name]][-1]

    # # if even round, guess the highest card
    if round % 2 == 0:
        logging.debug(f"Zeroing highest card and above")
        print(f"Player {player.name} zeroing above {last_exposed_card}")
        zero_above_card(player, last_exposed_card)
    else:
        logging.debug(f"Zeroing below card and above")
        print(f"Player {player.name} zeroing below {last_exposed_card}")
        zero_below_card(player, last_exposed_card)

    if round > 1:
        print(f"After round {round}, number of cvals : {player.cVals}")
    
    if round > 1: # We have c values 
        correct_answers = player.cVals[-1]
        previous_guesses = player_guesses[player.name].get(round - 1, [])
        print(correct_answers)
        print(len(previous_guesses))
        previous_guess_indices = [REV_CARD_TO_NUM[(card.suit, card.value)] for card in previous_guesses]
        update_prob_based_on_correct_answers(player, player.card_probabilities, previous_guess_indices, correct_answers)


        

        logging.debug(f"Current Player: {player.name}")
        logging.debug(f"Current Teammate: {TEAMMATE[player.name]}")
        logging.debug(f"The player, {player.name}, is examining card: {player.exposed_cards[TEAMMATE[player.name]][-1]}")
        


        logging.debug(f"Summary of Player: {player.name}")
        logging.debug(player.card_probabilities)
        # sum of probabilities should be 1
        logging.debug(f"Total probability: {sum(player.card_probabilities.values())}")
            
    card_choices_obj = choose_cards(player, round, max_probs=True)

    if player.name not in player_guesses:
        player_guesses[player.name] = {}  # Initialize if not present

    player_guesses[player.name][round] = card_choices_obj


    return card_choices_obj
