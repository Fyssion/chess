class ChessError(Exception):
    pass


class InvalidFEN(ChessError):
    def __init__(self):
        super().__init__('Invalid FEN provided.')


class InvalidMove(ChessError):
    def __init__(self):
        super().__init__('Invalid move provided.')


class DisambiguationError(ChessError):
    def __init__(self, moves):
        pretty = ', '.join(str(move) for move in moves)
        super().__init__(f'Error disambiguating moves: {pretty}.')
        self.moves = moves
