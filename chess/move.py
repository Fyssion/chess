from typing import Optional

from .piece import Piece
from .square import Square


class CastleType:
    KINGSIDE = 0
    QUEENSIDE = 1


class Move:
    __slots__ = ('from_square', 'to_square', 'capture', 'castle')

    from_square: Square
    to_square: Square
    capture: Optional[Piece]
    castle: Optional[int]

    def __init__(self, from_square: Square, to_square: Square, capture: Piece = None, castle: int = None):
        self.from_square = from_square
        self.to_square = to_square
        self.capture = capture
        self.castle = castle

    def __eq__(self, other) -> bool:
        return (
            isinstance(other, self.__class__)
            and self.from_square == other.from_square
            and self.to_square == other.to_square
            and self.capture == other.capture
            and self.castle == other.castle
        )

    def __repr__(self) -> str:
        return f'<Move lan="{self.lan}">'

    @property
    def castle_notation(self) -> str:
        if self.castle is None:
            raise ValueError('This move is not a castle.')

        if self.castle == CastleType.QUEENSIDE:
            return 'O-O-O'
        else:
            return 'O-O'

    @property
    def lan(self) -> str:
        if self.castle is not None:
            return self.castle_notation

        return f'{self.from_square.san}-{self.to_square.san}'

    @property
    def uci(self) -> str:
        if self.castle is not None:
            return self.castle_notation

        return f'{self.from_square.san}{self.to_square.san}'


class CastleMove(Move):
    from_square: Optional[Square]
    to_square: Optional[Square]

    def __init__(self, castle: int):
        self.from_square = None
        self.to_square = None
        self.capture = None
        self.castle = castle
