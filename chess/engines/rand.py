import random

import chess
from .base import Engine


class RandomEngine(Engine):
    """A chess engine that chooses a legal move at random.

    Yeah, I know it's dumb.
    """

    def get_move(self, board: chess.Board):
        legal_moves = list(board.legal_moves())
        return random.choice(legal_moves)
