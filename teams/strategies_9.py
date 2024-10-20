from collections import defaultdict, deque
from CardGame import Card, Deck, Player
import random
from teams.group9.constants import (
    CARD_VAL,
    TEAMMATE
)

# Initialize deck to original suits
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

# Shuffling deck and map to "fake" suits
def shuffle(player, deck, role='playing', use='shuffle', round=None):
    # If using to shuffle
    if use == 'shuffle':
        # To align seeds for both playing and guessing players
        prev_index = min([len(exposed) for exposed in player.exposed_cards.values()])
        if role == 'guessing':
            prev_index -= 1
        prev_exposed_cards = []

        # Removing previously exposed cards
        for exposed in player.exposed_cards.values():
            prev_exposed_cards += exposed[:prev_index] if len(exposed) > prev_index else exposed

        remaining_cards = list(set(deck.cards) - set(prev_exposed_cards))
        # Set seed as the length of remaining cards
        seed = len(remaining_cards)
    
    # If using to calculate probabilities for previous rounds
    elif use == 'calc_prob':
        prev_index = round - 1
        prev_exposed_cards = []
        for exposed in player.exposed_cards.values():
            prev_exposed_cards += exposed[:prev_index]
        
        remaining_cards = list(set(deck.cards) - set(prev_exposed_cards))
        seed = len(remaining_cards)
    else:
        assert "Invalid use case"

    random.seed(seed)
    random.shuffle(remaining_cards)

    group_len = len(remaining_cards) // 4

    shuffled_dict = {}
    
    # Organize into "fake" suits
    for i in range(4):
        start_index = i * group_len
        shuffled_dict[i + 1] = remaining_cards[start_index:start_index + group_len]
    
    return shuffled_dict

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

# Eliminate the index less than the index of your partner's played card
def eliminate_min_ind(card_probability, exposed_card, deck_dict):
    for suit in deck_dict.keys():
        if exposed_card in deck_dict[suit]:
            cur_suit = suit
            break
    count = 0
    for card in deck_dict[cur_suit][:deck_dict[cur_suit].index(exposed_card)]:
        if card in card_probability:
            count += 1
            del card_probability[card]
        

# Updates card_probability based on previous guesses
def update_card_probability(player, card_probability, round):
    # Get teammate's exposed cards
    teammate_played_cards = player.exposed_cards[TEAMMATE[player.name]]

    for ind, guesses in enumerate(player.guesses):
        # Initialize or Shuffle
        deck = Deck()
        deck_dict = dict()
        if ind == 0:
            deck_dict = initialize(deck)
        else:
            deck_dict = shuffle(player, deck, role='guessing', use='calc_prob', round=ind + 1)

        # Remove all cards from suit that have lower indices than teammate's played card
        exposed_card = player.exposed_cards[TEAMMATE[player.name]][ind]
        eliminate_min_ind(card_probability, exposed_card, deck_dict)

        correct_guesses = player.cVals[ind]
        total_guesses = len(guesses)
        num = correct_guesses
        den = total_guesses

        # Updating probabilities
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

    # Removing played cards in the current round
    deck = Deck()
    deck_dict = dict()
    deck_dict = shuffle(player, deck, role='guessing', use='calc_prob', round=round)
    exposed_card = player.exposed_cards[TEAMMATE[player.name]][round - 1]
    eliminate_min_ind(card_probability, exposed_card, deck_dict)

# Debugging tool to print probabilities
def print_probability_table(card_probability):
    sorted_cards =  sorted(card_probability.keys(), key=lambda x : card_probability[x], reverse=True)
    for card in sorted_cards:
        print((card.value, card.suit), ": ", card_probability[card])

# Main Playing Strategy
def playing(player, deck):
    """
    Greedy Max-Suit Strategy + Probability
    """
    # Base case
    if not player.hand:
        return None
    
    # Initialize or Shuffle
    deck = Deck()
    if len(player.hand) == 13:
        deck_dict = initialize(deck)
    else:
        deck_dict = shuffle(player, deck)

    # Organize current player's hand
    hand = defaultdict(list)
    suits = [1,2,3,4]
    for card in player.hand:
        for suit in suits:
            if card in deck_dict[suit]:
                hand[suit].append(card)
                break

    max_suit = max(hand, key=lambda key : len(hand[key]))

    # Play minimum-index if there's only one suit in hand
    if len(hand[max_suit]) == len(player.hand):
        play_card = min(hand[max_suit], key = lambda card : deck_dict[max_suit].index(card))
        return player.hand.index(play_card)

    anti_suits = deque([1, 2, 3, 4])
    anti_suits.rotate(abs(anti_suits.index(max_suit) - (len(anti_suits) - 1)))
    anti_suit = anti_suits[0]

    play_card_idx = -1
    while play_card_idx < 0:
        # If player has cards of anti-suit, play minimum index
        if hand[anti_suit]:
            play_card = min(hand[anti_suit], key = lambda card : deck_dict[anti_suit].index(card))
            play_card_idx = player.hand.index(play_card)
        else:
            # Else, find second max and play the second max's anti-suit
            del hand[max_suit]
            max_suit = max(hand, key=lambda key : len(hand[key]))
            anti_suits = deque([1, 2, 3, 4])
            anti_suits.rotate(abs(anti_suits.index(max_suit) - (len(anti_suits) - 1)))
            anti_suit = anti_suits[0]
            # If both the first and second max doesn't have anti-suits, just play the second max as the anti-suit
            if not hand[anti_suit]:
                anti_suit = max_suit

    return play_card_idx

# Main Guessing Strategy
def guessing(player, cards, round):
    """
    Guesses the Anti-Suit based on teammate's exposed card
    """
    num_of_guesses = 13 - round

    # Return the same guesss (except the card played in current turn) if we got everything right on the previous round
    if player.cVals and (player.cVals[-1] == num_of_guesses + 1):
        potential_guesses = player.guesses[-1]
        teammate_card = player.exposed_cards[TEAMMATE[player.name]][-1]
        potential_guesses.remove(teammate_card)
        return potential_guesses
    
    # Initialize or Shuffle
    deck = Deck()
    if round == 1:
        deck_dict = initialize(deck)
    else:
        deck_dict = shuffle(player, deck, role='guessing')

    # Initialize probability dictionary
    card_probability = {card : 1 for card in cards}

    # Remove previously exposed cards and cards in hand
    remove_cards_from_hand(player, card_probability)
    remove_cards_from_exposed_cards(player, card_probability)

    # Calculate and update probability dictionary
    if round > 1:
        update_card_probability(player, card_probability, round)

    # Fill guesses with only max-probability if player got greater than 70% or 7 cards correct in the previous round
    if player.cVals and ((player.cVals[-1] / (num_of_guesses + 1) >= 0.7) or player.cVals[-1] >= 7): 
        return sorted([card for card in card_probability.keys()], key = lambda x : card_probability[x], reverse=True)[:num_of_guesses]

    # Determine the suit and anti-suit of the card our teammate has played
    teammate_card = player.exposed_cards[TEAMMATE[player.name]][-1]
    teammate_suit = 0
    for suit in deck_dict.keys():
        if teammate_card in deck_dict[suit]:
            teammate_suit = suit
            break

    anti_suits = deque([4,3,2,1])
    anti_suits.rotate(abs(anti_suits.index(teammate_suit) - (len(anti_suits) - 1)))
    teammate_max = anti_suits[0]
    
    # All 13 cards of the teammate_suit
    potential_guesses = [card for card in deck_dict[teammate_max] if card in card_probability]
    potential_guesses.sort(key=lambda x : deck_dict[teammate_max].index(x))
    
    # Fill guesses with max-probability if we have more space
    if len(potential_guesses) < num_of_guesses:
        num_of_missing_cards = num_of_guesses - len(potential_guesses)
        extra_guesses = [card for card in card_probability if card not in potential_guesses]
        potential_guesses.extend(sorted(extra_guesses, key=lambda x : card_probability[x], reverse=True)[:num_of_missing_cards])

    # Prune guesses if we have too much
    if len(potential_guesses) > num_of_guesses:
        potential_guesses = potential_guesses[round:] if len(potential_guesses[round:]) == num_of_guesses else potential_guesses[:num_of_guesses]

    return potential_guesses