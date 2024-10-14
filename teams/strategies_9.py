from collections import defaultdict, deque
from CardGame import Card, Deck, Player
import random
from teams.group9.constants import (
    CARD_VAL,
    CARD_SHIFT,
    SUIT_VAL,
    TEAMMATE,
    # PLAYER_GUESSES,
    # EXPOSED_CARDS
)

"""
PLAYER CLASS VARIABLES

self.name = name
self.hand = []
self.played_cards = []
self.strategy = strategy
self.exposed_cards = {"North": [], "East": [], "South": [], "West": []}
self.cVals = []
"""

"""
CARDS CLASS VARIABLES

self.suit = suit
self.value = value
self.map = {"Hearts": "♥", "Diamonds": "♦", "Clubs": "♣", "Spades": "♠"}
self.rmap = {"♥": "Hearts", "♦": "Diamonds", "♣": "Clubs", "♠": "Spades"}
"""

"""
DECK CLASS VARIABLES

self.suits = ["Hearts", "Diamonds", "Clubs", "Spades"] 
self.values = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
self.cards = [Card(suit, value) for suit in self.suits for value in self.values]
"""

# # Use to get card value with order 2 to A
# CARD_VAL = {
#     '2' : 0,
#     '3' : 1,
#     '4' : 2,
#     '5' : 3,
#     '6' : 4,
#     '7' : 5,
#     '8' : 6,
#     '9' : 7,
#     '10' : 8,
#     'J' : 9,
#     'Q' : 10,
#     'K' : 11,
#     'A' : 12,
# }
# # Use to shift card value
# CARD_SHIFT = {
#     '2' : '3',
#     '3' : '4',
#     '4' : '5',
#     '5' : '6',
#     '6' : '7',
#     '7' : '8',
#     '8' : '9',
#     '9' : '10',
#     '10' : 'J',
#     'J' : 'Q',
#     'Q' : 'K',
#     'K' : 'A',
#     'A' : 'A',
# }
# # Use to get suit value
# SUIT_VAL = {
#     'Spades' : 0,
#     'Clubs' : 1,
#     'Hearts' : 2,
#     'Diamonds' : 3,
# }

# # Use to get teammate of current player
# TEAMMATE = {
#     "North" : "South",
#     "South" : "North",
#     "East" : "West",
#     "West" : "East",
# }

# # teammate_max = ''
# PLAYER_GUESSES = {
#     'North' : [],
#     'East' : [],
#     'South' : [],
#     'West' : []
# }

# EXPOSED_CARDS = []

def check_possible(card, player):
    return (card not in player.hand) and (card not in [card for cards in player.exposed_cards.values() for card in cards])

def initialize(deck):
    mapping = {
        'Spades' : 1,
        'Clubs' : 2,
        'Hearts' : 3,
        'Diamonds' : 4
    }
    org_deck = defaultdict(list)
    for card in deck.cards:
        org_deck[mapping[card.suit]].append(card)
    
    for idx in mapping.values():
        org_deck[idx].sort(key = lambda x : CARD_VAL[x.value])
    
    return org_deck

def shuffle(player, deck, role='playing', use='shuffle', round=None):

    #exclude the cards that are exposed in this round
    # exposed_now = len(EXPOSED_CARDS) % 4
    # if exposed_now != 0:
    #     # Remove the excess elements from the end
    #     prev_exposed_cards = EXPOSED_CARDS[:-exposed_now]
    # else:
    #     prev_exposed_cards = EXPOSED_CARDS

    if use == 'shuffle':
        prev_index = min([len(exposed) for exposed in player.exposed_cards.values()])
        if role == 'guessing':
            prev_index -= 1
        prev_exposed_cards = []
        for exposed in player.exposed_cards.values():
            prev_exposed_cards += exposed[:prev_index] if len(exposed) > prev_index else exposed

        remaining_cards = list(set(deck.cards) - set(prev_exposed_cards))
        # print(len(remaining_cards))

        # Shuffle remaining_cards using the provided seed for consistency
        seed = len(remaining_cards)
    elif use == 'calc_prob':
        prev_index = round - 1
        prev_exposed_cards = []
        for exposed in player.exposed_cards.values():
            prev_exposed_cards += exposed[:prev_index]
        
        remaining_cards = list(set(deck.cards) - set(prev_exposed_cards))
        seed = len(remaining_cards)
    else:
        assert "Invalid use case"
    # print(f'SEED : {seed} for Player {player.name} when {role}')
    random.seed(seed)
    random.shuffle(remaining_cards)

    group_len = len(remaining_cards) // 4

    shuffled_dict = {}
    
    for i in range(4):
        start_index = i * group_len
        shuffled_dict[i + 1] = remaining_cards[start_index:start_index + group_len]
    
    return shuffled_dict

# Converts a card to the index in card_probability
# def card_to_index (suit, val):
#     return (13 * SUIT_VAL[suit]) + CARD_VAL[val]
# Use to get the current probability of guessing a card
# Keys: Card Object, Val : 1

# Remove cards from player.hand in card_probability 
def remove_cards_from_hand(player, card_probability):
    for card in player.hand:
        if card in card_probability:
            del card_probability[card]


# Remove cards from exposed cards in card_probability 
def remove_cards_from_exposed_cards(player, card_probability):
    for cards in player.exposed_cards.values():
        for exposed_card in cards:
            if exposed_card in card_probability:
                del card_probability[exposed_card]

    

# Eliminate the index less than the min
def eliminate_min_ind(card_probability, exposed_card, deck_dict):
    for suit in deck_dict.keys():
        if exposed_card in deck_dict[suit]:
            # print(player.name)
            # print(f'Teammate card: {teammate_card}')
            # print(f'Suit: {suit}, {deck_dict[suit]}')
            cur_suit = suit
            break
    # print("THE EXPOSED CARD IS: ", exposed_card)
    # print(f"Suit: {deck_dict[cur_suit]}")
    count = 0
    for card in deck_dict[cur_suit][:deck_dict[cur_suit].index(exposed_card)]:
        # print("I AM REMOVING: ", (card.value, card.suit))
        if card in card_probability:
            count += 1
            del card_probability[card]
    # print(f'I REMOVED {count} CARDS')
        

# Updates card_probability based on previous guesses
def update_card_probability(player, card_probability, round):
    total_viable_cards = len(card_probability)
    teammate_played_cards = player.exposed_cards[TEAMMATE[player.name]]

    for ind, guesses in enumerate(player.guesses):
        deck = Deck()
        deck_dict = dict()
        if ind == 0:
            deck_dict = initialize(deck)
        else:
            deck_dict = shuffle(player, deck, role='guessing', use='calc_prob', round=ind + 1)
        # print(f"Shuffled deck: {deck_dict}")

        exposed_card = player.exposed_cards[TEAMMATE[player.name]][ind]

        eliminate_min_ind(card_probability, exposed_card, deck_dict)

        correct_guesses = player.cVals[ind]
        total_guesses = len(guesses)
        
        # if ind == 0:
            # print("I GUESSED ", total_guesses, " CARDS AND GOT ", correct_guesses, " OF THEM RIGHT LAST TURN.")
            # val_check_arr = []
            # for card in guesses:
            #     val_check_arr.append((card.value, card.suit))
            # print("MY PREV GUESSES: ", val_check_arr)

        num = correct_guesses
        den = total_guesses

        for card in guesses:
            if card not in card_probability:
                if card in teammate_played_cards:
                    num -= 1
                den -= 1
        
        if den > 0:
            guess_prob = num / den

            for card in guesses:
                if card in card_probability:
                    if guess_prob <= 0:
                        del card_probability[card]
                    else:
                        card_probability[card] *= guess_prob
        
        unguessed_cards = set()

        for card in card_probability:
            if card not in guesses:
                unguessed_cards.add(card)
        
        num_of_unguessed_cards = len(unguessed_cards)

        if num_of_unguessed_cards > 0:
            missed_guesses = total_guesses - correct_guesses
            unGuess_prob = missed_guesses / num_of_unguessed_cards

            for card in unguessed_cards:
                if unGuess_prob <= 0:
                    del card_probability[card]
                else:
                    card_probability[card] *= unGuess_prob

    deck = Deck()
    deck_dict = dict()
 

    deck_dict = shuffle(player, deck, role='guessing', use='calc_prob', round=round)
    # print(f"Shuffled deck: {deck_dict}")

    exposed_card = player.exposed_cards[TEAMMATE[player.name]][round - 1]
    # print("WHAT MY TEAMMATE PLAYED: ", exposed_card)

    eliminate_min_ind(card_probability, exposed_card, deck_dict)

    
    # print("I AM PLAYER ", player.name, " AND THIS IS MY PROBABILITY:")
    # print_probability_table(card_probability)
    # print(f"WE HAVE {len(card_probability.keys())} CARDS LEFT")

def print_probability_table(card_probability):
    sorted_cards =  sorted(card_probability.keys(), key=lambda x : card_probability[x], reverse=True)
    for card in sorted_cards:
        print((card.value, card.suit), ": ", card_probability[card])

def playing(player, deck):
    """Greedy Suit Strategy"""

    if not player.hand:
        return None
    
    # for cards in player.exposed_cards.values():
    #     for card in cards:
    #         if card not in EXPOSED_CARDS:
    #             # if player.name == "South":
    #             print(f'Our exposed cards: {card}')
    #             EXPOSED_CARDS.append(card)
    
    # for key in player.exposed_cards.keys():
    #     if player.exposed_cards[key] and player.name == "South":
    #         print(f'Actual exposed cards: {player.exposed_cards[key][-1]}')
    
    # Create dictionary for shuffled deck
    deck = Deck()
    if len(player.hand) == 13:
        # EXPOSED_CARDS = []
        deck_dict = initialize(deck)
        # print(deck_dict)
    else:
        deck_dict = shuffle(player, deck)
        # print(f"Shuffled deck: {deck_dict}")

    hand = defaultdict(list)
    suits = [1,2,3,4]
    # print(player.hand)
    for card in player.hand:
        for suit in suits:
            if card in deck_dict[suit]:
                hand[suit].append(card)
                break

    max_suit = max(hand, key=lambda key : len(hand[key]))
    # print(max_suit, hand[max_suit])

    # improve to min-max
    if len(hand[max_suit]) == len(player.hand):
        play_card = min(hand[max_suit], key = lambda card : deck_dict[max_suit].index(card))
        return player.hand.index(play_card)

    anti_suits = deque([1, 2, 3, 4])
    # print(abs(anti_suits.index(max_suit) - len(anti_suits)))
    # print(anti_suits)
    anti_suits.rotate(abs(anti_suits.index(max_suit) - (len(anti_suits) - 1)))
    # print(anti_suits)
    anti_suit = anti_suits[0]
    # print(max_suit, anti_suit)

    play_card_idx = -1
    while play_card_idx < 0:
        if hand[anti_suit]:
            play_card = min(hand[anti_suit], key = lambda card : deck_dict[anti_suit].index(card))
            play_card_idx = player.hand.index(play_card)
            # print(play_card_idx) 
        else:
            # anti_suits.rotate(-1)
            del hand[max_suit]
            # print(hand)
            max_suit = max(hand, key=lambda key : len(hand[key]))
            # print(max_suit)
            anti_suits = deque([1, 2, 3, 4])
            anti_suits.rotate(abs(anti_suits.index(max_suit) - (len(anti_suits) - 1)))
            anti_suit = anti_suits[0]
            # print(hand[anti_suit])
            if not hand[anti_suit]:
                anti_suit = max_suit
    
    # print(f'{player.name} --- MAX SUIT: {max_suit}, ANTI SUIT: {anti_suit}')

    return play_card_idx

def guessing(player, cards, round):
    """
    Guesses the Anti-Suit based on teammate's exposed card
    """

    deck = Deck()
    if round == 1:
        deck_dict = initialize(deck)
    else:
        deck_dict = shuffle(player, deck, role='guessing')
        # print(f"Shuffled deck: {deck_dict}")

    card_probability = {card : 1 for card in cards} # Initialize to 1
    remove_cards_from_hand(player, card_probability)
    # print("AFTER REMOVING FROM HAND: ", len(card_probability))
    remove_cards_from_exposed_cards(player, card_probability)
    # print("AFTER REMOVING FROM EXPOSED CARDS: ", len(card_probability))

    # print("Guesses: ", player.guesses)
    # print("Player cVals: ", player.cVals)
    if round > 1:
        update_card_probability(player, card_probability, round)

    num_of_guesses = 13 - round

    # Fill guesses with only probability after 6 rounds
    if round > 7:
        return sorted([card for card in card_probability.keys()], key = lambda x : card_probability[x], reverse=True)[:num_of_guesses]
    
    # for cards in player.exposed_cards.values():
    #     for i in range(len(cards) - 1):
    #         if cards[i] not in EXPOSED_CARDS:
    #             EXPOSED_CARDS.append(cards[i])


    # teammate_suit = player.exposed_cards[teammate[player.name]][-1].suit
    teammate_card = player.exposed_cards[TEAMMATE[player.name]][-1]
    teammate_suit = 0
    # print(teammate_card)
    for suit in deck_dict.keys():
        if teammate_card in deck_dict[suit]:
            # print(player.name)
            # print(f'Teammate card: {teammate_card}')
            # print(f'Suit: {suit}, {deck_dict[suit]}')
            teammate_suit = suit
            break

    anti_suits = deque([4,3,2,1])
    anti_suits.rotate(abs(anti_suits.index(teammate_suit) - (len(anti_suits) - 1)))
    teammate_max = anti_suits[0]
    # if not player.cVals:
    #     anti_suit = anti_suits[0]
    #     teammate_max = anti_suit
    # elif player.cVals[-1] == 0:
    #     anti_suits.rotate(round - 1)
    #     anti_suit = anti_suits[0]
    #     teammate_max = anti_suit
    # else:
    #     anti_suit = anti_suits[0]
    #     teammate_max = anti_suit
    # if player.cVals and player.cVals[-1] == 0:
    #     anti_suits.rotate(round - 1)
    #     anti_suit = anti_suits[0]
    #     teammate_max = anti_suit
    # else:
    #     anti_suit = anti_suits[0]
    #     teammate_max = anti_suit

    # print(f"{player.name} --- THIS IS TEAMMATE SUIT: {teammate_suit}, THIS IS ANTI SUIT: {teammate_max}")
    

    # # This is a testing print
    # val_check_arr = []
    # for card in potential_guesses:
    #     val_check_arr.append((card.value, card.suit))
    # print("Potential Guesses:", val_check_arr)
    
    potential_guesses = [card for card in deck_dict[teammate_max] if card in card_probability] # All 13 cards of the teammate_suit
    potential_guesses.sort(key=lambda x : deck_dict[teammate_max].index(x))

    # This is a testing print
    # val_check_arr = []
    # for card in potential_guesses:
    #     val_check_arr.append((card.value, card.suit))
    # print("Potential Guesses:", val_check_arr)
    
    if len(potential_guesses) < num_of_guesses:
        num_of_missing_cards = num_of_guesses - len(potential_guesses)
        extra_guesses = [card for card in card_probability if card not in potential_guesses]
        print("MY PRECIOUS CARDS: ", sorted(extra_guesses, key=lambda x : card_probability[x], reverse=True)[:num_of_missing_cards])
        potential_guesses.extend(sorted(extra_guesses, key=lambda x : card_probability[x], reverse=True)[:num_of_missing_cards])

    if len(potential_guesses) > num_of_guesses:
        potential_guesses = potential_guesses[round:] if len(potential_guesses[round:]) == num_of_guesses else potential_guesses[:num_of_guesses]
        print("MY PRECIOUS SUITS: ", potential_guesses)

    return potential_guesses

# def guessing(player, cards, round):
#     """
#     Guesses the Anti-Suit based on teammate's exposed card
#     """
#     num_of_guesses = 14 - round
#     teammate_value = player.exposed_cards[teammate[player.name]][0].value
#     teammate_suit = player.exposed_cards[teammate[player.name]][0].suit
#     anti_suits = deque(['Diamonds', 'Hearts', 'Clubs', 'Spades'])
#     anti_suits.rotate(abs(anti_suits.index(teammate_suit) - (len(anti_suits) - 1)))

#     if player.cVals and player.cVals[-1] == 0:
#         anti_suits.rotate(round - 1)
#         anti_suit = anti_suits[0]
#         teammate_max = anti_suit
#     else:
#         anti_suit = anti_suits[0]
#         teammate_max = anti_suit

#     potential_guesses = [card for card in cards if (card.suit == teammate_max and check_possible(card, player))] # All 13 cards of the teammate_suit
#     potential_guesses.sort(key=lambda x:CARD_VAL[x.value])

#     while len(potential_guesses) < num_of_guesses:
#         teammate_value = CARD_SHIFT[teammate_value]
#         if check_possible(Card(teammate_suit, teammate_value), player):
#             potential_guesses.append(Card(teammate_suit, str(teammate_value)))

#     return potential_guesses[:num_of_guesses]