from . import errors
from .square import Square


class PieceColor:
    BLACK = 0b0000
    WHITE = 0b1000


class PieceType:
    PAWN = 0b001
    ROOK = 0b010
    KNIGHT = 0b011
    BISHOP = 0b100
    QUEEN = 0b101
    KING = 0b110


# for pieces, the first bit signifies color,
# and the last 3 signify type.
#
# | color (black)
# 10011
#  |--| piece (knight)


class Piece:
    """A piece on the board."""

    __slots__ = ('id')

    TYPE: int
    FEN: str

    def __init__(self, id: int = None, *, color: int = None, type: int = None):
        self.id = id or color | (self.TYPE or type)  # type: ignore

        if self.TYPE and self.type != self.TYPE:
            raise errors.ChessError('Invalid type provided.')

    def __eq__(self, other) -> bool:
        return isinstance(other, Piece) and self.id == other.id

    def __int__(self):
        return self.id

    def __repr__(self) -> str:
        color = 'White' if self.color == PieceColor.WHITE else 'Black'
        return f'<Piece fen="{self.fen}" color="{color}">'

    @classmethod
    def from_fen(cls, fen: str, color: int = None):
        if color is None:
            color = PieceColor.WHITE if fen.isupper() else PieceColor.BLACK

        for Piece in PIECES:
            if Piece.FEN == fen.lower():
                return Piece(color=color)
        raise errors.InvalidFEN()

    @property
    def color(self) -> int:
        """Returns the color of the piece."""

        return self.id & 0b1000

    @property
    def type(self) -> int:
        """Returns the type of the piece."""

        mask = (1 << 3) - 1
        return (self.id & mask)

    @property
    def fen(self) -> str:
        """Returns the piece's FEN string."""

        if self.FEN:
            return self.FEN

        for Piece in PIECES:
            if Piece.TYPE == self.type:
                return Piece.FEN

        raise RuntimeError('Invalid PieceType.')

    def moves(self, board, square):
        """Returns a generator of the piece's possible moves."""

        raise NotImplementedError


def search_along_direction(board, square, direction, *, max_iterations=0, can_capture=True):
    """Returns a generator of the ray of moves along a direction."""

    piece = board.get(square)
    negative = -1 if piece.color is PieceColor.BLACK else 1
    current_square = square
    iterations = 0

    while current_square.is_valid():
        if max_iterations and iterations >= max_iterations:
            break

        if current_square is square:
            row = current_square.row + (direction[1] * negative)
            column = current_square.column + (direction[0] * negative)
            current_square = Square(row, column)
            continue

        current_piece = board.get(current_square)

        if current_piece:
            # stop if a piece is hit
            if piece.color == current_piece.color or not can_capture:
                break
            else:
                yield current_square
                break

        yield current_square

        iterations += 1

        row = current_square.row + (direction[1] * negative)
        column = current_square.column + (direction[0] * negative)
        current_square = Square(row, column)


class Pawn(Piece):
    TYPE = PieceType.PAWN
    FEN = 'p'

    def is_first_move(self, square, color):
        if color is PieceColor.WHITE and square.row == 1:
            return True
        if color is PieceColor.BLACK and square.row == 6:
            return True
        return False

    def moves(self, board, square):
        piece = board.get(square)
        max_iterations = 2 if self.is_first_move(square, piece.color) else 1

        for move in search_along_direction(board, square, direction=(0, 1), max_iterations=max_iterations, can_capture=False):
            yield move

        # also check diagonal squares
        up_or_down = 1 if piece.color is PieceColor.WHITE else -1
        squares_to_check = (
            Square(square.row + up_or_down, square.column + 1),
            Square(square.row + up_or_down, square.column - 1)
        )

        for square_to_check in squares_to_check:
            if not square_to_check.is_valid():
                continue

            piece_to_check = board.get(square_to_check)
            if piece_to_check:
                if piece.color != piece_to_check.color:
                    yield square_to_check

            # also check for en passant
            if board.en_passant_square == square_to_check:
                yield square_to_check


class Rook(Piece):
    TYPE = PieceType.ROOK
    FEN = 'r'

    def moves(self, board, square):
        # go through each direction and stop when a piece is hit

        # up, down, right, left
        for direction in ((0, 1), (0, -1), (1, 0), (-1, 0)):
            for move in search_along_direction(board, square, direction):
                yield move


class Knight(Piece):
    TYPE = PieceType.KNIGHT
    FEN = 'n'

    def moves(self, board, square):
        for direction in ((2, -1), (2, 1), (-1, 2), (1, 2), (-2, -1), (-2, 1), (-1, -2), (1, -2)):
            for move in search_along_direction(board, square, direction, max_iterations=1):
                yield move


class Bishop(Piece):
    TYPE = PieceType.BISHOP
    FEN = 'b'

    def moves(self, board, square):
        for direction in ((1, 1), (1, -1), (-1, 1), (-1, -1)):
            for move in search_along_direction(board, square, direction):
                yield move


class Queen(Piece):
    TYPE = PieceType.QUEEN
    FEN = 'q'

    def moves(self, board, square):
        for direction in ((0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)):
            for move in search_along_direction(board, square, direction):
                yield move


class King(Piece):
    TYPE = PieceType.KING
    FEN = 'k'

    def moves(self, board, square):
        for direction in ((0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)):
            for move in search_along_direction(board, square, direction, max_iterations=1):
                yield move


PIECES = (Pawn, Knight, Bishop, Rook, Queen, King)
