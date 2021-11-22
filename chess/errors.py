class ChessError(Exception):
    """Base chess error that all errors subclass."""


class InvalidFEN(ChessError):
    """Raised when an inputted FEN string is invalid."""

    def __init__(self):
        super().__init__('Invalid FEN provided.')


class InvalidMove(ChessError):
    """Raised when an inputted move is invalid."""

    def __init__(self):
        super().__init__('Invalid move provided.')


class DisambiguationError(ChessError):
    """Raised when the SAN parser cannot disambiguate between multiple moves."""

    def __init__(self, moves):
        pretty = ', '.join(str(move) for move in moves)
        super().__init__(f'Error disambiguating moves: {pretty}.')
        self.moves = moves


class PromotionError(ChessError):
    """Special DisambiguationError for missing promotion."""

    def __init__(self):
        super().__init__('Please provide a promotion piece.')
