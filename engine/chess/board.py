from typing import Optional

from . import errors
from .piece import PieceColor, Piece
from .square import Square


class Board:
    __slots__ = (
        'rows',
        'active_color',
        'castle_state',
        'en_passant_state',
        'fullmoves',
        'halfmoves',
    )

    DEFAULT_FEN = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'

    rows: list[list[Optional[Piece]]]
    active_color: int
    castle_state: int
    en_passant_state: Optional[Square]
    fullmoves: int
    halfmoves: int

    def __init__(self):
        # 8x8 board filled with nothing
        self.rows = [
            [None for i in range(8)]  # 8 columns
            for i in range(8)         # 8 rows
        ]

        self.active_color = PieceColor.WHITE
        self.castle_state = 0
        self.en_passant_state = None
        self.fullmoves = 1
        self.halfmoves = 0

    @classmethod
    def default(cls):
        return cls.from_fen(cls.DEFAULT_FEN)

    @classmethod
    def from_fen(cls, fen: str):
        self = cls()

        (
            piece_placement,
            active_color,
            castle_state,
            en_passant_state,
            halfmoves,
            fullmoves
        ) = fen.split()

        # parse piece placement

        row = 8
        column = 1

        for char in piece_placement:
            if char == '/':
                row -= 1
                column = 1
                continue

            try:
                inc = int(char)
            except ValueError:
                pass
            else:
                column += inc
                continue

            color = PieceColor.WHITE if char.isupper() else PieceColor.BLACK
            piece = Piece.from_fen(char.lower(), color)
            self.rows[row - 1][column - 1] = piece
            column += 1

        # set active color

        if active_color == 'w':
            self.active_color = PieceColor.WHITE
        elif active_color == 'b':
            self.active_color = PieceColor.BLACK
        else:
            raise Exception('Invalid FEN provided.')

        # castle state
        if castle_state != '-':
            for char in castle_state:
                if char == 'K':
                    self.castle_state |= 0b1000
                elif char == 'Q':
                    self.castle_state |= 0b0100
                elif char == 'k':
                    self.castle_state |= 0b0010
                elif char == 'q':
                    self.castle_state |= 0b0001

        # en passant state
        if en_passant_state != '-':
            self.en_passant_state = Square.from_notation(en_passant_state)

        # set halfmoves and fullmoves
        try:
            halfmoves = int(halfmoves)
        except ValueError:
            raise errors.InvalidFEN()
        else:
            self.halfmoves = halfmoves

        try:
            fullmoves = int(fullmoves)
        except ValueError:
            raise errors.InvalidFEN()
        else:
            self.fullmoves = fullmoves

        return self

    @property
    def fen(self) -> str:
        result = ''

        # piece placement
        for i, row in enumerate(reversed(self.rows)):
            gap = 0
            for piece in row:
                if not piece:
                    gap += 1
                    continue

                if gap:
                    result += str(gap)
                    gap = 0
                char = piece.FEN
                if piece.color == PieceColor.WHITE:
                    char = char.upper()
                result += char

            if gap:
                result += str(gap)
            if i + 1 != len(self.rows):
                result += '/'

        result += ' '

        # active color
        result += 'w' if self.active_color == PieceColor.WHITE else 'b'

        result += ' '

        # castle state
        if self.castle_state:
            if self.castle_state & 0b1000:
                result += 'K'
            if self.castle_state & 0b0100:
                result += 'Q'
            if self.castle_state & 0b0010:
                result += 'k'
            if self.castle_state & 0b0001:
                result += 'q'
        else:
            result += '-'

        result += ' '

        # en passant state
        if self.en_passant_state:
            result += self.en_passant_state.notation
        else:
            result += '-'

        result += ' '

        # halfmoves and fullmoves
        result += str(self.halfmoves)
        result += ' '
        result += str(self.fullmoves)

        return result

    def get(self, square: Square):
        return self.rows[square.row][square.column]

    def __repr__(self) -> str:
        return f'<Board fen={self.fen}>'
