import random
from itertools import chain
from collections import defaultdict
import numpy as np
from CardGame import Card, Player, Deck

PLAYERS = {"North", "South", "East", "West"}

PARTNERS = {
    "North": "South",
    "East": "West",
    "South": "North",
    "West": "East",
}

OPPONENTS = {
    "North": ["East", "West"],
    "South": ["East", "West"],
    "East": ["North", "South"],
    "West": ["North", "South"],
}

SUIT_TO_NUM = {"Hearts": 0, "Spades": 13, "Diamonds": 26, "Clubs": 39}

VAL_TO_NUM = {
    "A": 1,
    "2": 2,
    "3": 3,
    "4": 4,
    "5": 5,
    "6": 6,
    "7": 7,
    "8": 8,
    "9": 9,
    "10": 10,
    "J": 11,
    "Q": 12,
    "K": 13,
}

NUM_TO_SUIT = {v: k for k, v in SUIT_TO_NUM.items()}
NUM_TO_VAL = {v: k for k, v in VAL_TO_NUM.items()}

MIN_SUIT = {player: -1 for player in PLAYERS}

DECK = [Card(suit, value) for suit in SUIT_TO_NUM.keys() for value in VAL_TO_NUM.keys()]
SWITCH_STRATEGIES = 1
PERMUTATIONS_SEEN = { "North": [],
    "South": [],
    "East": [],
    "West": [],
}


def generate_permutation(perm_size, seedcard, player, unguessed_cards):
    """Generates a permutation dictionary, each card points to one permutation"""
    unguessed = unguessed_cards.copy()
    if seedcard in unguessed:
        unguessed.remove(seedcard)
    unguessed = sorted(unguessed, key=lambda k: VAL_TO_NUM[k.value] + SUIT_TO_NUM[k.suit])

    # Generate a seed based on the card's suit and value
    seed = SUIT_TO_NUM[seedcard.suit] + VAL_TO_NUM[seedcard.value]
    
    # Use NumPy's random generator with the seed
    # rng = np.random.default_rng(seed)
    
    # Generate the permutation sample
    random.seed(seed)
    # sample1 = np.random.choice(unguessed, perm_size, replace=False)
    # np.random.seed(seed)
    # sample2 = np.random.choice(unguessed, perm_size, replace=False)
    
    # print("Seed", seed)
    sample = random.sample(unguessed, perm_size)
    # print("Card", seedcard, "Perm size", perm_size, "Sample", sample)
    
    return sample



def get_unguessed_cards(player, play = False):
    """Get all cards that have not been guessed by the player."""
    stop = player.name if play else PARTNERS[player.name]
    length = len(player.exposed_cards["North"]) + int(player.name == "North" and stop == "North")

    exposed_cards = set()
    for i in range(length):
        for pl in player.exposed_cards:
            if i == length - 1 and pl == stop:
                break
            exposed_cards.add(player.exposed_cards[pl][i])

    return [card for card in DECK if card not in exposed_cards]


def get_suit_frequencies(hand):
    """Get the count of cards in each suit."""
    freq = defaultdict(int)
    for card in hand:
        freq[card.suit] += 1
    return freq


def update_c_vals_and_guesses(player):
    """Update cvals based on correct and incorrect guesses from exposed cards."""
    cvals = player.cVals.copy()
    guesses = player.guesses.copy()

    for i, guess in enumerate(guesses):
        guessed = [g for g in guess if g in player.exposed_cards[PARTNERS[player.name]]]
        wrongly_guessed = [
            g
            for g in guess
            if g
            in chain.from_iterable(
                player.exposed_cards[op] for op in OPPONENTS[player.name]
            )
        ]

        cvals[i] -= len(guessed)
        guesses[i] = [g for g in guess if g not in guessed and g not in wrongly_guessed]
    return cvals, guesses


def get_remaining_cards(player, all_cards):
    """Returns a list of cards not exposed, played, or in hand."""
    exposed_set = (
        set(chain.from_iterable(player.exposed_cards.values()))
        | set(player.hand)
        | set(player.played_cards)
    )
    remaining_cards = [card for card in all_cards if card not in exposed_set]

    #print(f"Remaining cards for player {player.name}: {remaining_cards}")
    return remaining_cards


def group_cards_by_suit(cards):
    """Group cards by suit."""
    suit_groups = defaultdict(list)
    for card in cards:
        suit_groups[card.suit].append(card)
    return suit_groups


def round_1_strategy(player, remaining_cards):
    """Eliminate the cards of min suit and return 4 cards from other suits."""
    suit = player.exposed_cards[PARTNERS[player.name]][-1].suit
    MIN_SUIT[player.name] = suit

    remaining_cards = [card for card in remaining_cards if card.suit != suit]
    suit_groups = group_cards_by_suit(remaining_cards)
    random.seed(7)
    selected_cards = [
        card
        for _, cards in suit_groups.items()
        for card in random.sample(cards, min(4, len(cards)))
    ]
    return selected_cards[:12]


def update_probabilities_from_c_vals(player, probabilities, game_round):
    """Update probabilities of remaining cards based on c values and guess history."""
    cvals, guesses = update_c_vals_and_guesses(player)
    prob = probabilities.copy()
    flag = False
    for i, guess in enumerate(guesses):
        c = cvals[i]

        # Remove cards whose c_val was 0
        prob = {
            card: value
            for card, value in prob.items()
            if card not in guess or player.cVals[i] != 0
        }

        # if game_round >= 3 and flag == False:
        #     flag = True
        #     prev_guess = guesses[-2]
        #     prev_cval = cvals[-2]
        #     pres_guess = guesses[-1]
        #     pres_cval = cvals[-1]
        #     print("/nPlayer: ", player.name)
        #     print()
        #     print(pres_cval, prev_cval)
        #     better_cards = []
        #     worse_cards = []
        #     best_cards = []
        #     if pres_cval > prev_cval:
        #         print("Guesses:")
        #         print(pres_guess, prev_guess)
        #         better_cards = [card for card in set(pres_guess) - set(prev_guess)]
        #         print(f"\nPlayer: {player.name}")
        #         print("Here", better_cards)
        #     elif pres_cval < prev_cval:
        #         print(pres_cval, prev_cval)
        #         worse_cards = [card for card in set(prev_guess) - set(pres_guess)]
        #         print(f"\nPlayer: {player.name}")
        #         print("There", worse_cards)
        #     else:
        #         best_cards = [
        #             card for card in set(pres_guess).intersection(set(prev_guess))
        #         ]
        #         print("Else", better_cards)
        #     for card in prob:
        #         if card in better_cards:
        #             prob[card] *= 1.1
        #         elif card in best_cards:
        #             prob[card] *= 1.1
        #         elif card in worse_cards:
        #             prob[card] *= 0.9

        for card in prob:
            if card in guess:
                if c == len(guess):  # All cards are right
                    prob[card] = 100
                elif c > (len(guess) // 2) + 1:  # More than half are right
                    prob[card] *= (c / len(guess))
                elif c == 0:
                    prob[card] = 0
                else:  # Boost by c/len(guess)
                    prob[card] *= c / len(guess)
            else:  # Boost unguessed cards
                if len(guess) - c:
                    prob[card] *= (len(guess) - c) / len(guess)

    return prob


def update_probabilities_for_min_max(prob, last_exposed, game_round):
    """Remove cards < min and > max alternating on game rounds."""
    threshold = VAL_TO_NUM[last_exposed.value]
    return {
        card: value
        for card, value in prob.items()
        if not (
            (game_round % 2 != 0 and VAL_TO_NUM[card.value] > threshold)
            or (game_round % 2 == 0 and VAL_TO_NUM[card.value] < threshold)
        )
    }


def playing(player: Player, deck: Deck):
    """If game_round =1: Play min suit
    game_round <=10: Alternate between min and max cards
    game_round >10: Play most similar card from permutaion
    """
    global PERMUTATIONS_SEEN
    game_round = len(player.played_cards) + 1
    # print("SEED", deck.seed)
    player.hand=sorted(player.hand, key=lambda k: VAL_TO_NUM[k.value] + SUIT_TO_NUM[k.suit])

    if game_round == 1:
        PERMUTATIONS_SEEN = []
        # print("PLAYER", player.name,PERMUTATIONS_SEEN, deck.seed, player.hand)
        freq = get_suit_frequencies(player.hand)
        min_suit = min(freq, key=freq.get)
        max_card_in_min_suit = max(
            [card for card in player.hand if card.suit == min_suit],
            key=lambda card: VAL_TO_NUM[card.value],
        )
        return player.hand.index(max_card_in_min_suit)

    if game_round > SWITCH_STRATEGIES :
        return (
            player.hand.index(min(player.hand, key=lambda card: VAL_TO_NUM[card.value]))
            if game_round % 2 == 0
            else player.hand.index(
                max(player.hand, key=lambda card: VAL_TO_NUM[card.value])
            )
        )
    
    card_index_min = 0
    min_sim = len(player.hand)
    max_sim = 0
    card_index_max = 0
    card1 = -1
    permm1 = []
    card2 =-1
    permm2 = []
    unguessed_cards = get_unguessed_cards(player, True)
    for i, k in enumerate(player.hand):
        perm = generate_permutation(13 - game_round, k, player, unguessed_cards)
        sim = len((set(player.hand) & set(perm)) - {k})
        if sim < min_sim:
            card_index_min = i
            min_sim = sim
            card1 = k
            permm1 = perm
        elif sim > max_sim:
            card_index_max = i
            max_sim = sim
            card2 = k
            permm2 = perm
    #print("Card", card, "PERM", permmm, "PERM FROM RANDOM", generate_permutation(13-game_round, card, player, unguessed_cards))
    #print("Max similarity", max_sim)
    #print("Min similarity", min_sim)
    print("Playing:")
    if game_round %2 == 0:
        print(card1, permm1)
        return card_index_min
    else:
        print(card2, permm2)
        return card_index_max



def guessing(player: Player, cards, game_round):
    """Returns a set of cards guessed at each game round."""
    #print(f"\nPlayer: {player.name}")

    remaining_cards = get_remaining_cards(player, cards)
    if not remaining_cards:
        #print(f"0 cards remaining at game round {game_round}")
        return random.sample(cards, 13 - game_round)

    if game_round == 1:
        return round_1_strategy(player, remaining_cards)

    # Adjust probabilities of min suit
    prob = {
        card: (1 / len(remaining_cards))
        * (0.001 if card.suit == MIN_SUIT[player.name] else 1)
        for card in remaining_cards
    }
    prob = update_probabilities_from_c_vals(player, prob, game_round)

    if game_round > SWITCH_STRATEGIES:
        prob = update_probabilities_for_min_max(
            prob, player.exposed_cards[PARTNERS[player.name]][-1], game_round
        )
    else:
        #print("Last exposed", player.exposed_cards[PARTNERS[player.name]][-1])
        unguessed_cards = get_unguessed_cards(player)
        most_sim_p = generate_permutation(13-game_round, player.exposed_cards[PARTNERS[player.name]][-1], player, unguessed_cards)
        PERMUTATIONS_SEEN[player.name].append(most_sim_p)
        #print("Most Similar/Disimilar Permutation", most_sim_p)

    for i,permutation in enumerate(PERMUTATIONS_SEEN[player.name]):
        #print(i,permutation)
        for val in permutation:
            #print(val)
            if val in prob:
                if i%2 == 0:
                    prob[val] *= 0.9  # Reduce
                    #print("Reducing prob of ", val, "to ", prob[val])
                else:
                    prob[val] *=1.1 #Increase
                    #print("Increasing prob of ", val, "to ", prob[val])

    normalized_weights = np.array(list(prob.values()))
    sorted_indices = np.argsort(normalized_weights)[::-1]
    top_indices = sorted_indices[:13 - game_round]
    sampled_cards = [list(prob.keys())[i] for i in top_indices]
    return sampled_cards
