from platform import version
from typing import Optional

from . import errors
from .move import Move, CastleMove, CastleType
from .piece import PieceColor, Piece, PIECES, PieceType
from .square import Square


class CastleState:
    def __init__(self, id: int = 0):
        self.id = id

    def __repr__(self) -> str:
        return f'<CastleState fen="{self.fen}">'

    @classmethod
    def from_fen(cls, fen: str):
        castle_state = 0

        if fen != '-':
            for char in fen:
                if char == 'K':
                    castle_state |= 0b1000
                elif char == 'Q':
                    castle_state |= 0b0100
                elif char == 'k':
                    castle_state |= 0b0010
                elif char == 'q':
                    castle_state |= 0b0001

        return cls(castle_state)

    @property
    def fen(self) -> str:
        fen = ''

        if self.id:
            if self.id & 0b1000:
                fen += 'K'
            if self.id & 0b0100:
                fen += 'Q'
            if self.id & 0b0010:
                fen += 'k'
            if self.id & 0b0001:
                fen += 'q'
        else:
            fen += '-'

        return fen


class Board:
    __slots__ = (
        'rows',
        'active_color',
        'castle_state',
        'en_passant_state',
        'fullmoves',
        'halfmoves',
        'move_history'
    )

    DEFAULT_FEN = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'

    rows: list[list[Optional[Piece]]]
    active_color: int
    castle_state: CastleState
    en_passant_state: Optional[Square]
    fullmoves: int
    halfmoves: int
    move_history: list[Move]

    def __init__(self):
        # 8x8 board filled with nothing
        self.rows = [
            [None for i in range(8)]  # 8 columns
            for i in range(8)         # 8 rows
        ]

        self.active_color = PieceColor.WHITE
        self.castle_state = CastleState()
        self.en_passant_state = None
        self.fullmoves = 1
        self.halfmoves = 0
        self.move_history = []

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
        self.castle_state = CastleState.from_fen(castle_state)

        # en passant state
        if en_passant_state != '-':
            self.en_passant_state = Square.from_san(en_passant_state)

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
        result += self.castle_state.fen

        result += ' '

        # en passant state
        if self.en_passant_state:
            result += self.en_passant_state.san
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

    def is_in_check(self, color: int = None) -> bool:
        if color is None:
            color = self.active_color

        for i, row in enumerate(self.rows):
            for j, piece in enumerate(row):
                if piece is None:
                    continue
                if piece.color == color:
                    continue

                square = Square(i, j)
                for move in piece.moves(self, square):
                    capture = self.get(move)

                    if capture and capture.type == PieceType.KING:
                        return True

        return False

    def is_checkmate(self) -> bool:
        if self.is_in_check() and not list(self.legal_moves()):
            return True

        return False

    def is_stalemate(self) -> bool:
        if self.halfmoves >= 100:
            return True

        if not self.is_in_check and not list(self.legal_moves()):
            return True

        return False

    def pseudo_legal_moves(self):
        for i, row in enumerate(self.rows):
            for j, piece in enumerate(row):
                if not piece:
                    continue
                if piece.color != self.active_color:
                    continue

                square = Square(i, j)
                for move in piece.moves(self, square):
                    capture = self.get(move)
                    yield Move(square, move, capture=capture)

    def legal_moves(self):
        is_in_check = self.is_in_check()
        active_color = self.active_color

        for move in self.pseudo_legal_moves():
            if not is_in_check:
                yield move
                continue

            valid: Optional[bool] = False

            # make the move, see if still in check, unmake the move
            self.make_move(move)
            if not self.is_in_check(active_color):
                valid = True
            self.unmake_move(move)

            if valid:
                yield move

    def make_move(self, move: Move):
        piece = self.rows[move.from_square.row][move.from_square.column]
        self.rows[move.from_square.row][move.from_square.column] = None
        self.rows[move.to_square.row][move.to_square.column] = piece

        self.move_history.append(move)

        if self.active_color is PieceColor.BLACK:
            self.fullmoves += 1

        self.active_color = PieceColor.BLACK if self.active_color else PieceColor.WHITE

    def unmake_move(self, move: Move):
        piece = self.rows[move.to_square.row][move.to_square.column]
        self.rows[move.to_square.row][move.to_square.column] = move.capture
        self.rows[move.from_square.row][move.from_square.column] = piece

        if self.move_history[-1] == move:
            self.move_history.pop(-1)

        if self.active_color is PieceColor.WHITE:
            self.fullmoves -= 1

        self.active_color = PieceColor.BLACK if self.active_color else PieceColor.WHITE

    def parse_san(self, san: str) -> Move:
        piece: Optional[Piece] = None
        from_row: Optional[int] = None
        from_column: Optional[int] = None
        to_square: Optional[Square] = None

        if san in ('0-0', 'O-O'):
            return CastleMove(CastleType.KINGSIDE)

        if san in ('0-0-0', 'O-O-O'):
            return CastleMove(CastleType.QUEENSIDE)

        for i, char in enumerate(san):
            # see if a piece if specified
            possible_fens = [Piece.FEN.upper() for Piece in PIECES]

            if char in possible_fens:
                piece = Piece.from_fen(char, color=self.active_color)
                continue

            if char in Square.FILES:
                # we are either at the final square's file or the first square's file
                if 1 <= len(char) - i + 1 <= 2:
                    # we are at the final square's file
                    to_square = Square(int(san[i + 1]) - 1, Square.FILES.index(char))
                    break
                else:
                    # we are at the first square's file
                    # the next char could be a rank
                    from_column = Square.FILES.index(char)
                    try:
                        from_row = int(san[i + 1]) - 1
                    except ValueError:
                        # no rank specified
                        continue

            try:
                from_row = int(char) - 1
            except ValueError:
                # not a rank
                pass

            if char == 'x':
                # piece takes a piece, which we can ignore
                continue

        legal_moves = list(self.legal_moves())
        possible_moves: list[Move] = []

        for legal_move in legal_moves:
            if (
                to_square == legal_move.to_square
                and (not piece or piece == self.get(legal_move.from_square))
                and (from_column is None or from_column == legal_move.from_square.column)
                and (from_row is None or from_row == legal_move.from_square.row)
            ):
                possible_moves.append(legal_move)

        if not possible_moves:
            raise errors.InvalidMove()

        if len(possible_moves) > 1:
            raise errors.DisambiguationError(possible_moves)

        return possible_moves[0]

    def push_san(self, san: str):
        move = self.parse_san(san)
        self.make_move(move)
        return move

    def __repr__(self) -> str:
        return f'<Board fen={self.fen}>'
