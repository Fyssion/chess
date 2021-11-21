from typing import Optional

from . import errors
from .castle_state import CastleState
from .move import Move, CastleMove, CastleType
from .piece import PieceColor, Piece, PIECES, PieceType
from .square import Square


class Board:
    """A chess board.

    Internally, the board is represented as a 2D list.
    """

    __slots__ = (
        'rows',
        'active_color',
        'castle_state',
        'en_passant_square',
        'fullmoves',
        'halfmoves',
        'move_history'
    )

    DEFAULT_FEN = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'

    rows: list[list[Optional[Piece]]]
    active_color: int
    castle_state: CastleState
    en_passant_square: Optional[Square]
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
        self.en_passant_square = None
        self.fullmoves = 1
        self.halfmoves = 0
        self.move_history = []

    def __repr__(self) -> str:
        return f'<Board fen={self.fen}>'

    @classmethod
    def default(cls):
        """Returns the default board layout."""

        return cls.from_fen(cls.DEFAULT_FEN)

    @classmethod
    def from_fen(cls, fen: str):
        """Parses a FEN string into a board."""

        self = cls()

        split_fen = fen.split()

        if len(split_fen) != 6:
            raise errors.InvalidFEN()

        (
            piece_placement,
            active_color,
            castle_state,
            en_passant_square,
            halfmoves,
            fullmoves
        ) = split_fen

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
            raise errors.InvalidFEN()

        # castle state
        self.castle_state = CastleState.from_fen(castle_state)

        # en passant state
        if en_passant_square != '-':
            self.en_passant_square = Square.from_san(en_passant_square)

            # bugfix for lost en passant move
            up_or_down = 1 if self.active_color is PieceColor.WHITE else -1
            from_square_row = self.en_passant_square.row + up_or_down
            from_square = Square(from_square_row, self.en_passant_square.column)
            to_square_row = self.en_passant_square.row - up_or_down
            to_square = Square(to_square_row, self.en_passant_square.column)
            self.move_history.append(Move(from_square, to_square, self.castle_state, en_passant=from_square))

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
        """Returns a FEN string of the board."""

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
        if self.en_passant_square:
            result += self.en_passant_square.san
        else:
            result += '-'

        result += ' '

        # halfmoves and fullmoves
        result += str(self.halfmoves)
        result += ' '
        result += str(self.fullmoves)

        return result

    def get(self, square: Square):
        """Returns the piece on a Square, if any."""

        return self.rows[square.row][square.column]

    def is_in_check(self, color: int = None) -> bool:
        """Returns whether or not a color is in check.

        The color defaults to the active color.
        """

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
        """Returns whether the board is a checkmate."""

        if self.is_in_check() and not list(self.legal_moves()):
            return True

        return False

    def is_stalemate(self) -> bool:
        """Returns whether the board is a stalemate."""

        if self.halfmoves >= 100:
            return True

        if not self.is_in_check and not list(self.legal_moves()):
            return True

        return False

    def _controls_square(self, color: int, square: Square):
        """Returns whether or not a Square is controlled by a color."""

        for i, row in enumerate(self.rows):
            for j, piece in enumerate(row):
                if not piece:
                    continue
                if piece.color != color:
                    continue

                current_square = Square(i, j)
                for move in piece.moves(self, current_square):
                    if move == square:
                        return True

        return False

    def _check_castle(self, white_squares: tuple[Square, Square], black_squares: tuple[Square, Square]):
        """Performs part of the castle detection logic."""

        if self.active_color == PieceColor.WHITE:
            squares_to_check = white_squares
            color = PieceColor.BLACK
        else:
            squares_to_check = black_squares
            color = PieceColor.WHITE

        can_castle: bool = True

        for square in squares_to_check:
            if self.get(square) or self._controls_square(color, square):
                can_castle = False

        return can_castle

    def pseudo_legal_moves(self):
        """Returns a generator of all pseudo-legal moves on the board."""

        # regular moves
        for i, row in enumerate(self.rows):
            for j, piece in enumerate(row):
                if not piece:
                    continue
                if piece.color != self.active_color:
                    continue

                square = Square(i, j)
                for move in piece.moves(self, square):
                    capture = self.get(move)

                    if piece.type == PieceType.PAWN and move == self.en_passant_square:
                        up_or_down = -1 if piece.color is PieceColor.WHITE else 1
                        original_piece_row = self.en_passant_square.row + up_or_down
                        en_passant = Square(original_piece_row, move.column)
                        capture = self.get(en_passant)
                    else:
                        en_passant = None

                    yield Move(square, move, capture=capture, castle_state=self.castle_state.copy(), en_passant=en_passant)

        # castle moves
        if self.is_in_check():
            return

        if self.castle_state.can_castle_kingside(self.active_color):
            if self._check_castle(
                (Square(0, 6), Square(0, 5)),
                (Square(7, 6), Square(7, 5))
            ):
                yield CastleMove(CastleType.KINGSIDE, self.castle_state.copy())

        if self.castle_state.can_castle_queenside(self.active_color):
            if self._check_castle(
                (Square(0, 2), Square(0, 3)),
                (Square(7, 2), Square(7, 3))
            ):
                yield CastleMove(CastleType.QUEENSIDE, self.castle_state.copy())

    def legal_moves(self, color: int = None):
        """Returns a generator of all legal moves on the board."""

        active_color = self.active_color

        for move in self.pseudo_legal_moves():
            valid: Optional[bool] = False

            # make the move, see if still in check, unmake the move
            self.make_move(move)
            if not self.is_in_check(active_color):
                valid = True
            self.unmake_move(move)

            if valid:
                yield move

    def _is_double_pawn_push(self, piece: Optional[Piece], move: Move) -> bool:
        """Returns whether or not a move is a double pawn push."""

        if piece and piece.type != PieceType.PAWN:
            return False

        if abs(move.from_square.row - move.to_square.row) == 2:
            return True

        return False

    def make_move(self, move: Move):
        """Updates the internal board state to reflect a move.

        This does NOT check if the move is valid.
        It simply performs a replacement and updates the board's state.
        """

        if isinstance(move, CastleMove):
            # this is such a disgusting mess.
            # I'm so sorry

            king_from_square = move.king_from_square(self.active_color)
            king_to_square = move.king_to_square(self.active_color)
            rook_from_square = move.rook_from_square(self.active_color)
            rook_to_square = move.rook_to_square(self.active_color)

            piece = self.get(king_from_square)
            self.rows[king_from_square.row][king_from_square.column] = None
            self.rows[king_to_square.row][king_to_square.column] = piece

            piece = self.get(rook_from_square)
            self.rows[rook_from_square.row][rook_from_square.column] = None
            self.rows[rook_to_square.row][rook_to_square.column] = piece

        else:
            piece = self.get(move.from_square)
            self.rows[move.from_square.row][move.from_square.column] = None
            self.rows[move.to_square.row][move.to_square.column] = piece

            if move.en_passant:
                self.rows[move.en_passant.row][move.en_passant.column] = None

        self.move_history.append(move)

        if self.active_color is PieceColor.BLACK:
            self.fullmoves += 1

        # en passant
        if not isinstance(move, CastleMove) and self._is_double_pawn_push(piece, move):
            en_passant_row = (move.from_square.row + move.to_square.row) // 2
            self.en_passant_square = Square(en_passant_row, move.from_square.column)
        else:
            self.en_passant_square = None

        # castling
        if isinstance(move, CastleMove) or (piece and piece.type == PieceType.KING):
            change = 0b0011 if self.active_color == PieceColor.WHITE else 0b1100
            self.castle_state.id &= change

        elif piece and piece.type == PieceType.ROOK:
            if self.active_color == PieceColor.WHITE:
                kingside_square = Square(0, 7)
                kingside_change = 0b0100
                queenside_square = Square(0, 0)
                queenside_change = 0b1000
            else:
                kingside_square = Square(7, 7)
                kingside_change = 0b0001
                queenside_square = Square(7, 0)
                queenside_change = 0b0010

            if move.from_square == kingside_square:
                self.castle_state.id &= kingside_change
            elif move.from_square == queenside_square:
                self.castle_state.id &= queenside_change

        self.active_color = PieceColor.BLACK if self.active_color else PieceColor.WHITE

    def unmake_move(self, move: Move):
        """Updates the internal board state to reflect a move being unmade."""

        if isinstance(move, CastleMove):
            # here we go again.
            # this is just the code from Board.make_move, but the values are switched

            color = PieceColor.WHITE if self.active_color == PieceColor.BLACK else PieceColor.BLACK
            king_from_square = move.king_from_square(color)
            king_to_square = move.king_to_square(color)
            rook_from_square = move.rook_from_square(color)
            rook_to_square = move.rook_to_square(color)

            piece = self.get(king_to_square)
            self.rows[king_to_square.row][king_to_square.column] = None
            self.rows[king_from_square.row][king_from_square.column] = piece

            piece = self.get(rook_to_square)
            self.rows[rook_to_square.row][rook_to_square.column] = None
            self.rows[rook_from_square.row][rook_from_square.column] = piece

        else:
            piece = self.rows[move.to_square.row][move.to_square.column]
            self.rows[move.to_square.row][move.to_square.column] = move.capture
            self.rows[move.from_square.row][move.from_square.column] = piece

            if move.en_passant:
                self.rows[move.en_passant.row][move.en_passant.column] = move.capture
                self.rows[move.to_square.row][move.to_square.column] = None

        # en passant
        if len(self.move_history) >= 2:
            last_move = self.move_history[-2]
            last_move_piece = self.get(last_move.to_square)
            if not isinstance(last_move, CastleMove) and self._is_double_pawn_push(last_move_piece, last_move):
                en_passant_row = (last_move.from_square.row + last_move.to_square.row) // 2
                self.en_passant_square = Square(en_passant_row, last_move.from_square.column)
            else:
                self.en_passant_square = None
        else:
            self.en_passant_square = None

        if self.move_history[-1] == move:
            self.move_history.pop(-1)

        if self.active_color is PieceColor.WHITE:
            self.fullmoves -= 1

        # lazy castle state stuff
        self.castle_state = move.castle_state

        self.active_color = PieceColor.BLACK if self.active_color else PieceColor.WHITE

    def parse_san(self, san: str) -> Move:
        """Parses a string in Standard Algebraic Notation and returns the Move."""

        piece: Optional[Piece] = None
        from_row: Optional[int] = None
        from_column: Optional[int] = None
        to_square: Optional[Square] = None

        if san in ('0-0', 'O-O'):
            return CastleMove(CastleType.KINGSIDE, self.castle_state.copy())

        if san in ('0-0-0', 'O-O-O'):
            return CastleMove(CastleType.QUEENSIDE, self.castle_state.copy())

        for i, char in enumerate(san):
            # see if a piece if specified
            possible_fens = [Piece.FEN.upper() for Piece in PIECES]

            if char in possible_fens:
                piece = Piece.from_fen(char, color=self.active_color)
                continue

            if char in Square.FILES:
                # we are either at the final square's file or the first square's file'
                remaining_len = len(san) - i - 1
                promotion_pieces = ('Q', 'R', 'B', 'N')
                is_promotion = (
                    (remaining_len == 2 and san[i + 2] in promotion_pieces)
                    or (remaining_len == 3 and san[i + 2] == '=' and san[i + 3] in promotion_pieces)
                )
                if remaining_len == 1 or is_promotion:
                    # we are at the final square's file
                    to_square = Square(int(san[i + 1]) - 1, Square.FILES.index(char))
                    # TODO: promotion
                    break
                else:
                    # we are at the first square's file
                    # the next char could be a rank
                    from_column = Square.FILES.index(char)
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

        could_be_castle: bool = False

        possible_squares = (Square(0, 0), Square(0, 7), Square(7, 0), Square(7, 7))
        if piece and piece.type == PieceType.KING and to_square in possible_squares:
            could_be_castle = True

        for legal_move in legal_moves:
            if isinstance(legal_move, CastleMove):
                if could_be_castle and to_square == legal_move.rook_from_square(self.active_color):
                    return legal_move
                else:
                    continue

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

    def push_san(self, san: str) -> Move:
        """Pushes a inputted move to the board in Standard Algebraic Notation."""

        move = self.parse_san(san)
        self.make_move(move)
        return move
