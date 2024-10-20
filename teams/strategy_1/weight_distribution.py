from typing import Any, Dict, List
import numpy as np
from collections import defaultdict

from teams.strategy_1.util import card_to_idx, idx_to_card


TOTAL_CARDS = 52


def get_likelihood_weight_distribution(turn_dataset: List[Dict[str, Any]]) -> Dict[int, float]:
    """
    Calculate the likelihood weight distribution of each card based on all past turn data containing previous guesses and c-values.
    :param turn_dataset: List of dictionaries containing previous guesses and c-values.
    :return: Dictionary containing the likelihood weight distribution of each card.
    """
    weight = defaultdict(float)

    for turn_data in turn_dataset:
        guesses = turn_data['guesses']
        correct = turn_data['c_val']
        n = len(guesses)
        
        guessed_cards = set(map(card_to_idx, guesses))
        for card_idx in range(TOTAL_CARDS):
            if card_idx in guessed_cards:
                weight[card_idx] += correct / n
            else:
                weight[card_idx] += (len(guesses) - correct) / (TOTAL_CARDS - n)

    if not weight:
        return weight
    
    min_weight = min(weight.values())
    for card_idx in weight:
        weight[card_idx] -= min_weight

    # TODO: remove below print/debug for-loop
    sorted_distribution = sorted(weight.items(), key=lambda x: x[1], reverse=True)
    probability_table = "[DEBUG] Card Number \t| Probability\n" + "-" * 30 + "\n"
    for card, prob in sorted_distribution:
        probability_table += f"{idx_to_card(card)} \t| {prob:.4f}\n"
    # print(probability_table)

    return weight