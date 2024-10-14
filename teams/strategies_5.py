from collections import defaultdict
import random

ordered_players = ["North", "East", "South", "West"]
avg = [0] * 12
count = 0

# ​​Obtained via simulation - unused rn, could be used later
expectation_constants = {
    "North": [
        5.0279,
        4.6287,
        4.2454,
        3.8219,
        3.4301,
        2.9994,
        2.571,
        2.1446,
        1.6964,
        1.2408,
        0.7697,
        0.2664,
        0.0,
    ],
    "East": [
        5.0938,
        4.6958,
        4.301,
        3.8704,
        3.4803,
        3.0624,
        2.6374,
        2.2074,
        1.7568,
        1.2959,
        0.8189,
        0.3069,
        0.0,
    ],
    "South": [
        5.1595,
        4.757,
        4.3671,
        3.9484,
        3.5233,
        3.115,
        2.7041,
        2.2568,
        1.8143,
        1.3575,
        0.8931,
        0.3492,
        0.0,
    ],
    "West": [
        5.227,
        4.8234,
        4.4193,
        4.0222,
        3.6142,
        3.1991,
        2.7588,
        2.3307,
        1.8908,
        1.4196,
        0.9461,
        0.4402,
        0.0,
    ],
}


samples_received = defaultdict(list)


def get_seed(card, round):
    """
    Generates a seed value based on the card's value and suit.
    """
    return (card**round) + 7


def get_possible_cards(player, stop_at_who):
    """
    Returns a list of all possible cards in the deck.
    """
    possible = [n for n in range(52)]
    length = len(player.exposed_cards["North"])
    length += 1 if player.name == "North" and stop_at_who == "North" else 0
    for i in range(length):
        for p in ordered_players:
            if i == length - 1 and p == stop_at_who:
                break

            possible.remove(card_to_val(player.exposed_cards[p][i]))
    return possible


def get_sample(card, sample_size, player, stop_at_who, round):
    """
    Returns a sample of cards based on the seed derived from the card.
    """
    possible_cards = get_possible_cards(player, stop_at_who)
    possible_cards.remove(card)
    # print(card, len(possible_cards), player.name, stop_at_who)
    seed = get_seed(card, round)
    random.seed(seed)
    return random.sample(possible_cards, sample_size)


def playing(player, deck):
    """
    Selects the card to play based on maximizing the overlap between
    the generated sample and the player's own hand.
    """
    round = len(player.cVals) + 1
    # print(player.name, player.exposed_cards)
    if not player.hand:
        return None

    held_cards = [card_to_val(c) for c in player.hand]
    highest_score = -1
    best_card_index = -1

    sample_size = 13 - len(player.played_cards) - 1
    sample_size = max(sample_size, 0)

    for idx, card in enumerate(held_cards):
        sample = get_sample(card, sample_size, player, player.name, round)
        # print(card, ",", sample)

        score = sum(1 for c in sample if c in held_cards)

        if score > highest_score:
            highest_score = score
            best_card_index = idx
    # print("!!!", highest_score)
    return best_card_index if best_card_index != -1 else 0


def guessing(player, cards, round):
    # print(round, player.cVals)
    global samples_received
    if round == 1:
        samples_received = defaultdict(list)
    # if round == 13:
    #     global count
    #     count += 1
    #     for i in range(len(player.cVals)):
    #         avg[i] = (avg[i] * (count - 1) + player.cVals[i]) / count
    #     print(player.name, avg)

    cp = {val: 1 for val in range(52)}

    for held_card in player.hand:
        del cp[card_to_val(held_card)]

    for exposed_cards_li in player.exposed_cards.values():
        for exposed_card in exposed_cards_li:
            del cp[card_to_val(exposed_card)]

    for played_card in player.played_cards:
        if card_to_val(played_card) in cp:
            del cp[card_to_val(played_card)]

    partner_name = partner(player.name)

    taken_from_samples = []

    partner_exposed_cards = player.exposed_cards[partner_name]

    if not partner_exposed_cards:
        print("Something went wrong")
        return []

    last_partner_card = card_to_val(partner_exposed_cards[-1])

    sample_size = 13 - len(partner_exposed_cards)
    sample_size = max(sample_size, 0)

    sample = get_sample(last_partner_card, sample_size, player, partner_name, round)
    # print("---", player.name, sample)
    samples_received[player.name].append(sample)

    update_probabilities_with_guesses(player, cp, round, player.cVals, player.guesses)

    sampled_count = defaultdict(int)
    for i in range(len(samples_received[player.name])):
        s = samples_received[player.name][i]
        for c in s:
            if c in cp:
                sampled_count[c] += 1

    taken_from_samples = sorted(
        sampled_count.keys(), key=lambda c: sampled_count[c], reverse=True
    )[: min(13 - round, len(sampled_count))]
    # print(player.name, taken_from_samples, sampled_count)

    selected_vals = sorted(
        [k for k in cp.keys() if k not in taken_from_samples],
        key=lambda val: cp[val],
        reverse=True,
    )[: 13 - round - len(taken_from_samples)]
    selected_vals += taken_from_samples
    selected = []
    for card in cards:
        if card_to_val(card) in selected_vals:
            selected.append(card)
    # print(selected_vals, len(cp))
    # for k in cp:
    #     print(k, ":", cp[k])
    # print("\n\n")
    return selected


def update_probabilities_with_guesses(player, cp, round, cVals, guesses):
    """
    Update probabilities using previous guesses and correct guesses count (cVals).
    """
    partner_cards = {
        card_to_val(card) for card in player.exposed_cards[partner(player.name)]
    }

    prev_possible_cards = 0
    while len(cp) != prev_possible_cards:
        prev_possible_cards = len(cp)

        for past_round, guess_set in enumerate(guesses):
            guess_set = [card_to_val(card) for card in guess_set]
            numerator = cVals[past_round]
            denominator = len(guess_set)

            for card_val in guess_set:
                if card_val in partner_cards:
                    numerator -= 1

                elif card_val not in cp:
                    denominator -= 1

            if denominator > 0:
                remaining_prob = numerator / denominator
                # print("Guessed", guess_set, remaining_prob, numerator)
                for card_val in guess_set:
                    if card_val in cp:
                        if numerator <= 0:
                            del cp[card_val]
                        else:
                            cp[card_val] *= remaining_prob

            unguessed_cards = set()
            for card_val in cp:
                if card_val not in guess_set:
                    unguessed_cards.add(card_val)

            # print(len(unguessed_cards), len(guess_set), len(cp))

            if len(unguessed_cards) > 0:
                missed_guesses = len(guess_set) - cVals[past_round]
                remaining_prob = min(missed_guesses / len(unguessed_cards), 1)
                # print("Unguessed", unguessed_cards, remaining_prob, missed_guesses)
                # print(missed_guesses, len(unguessed_cards))
                for card_val in unguessed_cards:
                    if missed_guesses <= 0:
                        del cp[card_val]
                    else:
                        cp[card_val] *= remaining_prob


def partner(name):
    if name == "North":
        return "South"
    if name == "South":
        return "North"
    if name == "East":
        return "West"
    if name == "West":
        return "East"
    raise Exception("Invalid name")


def card_to_val(card):
    return (rank_to_val[card.value] * 4) + suit_to_val[card.suit]


rank_to_val = {
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
suit_to_val = {"Hearts": 0, "Diamonds": 1, "Clubs": 2, "Spades": 3}
ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
suits = ["Hearts", "Diamonds", "Clubs", "Spades"]
