from .square import Square


class Move:
    __slots__ = ('from_square', 'to_square')

    from_square: Square
    to_square: Square

    def __init__(self, from_square: Square, to_square: Square):
        self.from_square = from_square
        self.to_square = to_square

    def __repr__(self) -> str:
        return f'<Move from="{self.from_square}" to={self.to_square}">'
