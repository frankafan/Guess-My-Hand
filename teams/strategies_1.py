import abc
import random
from typing import List

from CardGame import Deck, Player
from teams.strategy_1.weight_distribution import get_likelihood_weight_distribution
from teams.strategy_1.util import partner, card_to_idx, idx_to_card
from teams.strategy_1.turn_suits import get_fake_suits

remaining_cards_1 = {}
points_1 = {}
prev_guesses_1 = []
remaining_cards_2 = {}
points_2 = {}
prev_guesses_2 = []
LATE_GAME_INDEX = 10
SUIT_GUESS_POINTS = 1
INCORRECT_GUESS_POINTS = -0.5

guesses_and_c_vals_1 = []
guesses_and_c_vals_2 = []


def initialize_totals(deck, remaining_cards, points):
    # print("Initializing totals player")
    for card in deck.copyCards:
        remaining_cards[card_to_idx(card)] = 1
        points[card_to_idx(card)] = 0

def initialize_totals_guessing(deck, remaining_cards, points, player_name):
    # print("Initializing totals guessing")
    if player_name == "North" or player_name == "East":
        global prev_guesses_1
        prev_guesses_1 = []

        global guesses_and_c_vals_1
        guesses_and_c_vals_1 = []
    else:
        global prev_guesses_2
        prev_guesses_2 = []

        global guesses_and_c_vals_2
        guesses_and_c_vals_2 = []
    for card in deck:
        remaining_cards[card_to_idx(card)] = 1
        points[card_to_idx(card)] = 0

def remove_seen_till_last_round(exposed_cards, remaining_cards, points):
    for player in exposed_cards:
        remove_card(exposed_cards[player], remaining_cards, points)

def remove_seen_till_last_round_playing(exposed_cards, remaining_cards, points, cards_played):
    if cards_played == 0:
        return
    for player in exposed_cards:
        hand = exposed_cards[player]
        remaining_cards[card_to_idx(hand[cards_played-1])] = -100
        points[card_to_idx(hand[cards_played-1])] = -100

def remove_card(hand, remaining_cards, points):
    if len(hand) != 0:
        remaining_cards[card_to_idx(hand[-1])] = -100
        points[card_to_idx(hand[-1])] = -100

def remove_from_points(hand, points):
    for card in hand:
        points[card_to_idx(card)] = -100

class PlayingStrategy(abc.ABC):
    @abc.abstractmethod
    def guess(self, player: Player, cards, round) -> List[int]:
        pass

    @abc.abstractmethod
    def play(self, player: Player, deck: Deck) -> int:
        pass


class DefaultPlayingStrategy(PlayingStrategy):
    def guess(self, player: Player, cards, round) -> List[int]:
        return random.sample(cards, 13 - round)

    def play(self, player: Player, deck: Deck) -> int:
        if not player.hand:
            return None

        # Find the card with the highest value and suit

        value_order = deck.values
        max_index = 0
        max_value = -1

        for i, card in enumerate(player.hand):
            value = value_order.index(card.value)
            if value > max_value:
                max_value = value
                max_index = i
        return max_index

# def playing2(player, deck):
#     if player.name == "North" or player.name == "East":
#         remaining_cards_local = remaining_cards_1
#         points_local = points_1
#     else:
#         remaining_cards_local = remaining_cards_2
#         points_local = points_2
#     if len(player.cVals) == 0:
#         initialize_totals(deck, remaining_cards_local, points_local)
#
#     cards_played = len(player.cVals)
#     # print(player.exposed_cards)
#     remove_seen_till_last_round_playing(player.exposed_cards, remaining_cards_local, points_local, cards_played)
#     rem = []
#     for card in remaining_cards_local.keys():
#         if remaining_cards_local[card] != -100:
#             rem.append(card)
#     turn_number = len(player.cVals) + 1
#     rem = sorted(rem)
#     fake_suits = get_fake_suits(turn_number, rem, 4)
#
#     if turn_number < LATE_GAME_INDEX:
#         # Check which suit has the most cards in it matching with the player's hand
#         suit_counts = [0, 0, 0, 0]
#         for i, fake_suit in enumerate(fake_suits):
#             # Find number of cards matching with the player's hand
#             for card in player.hand:
#                 if card_to_idx(card) in fake_suit:
#                     suit_counts[i] += 1
#
#         # Find the id of the suit with the most cards and second most cards
#         max_suit_id = suit_counts.index(max(suit_counts))
#         suit_counts[max_suit_id] = -1
#         second_max_suit_id = suit_counts.index(max(suit_counts))
#         suit_counts[second_max_suit_id] = -1
#         third_max_suit_id = suit_counts.index(max(suit_counts))
#         suit_counts[third_max_suit_id] = -1
#         fourth_max_suit_id = suit_counts.index(max(suit_counts))
#
#         pointer_suit = fake_suits[max_suit_id - 1 if max_suit_id != 0 else 3]
#         pointer_suit = sorted(pointer_suit)
#         # Card with highest idx on even turns and with the lowest idx on odd turns and in hand
#         if turn_number % 2 == 0:
#             card_played_idx = -1
#             card_index = -1
#             for i, card in enumerate(player.hand):
#                 if card_to_idx(card) in pointer_suit and card_to_idx(card) > card_played_idx:
#                     card_played_idx = card_to_idx(card)
#                     card_index = i
#             if card_index == -1:
#                 second_pointer_suit = fake_suits[second_max_suit_id - 1 if second_max_suit_id != 0 else 3]
#                 second_pointer_suit = sorted(second_pointer_suit)
#                 for i, card in enumerate(player.hand):
#                     if card_to_idx(card) in second_pointer_suit and card_to_idx(card) > card_played_idx:
#                         card_played_idx = card_to_idx(card)
#                         card_index = i
#
#             if card_index == -1:
#                 third_pointer_suit = fake_suits[third_max_suit_id - 1 if third_max_suit_id != 0 else 3]
#                 third_pointer_suit = sorted(third_pointer_suit)
#                 for i, card in enumerate(player.hand):
#                     if card_to_idx(card) in third_pointer_suit and card_to_idx(card) > card_played_idx:
#                         card_played_idx = card_to_idx(card)
#                         card_index = i
#
#             if card_index == -1:
#                 fourth_pointer_suit = fake_suits[fourth_max_suit_id - 1 if fourth_max_suit_id != 0 else 3]
#                 fourth_pointer_suit = sorted(fourth_pointer_suit)
#                 for i, card in enumerate(player.hand):
#                     if card_to_idx(card) in fourth_pointer_suit and card_to_idx(card) > card_played_idx:
#                         card_played_idx = card_to_idx(card)
#                         card_index = i
#             return card_index
#         else:
#             card_played_idx = 60
#             card_index = -1
#             for i, card in enumerate(player.hand):
#                 if card_to_idx(card) in pointer_suit and card_to_idx(card) < card_played_idx:
#                     card_played_idx = card_to_idx(card)
#                     card_index = i
#             if card_index == -1:
#                 second_pointer_suit = fake_suits[second_max_suit_id - 1 if second_max_suit_id != 0 else 3]
#                 second_pointer_suit = sorted(second_pointer_suit)
#                 for i, card in enumerate(player.hand):
#                     if card_to_idx(card) in second_pointer_suit and card_to_idx(card) < card_played_idx:
#                         card_played_idx = card_to_idx(card)
#                         card_index = i
#
#             if card_index == -1:
#                 third_pointer_suit = fake_suits[third_max_suit_id - 1 if third_max_suit_id != 0 else 3]
#                 third_pointer_suit = sorted(third_pointer_suit)
#                 for i, card in enumerate(player.hand):
#                     if card_to_idx(card) in third_pointer_suit and card_to_idx(card) < card_played_idx:
#                         card_played_idx = card_to_idx(card)
#                         card_index = i
#
#             if card_index == -1:
#                 fourth_pointer_suit = fake_suits[fourth_max_suit_id - 1 if fourth_max_suit_id != 0 else 3]
#                 fourth_pointer_suit = sorted(fourth_pointer_suit)
#                 for i, card in enumerate(player.hand):
#                     if card_to_idx(card) in fourth_pointer_suit and card_to_idx(card) < card_played_idx:
#                         card_played_idx = card_to_idx(card)
#                         card_index = i
#             return card_index
#     else:
#         # Check which suit has the most cards in it matching with the player's hand
#         if turn_number %2 == 0:
#             card_played_idx = -1
#             card_index = -1
#             for i, card in enumerate(player.hand):
#                 if card_to_idx(card) > card_played_idx:
#                     card_played_idx = card_to_idx(card)
#                     card_index = i
#             return card_index
#         else:
#             card_played_idx = 60
#             card_index = -1
#             for i, card in enumerate(player.hand):
#                 if card_to_idx(card) < card_played_idx:
#                     card_played_idx = card_to_idx(card)
#                     card_index = i
#             return card_index

def playing(player, deck):
    if player.name == "North" or player.name == "East":
        remaining_cards_local = remaining_cards_1
        points_local = points_1
    else:
        remaining_cards_local = remaining_cards_2
        points_local = points_2
    if len(player.cVals) == 0:
        initialize_totals(deck, remaining_cards_local, points_local)

    cards_played = len(player.cVals)
    # print(player.exposed_cards)
    remove_seen_till_last_round_playing(player.exposed_cards, remaining_cards_local, points_local, cards_played)
    rem = []
    for card in remaining_cards_local.keys():
        if remaining_cards_local[card] != -100:
            rem.append(card)
    turn_number = len(player.cVals) + 1
    rem = sorted(rem)
    fake_suits = get_fake_suits(turn_number, rem, 4)

    if turn_number < LATE_GAME_INDEX:
        # Check which suit has the most cards in it matching with the player's hand
        suit_counts = [0, 0, 0, 0]
        for i, fake_suit in enumerate(fake_suits):
            # Find number of cards matching with the player's hand
            for card in player.hand:
                if card_to_idx(card) in fake_suit:
                    suit_counts[i] += 1

        # Find the id of the suit with the most cards and second most cards
        max_suit_id = suit_counts.index(max(suit_counts))
        suit_counts[max_suit_id] = -1
        second_max_suit_id = suit_counts.index(max(suit_counts))
        suit_counts[second_max_suit_id] = -1
        third_max_suit_id = suit_counts.index(max(suit_counts))
        suit_counts[third_max_suit_id] = -1
        fourth_max_suit_id = suit_counts.index(max(suit_counts))

        pointer_suit = fake_suits[max_suit_id - 1 if max_suit_id != 0 else 3]
        pointer_suit = sorted(pointer_suit)
        # Card with highest idx on even turns and with the lowest idx on odd turns and in hand
        if turn_number % 2 == 0:
            card_played_idx = -1
            card_index = -1
            for i, card in enumerate(player.hand):
                if card_to_idx(card) in pointer_suit and card_to_idx(card) > card_played_idx:
                    card_played_idx = card_to_idx(card)
                    card_index = i
            if card_index == -1:
                second_pointer_suit = fake_suits[second_max_suit_id - 1 if second_max_suit_id != 0 else 3]
                second_pointer_suit = sorted(second_pointer_suit)
                for i, card in enumerate(player.hand):
                    if card_to_idx(card) in second_pointer_suit and card_to_idx(card) > card_played_idx:
                        card_played_idx = card_to_idx(card)
                        card_index = i

            if card_index == -1:
                third_pointer_suit = fake_suits[third_max_suit_id - 1 if third_max_suit_id != 0 else 3]
                third_pointer_suit = sorted(third_pointer_suit)
                for i, card in enumerate(player.hand):
                    if card_to_idx(card) in third_pointer_suit and card_to_idx(card) > card_played_idx:
                        card_played_idx = card_to_idx(card)
                        card_index = i

            if card_index == -1:
                fourth_pointer_suit = fake_suits[fourth_max_suit_id - 1 if fourth_max_suit_id != 0 else 3]
                fourth_pointer_suit = sorted(fourth_pointer_suit)
                for i, card in enumerate(player.hand):
                    if card_to_idx(card) in fourth_pointer_suit and card_to_idx(card) > card_played_idx:
                        card_played_idx = card_to_idx(card)
                        card_index = i
            return card_index
        else:
            card_played_idx = 60
            card_index = -1
            for i, card in enumerate(player.hand):
                if card_to_idx(card) in pointer_suit and card_to_idx(card) < card_played_idx:
                    card_played_idx = card_to_idx(card)
                    card_index = i
            if card_index == -1:
                second_pointer_suit = fake_suits[second_max_suit_id - 1 if second_max_suit_id != 0 else 3]
                second_pointer_suit = sorted(second_pointer_suit)
                for i, card in enumerate(player.hand):
                    if card_to_idx(card) in second_pointer_suit and card_to_idx(card) < card_played_idx:
                        card_played_idx = card_to_idx(card)
                        card_index = i

            if card_index == -1:
                third_pointer_suit = fake_suits[third_max_suit_id - 1 if third_max_suit_id != 0 else 3]
                third_pointer_suit = sorted(third_pointer_suit)
                for i, card in enumerate(player.hand):
                    if card_to_idx(card) in third_pointer_suit and card_to_idx(card) < card_played_idx:
                        card_played_idx = card_to_idx(card)
                        card_index = i

            if card_index == -1:
                fourth_pointer_suit = fake_suits[fourth_max_suit_id - 1 if fourth_max_suit_id != 0 else 3]
                fourth_pointer_suit = sorted(fourth_pointer_suit)
                for i, card in enumerate(player.hand):
                    if card_to_idx(card) in fourth_pointer_suit and card_to_idx(card) < card_played_idx:
                        card_played_idx = card_to_idx(card)
                        card_index = i
            return card_index
    else:
        # Check which suit has the most cards in it matching with the player's hand
        max_suit = -1
        max_suit_count = -1
        for fake_suit in fake_suits:
            # Find number of cards matching with the player's hand
            count = 0
            for card in player.hand:
                if card_to_idx(card) in fake_suit:
                    count += 1
            if count > max_suit_count:
                max_suit = fake_suit
                max_suit_count = count

        max_suit = sorted(max_suit)
        # Card with highest idx on even turns and with the lowest idx on odd turns and in hand
        if turn_number %2 == 0:
            card_played_idx = -1
            card_index = -1
            for i, card in enumerate(player.hand):
                if card_to_idx(card) in max_suit and card_to_idx(card) > card_played_idx:
                    card_played_idx = card_to_idx(card)
                    card_index = i
            return card_index
        else:
            card_played_idx = 60
            card_index = -1
            for i, card in enumerate(player.hand):
                if card_to_idx(card) in max_suit and card_to_idx(card) < card_played_idx:
                    card_played_idx = card_to_idx(card)
                    card_index = i
            return card_index

def update_points_with_guesses(guesses, points, prob, c_val, datastore):
    for card in guesses:
        points[card_to_idx(card)] += prob + INCORRECT_GUESS_POINTS

    turn_data = {
        "guesses": guesses,
        "c_val": c_val
    }
    datastore.append(turn_data)


def guessing(player, cards, round):
    global prev_guesses_2
    global prev_guesses_1
    global guesses_and_c_vals_1
    global guesses_and_c_vals_2

    if player.name == "North" or player.name == "East":
        remaining_cards_local = remaining_cards_1
        points_local = points_1
        prev_guesses_local = prev_guesses_1
        guesses_and_c_vals_local = guesses_and_c_vals_1
    else:
        remaining_cards_local = remaining_cards_2
        points_local = points_2
        prev_guesses_local = prev_guesses_2
        guesses_and_c_vals_local = guesses_and_c_vals_2

    if round == 1:
        initialize_totals_guessing(cards, remaining_cards_local, points_local, player.name)
        remove_from_points(player.hand, points_local)

    # print("Remaining cards: ", remaining_cards_local)
    rem = []
    for card in remaining_cards_local.keys():
        if remaining_cards_local[card] != -100:
            rem.append(card)
    turn_number = len(player.cVals) + 1

    if turn_number > 1:
        update_points_with_guesses(
            prev_guesses_local,
            points_local,
            player.cVals[-1]/(13-round+1),
            player.cVals[-1],
            guesses_and_c_vals_local,
        )
    rem = sorted(rem)
    fake_suits = get_fake_suits(turn_number, rem, 4)

    # print(f"Check prob datastore: {guesses_and_c_vals_local}")
    # TODO: below is how you can get the weight distribution to use for guessing
    weight_distribution = get_likelihood_weight_distribution(guesses_and_c_vals_local)
    # print(f"w_d: {weight_distribution}")

    partner_card = player.exposed_cards[partner(player.name)][-1]
    partner_card_idx = card_to_idx(partner_card)
    # Find the suit of the card exposed by the partner
    if turn_number < LATE_GAME_INDEX:
        pointer_suit_id = -1

        # Get the suit containing partner card
        for i, suit in enumerate(fake_suits):
            if partner_card_idx in suit:
                pointer_suit_id = i
                break

        partner_suit = fake_suits[pointer_suit_id + 1 if pointer_suit_id != 3 else 0]
        pointer_suit = fake_suits[pointer_suit_id]
        partner_suit = sorted(partner_suit)

        if turn_number % 2 == 0:
            for i, card_idx in enumerate(pointer_suit):
                if card_idx > partner_card_idx:
                    points_local[card_idx] = -100
        else:
            for i, card_idx in enumerate(pointer_suit):
                if card_idx < partner_card_idx:
                    points_local[card_idx] = -100

        # Return the cards in the fake_suits[partner_suit]
        remove_seen_till_last_round(player.exposed_cards, remaining_cards_local, points_local)
        returned_cards = []
        for i, card in enumerate(partner_suit):
            if card != partner_card_idx and points_local[card] != -100:
                points_local[card] += SUIT_GUESS_POINTS
                returned_cards.append(idx_to_card(card))

        # Sort the cards in decreasing order of points value
        remaining = sorted(remaining_cards_local.keys(), key=lambda x: points_local[x], reverse=True)

        for card in remaining:
            if len(returned_cards) == 13 - round:
                break
            if card not in partner_suit:
                returned_cards.append(idx_to_card(card))
        if player.name == "North" or player.name == "East":
            prev_guesses_1 = returned_cards
        else:
            prev_guesses_2 = returned_cards

        return returned_cards
    else:
        partner_suit = None

        # Get the suit containing partner card
        for suit in fake_suits:
            if partner_card_idx in suit:
                partner_suit = suit
                break

        partner_suit = sorted(partner_suit)

        if turn_number%2 == 0:
            for i, card_idx in enumerate(partner_suit):
                if card_idx > partner_card_idx:
                    points_local[card_idx] = -100
        else:
            for i, card_idx in enumerate(partner_suit):
                if card_idx < partner_card_idx:
                    points_local[card_idx] = -100

        # Return the cards in the fake_suits[partner_suit]
        remove_seen_till_last_round(player.exposed_cards, remaining_cards_local, points_local)
        returned_cards = []
        for i, card in enumerate(partner_suit):
            if card != partner_card_idx and points_local[card] != -100:
                points_local[card] += SUIT_GUESS_POINTS
                returned_cards.append(idx_to_card(card))

        # Sort the cards in decreasing order of points value
        remaining = sorted(remaining_cards_local.keys(), key=lambda x: points_local[x], reverse=True)

        for card in remaining:
            if len(returned_cards) == 13 - round:
                break
            if card not in partner_suit:
                returned_cards.append(idx_to_card(card))
        if player.name == "North" or player.name == "East":
            prev_guesses_1 = returned_cards
        else:
            prev_guesses_2 = returned_cards

        return returned_cards

# def guessing2(player, cards, round):
#     global prev_guesses_2
#     global prev_guesses_1
#     global guesses_and_c_vals_1
#     global guesses_and_c_vals_2
#
#     if player.name == "North" or player.name == "East":
#         remaining_cards_local = remaining_cards_1
#         points_local = points_1
#         prev_guesses_local = prev_guesses_1
#         guesses_and_c_vals_local = guesses_and_c_vals_1
#     else:
#         remaining_cards_local = remaining_cards_2
#         points_local = points_2
#         prev_guesses_local = prev_guesses_2
#         guesses_and_c_vals_local = guesses_and_c_vals_2
#
#     if round == 1:
#         initialize_totals_guessing(cards, remaining_cards_local, points_local, player.name)
#         remove_from_points(player.hand, points_local)
#
#     # print("Remaining cards: ", remaining_cards_local)
#     rem = []
#     for card in remaining_cards_local.keys():
#         if remaining_cards_local[card] != -100:
#             rem.append(card)
#     turn_number = len(player.cVals) + 1
#
#     if turn_number > 1:
#         update_points_with_guesses(
#             prev_guesses_local,
#             points_local,
#             player.cVals[-1] / (13 - round + 1),
#             player.cVals[-1],
#             guesses_and_c_vals_local,
#         )
#     rem = sorted(rem)
#     fake_suits = get_fake_suits(turn_number, rem, 4)
#
#     # print(f"Check prob datastore: {guesses_and_c_vals_local}")
#     # TODO: below is how you can get the weight distribution to use for guessing
#     weight_distribution = get_likelihood_weight_distribution(guesses_and_c_vals_local)
#     # print(f"w_d: {weight_distribution}")
#
#     partner_card = player.exposed_cards[partner(player.name)][-1]
#     partner_card_idx = card_to_idx(partner_card)
#     # Find the suit of the card exposed by the partner
#     if turn_number < LATE_GAME_INDEX:
#         pointer_suit_id = -1
#
#         # Get the suit containing partner card
#         for i, suit in enumerate(fake_suits):
#             if partner_card_idx in suit:
#                 pointer_suit_id = i
#                 break
#
#         partner_suit = fake_suits[pointer_suit_id + 1 if pointer_suit_id != 3 else 0]
#         pointer_suit = fake_suits[pointer_suit_id]
#         partner_suit = sorted(partner_suit)
#
#         if turn_number % 2 == 0:
#             for i, card_idx in enumerate(pointer_suit):
#                 if card_idx > partner_card_idx:
#                     points_local[card_idx] = -100
#         else:
#             for i, card_idx in enumerate(pointer_suit):
#                 if card_idx < partner_card_idx:
#                     points_local[card_idx] = -100
#
#         # Return the cards in the fake_suits[partner_suit]
#         remove_seen_till_last_round(player.exposed_cards, remaining_cards_local, points_local)
#         returned_cards = []
#         for i, card in enumerate(partner_suit):
#             if card != partner_card_idx and points_local[card] != -100:
#                 points_local[card] += SUIT_GUESS_POINTS
#                 returned_cards.append(idx_to_card(card))
#
#         # Sort the cards in decreasing order of points value
#         remaining = sorted(remaining_cards_local.keys(), key=lambda x: points_local[x], reverse=True)
#
#         for card in remaining:
#             if len(returned_cards) == 13 - round:
#                 break
#             if card not in partner_suit:
#                 returned_cards.append(idx_to_card(card))
#         if player.name == "North" or player.name == "East":
#             prev_guesses_1 = returned_cards
#         else:
#             prev_guesses_2 = returned_cards
#
#         return returned_cards
#     else:
#         if turn_number % 2 == 0:
#             for card_idx in range(partner_card_idx, 52):
#                 points_local[card_idx] = -100
#         else:
#             for card_idx in range(0, partner_card_idx+1):
#                 points_local[card_idx] = -100
#
#         # Return the cards in the fake_suits[partner_suit]
#         remove_seen_till_last_round(player.exposed_cards, remaining_cards_local, points_local)
#
#         returned_cards = []
#         # Sort the cards in decreasing order of points value
#         remaining = sorted(weight_distribution.keys(), key=lambda x: weight_distribution[x], reverse=True)
#
#         for card in remaining:
#             if len(returned_cards) == 13 - round:
#                 break
#             returned_cards.append(idx_to_card(card))
#         if player.name == "North" or player.name == "East":
#             prev_guesses_1 = returned_cards
#         else:
#             prev_guesses_2 = returned_cards
#
#         return returned_cards

