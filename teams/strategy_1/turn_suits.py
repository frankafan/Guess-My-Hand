import random
from typing import List

from teams.strategy_1.orthogonality_seed import NAIVE_BEST_SEED


def get_fake_suits(turn: int, remaining_card_idxs: List[int], num_groups: int = 4) -> List[List[int]]:
    prev_seed = random.seed()
    random.seed(NAIVE_BEST_SEED*turn)
    random.shuffle(remaining_card_idxs)
    random.seed(prev_seed)
    fake_suits = [remaining_card_idxs[i::num_groups] for i in range(num_groups)]
    return fake_suits
