class ChessError(Exception):
    pass


class InvalidFEN(ChessError):
    def __init__(self):
        super().__init__('Invalid FEN provided.')
