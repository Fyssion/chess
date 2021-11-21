from typing import Optional

from .castle_state import CastleState
from .piece import Piece, PieceColor
from .square import Square


class CastleType:
    KINGSIDE = 0
    QUEENSIDE = 1


class Move:
    """A move being made on the board."""

    __slots__ = ('from_square', 'to_square', 'capture', 'castle', 'castle_state')

    from_square: Square
    to_square: Square
    capture: Optional[Piece]
    castle: Optional[int]
    castle_state: CastleState

    def __init__(self, from_square: Square, to_square: Square, castle_state: CastleState, capture: Piece = None, castle: int = None):
        self.from_square = from_square
        self.to_square = to_square
        self.capture = capture
        self.castle = castle
        self.castle_state = castle_state

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

    def __init__(self, castle: int, castle_state: CastleState):
        self.from_square = None
        self.to_square = None
        self.capture = None
        self.castle = castle
        self.castle_state = castle_state

    # the code below this line is an abysmal mess.
    # I apologize

    def king_from_square(self, color: int):
        """Returns the Square that the king moves from."""

        if color == PieceColor.WHITE:
            return Square(0, 4)
        else:
            return Square(7, 4)

    def rook_from_square(self, color: int):
        """Returns the Square that the rook moves from."""

        if self.castle == CastleType.KINGSIDE:
            if color == PieceColor.WHITE:
                return Square(0, 7)
            else:
                return Square(7, 7)
        else:
            if color == PieceColor.WHITE:
                return Square(0, 0)
            else:
                return Square(7, 0)

    def king_to_square(self, color: int):
        """Returns the Square that the king moves to."""

        if self.castle == CastleType.KINGSIDE:
            if color == PieceColor.WHITE:
                return Square(0, 6)
            else:
                return Square(7, 6)
        else:
            if color == PieceColor.WHITE:
                return Square(0, 2)
            else:
                return Square(7, 2)

    def rook_to_square(self, color: int):
        """Returns the Square that the rook moves to."""

        if self.castle == CastleType.KINGSIDE:
            if color == PieceColor.WHITE:
                return Square(0, 5)
            else:
                return Square(7, 5)
        else:
            if color == PieceColor.WHITE:
                return Square(0, 3)
            else:
                return Square(7, 3)
