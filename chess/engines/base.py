import chess


class Engine:
    """The base chess engine that all other engines subclass.

    This doesn't include any logic. It is simply a framework for actual engines.
    """

    def evaluate(self, board: chess.Board):
        """Returns the engine's evaluation score for a board."""
        raise NotImplementedError

    def get_move(self, board: chess.Board):
        """Finds and returns the best move on the board."""
        raise NotImplementedError
