import chess


class Engine:
    """The base chess engine that all other engines subclass.

    This doesn't include any logic. It is simply a framework for actual engines.
    """

    def __init__(self):
        self.setup()

    def setup(self):
        """Performs engine setup functions.

        This is called when an instance is created.
        """
        pass

    def get_move(self, board: chess.Board):
        """Finds and returns the best move on the board."""
        raise NotImplementedError

    def evaluate(self, board: chess.Board):
        """Returns the engine's evaluation score for a board."""
        raise NotImplementedError
