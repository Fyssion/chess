import chess
from chess.move import CastleMove
from chess.piece import PieceColor, PieceType


class Board(chess.Board):
    WHITE_PRETTY_PIECES = {'r': '♜', 'n': '♞', 'b': '♝', 'q': '♛', 'k': '♚', 'p': '♟'}
    BLACK_PRETTY_PIECES = {'r': '♖', 'n': '♘', 'b': '♗', 'q': '♕', 'k': '♔', 'p': '♙'}

    BG_COLOR = '#202025'
    TEXT_COLOR = '#e3e3e3'
    DIM_TEXT_COLOR = '#b0b0b0'
    DARK_SQUARE_COLOR = '#00495c'
    LIGHT_SQUARE_COLOR = '#2aa198'
    DARK_SQUARE_HIGHLIGHT_COLOR = '#156f87'
    LIGHT_SQUARE_HIGHLIGHT_COLOR = '#47c5bc'
    DARK_SQUARE_CHECK_COLOR = '#9e3432'
    LIGHT_SQUARE_CHECK_COLOR = '#ce4441'
    WHITE_PIECE_COLOR = '#ffffff'
    BLACK_PIECE_COLOR = '#000000'

    def render(self) -> str:
        result = ''
        is_in_check = self.is_in_check()

        highlighted_squares: 'list[chess.Square]' = []

        if self.move_history:
            move = self.move_history[-1]
            if isinstance(move, CastleMove):
                color = PieceColor.WHITE if self.active_color == PieceColor.BLACK else PieceColor.BLACK
                highlighted_squares.append(move.rook_from_square(color))
                highlighted_squares.append(move.king_from_square(color))
            else:
                highlighted_squares.append(move.from_square)
                highlighted_squares.append(move.to_square)

        for i, row in enumerate(reversed(self.rows)):
            result += f'[{self.DIM_TEXT_COLOR}]{8 - i}[/] '
            for j, piece in enumerate(row):
                if not piece:
                    char = ' '
                else:
                    if piece.color == PieceColor.WHITE:
                        char = f'[{self.WHITE_PIECE_COLOR}]{piece.fen.upper()}[/]'
                        # char = self.WHITE_PRETTY_PIECES[piece.fen]
                    else:
                        char = f'[{self.BLACK_PIECE_COLOR}]{piece.fen}[/]'
                        # char = self.BLACK_PRETTY_PIECES[piece.fen]

                color = self.DARK_SQUARE_COLOR if (i + j) % 2 else self.LIGHT_SQUARE_COLOR

                if is_in_check and piece and piece.color == self.active_color and piece.type == PieceType.KING:
                    color = self.DARK_SQUARE_CHECK_COLOR if color == self.DARK_SQUARE_COLOR else self.LIGHT_SQUARE_CHECK_COLOR

                if chess.Square(7 - i, j) in highlighted_squares:
                    color = self.DARK_SQUARE_HIGHLIGHT_COLOR if color == self.DARK_SQUARE_COLOR else self.LIGHT_SQUARE_HIGHLIGHT_COLOR

                result += f'[white on {color}] {char} [/]'

            if i + 1 != len(self.rows):
                result += '\n'

        turn = 'White' if self.active_color == PieceColor.WHITE else 'Black'
        # check = f'[bold red]{turn} is in check![/]\n' if is_in_check else ''
        output = (
            f"It's [bold magenta]{turn}'s[/] turn! | Move {self.fullmoves}\n"
            # f"{check}"
            f'{result}\n'
            f'  [{self.DIM_TEXT_COLOR}] ' + '  '.join(chess.Square.FILES) + ' [/]'
        )

        lines = output.split('\n')
        modified_lines = []
        for i, line in enumerate(lines):
            if i == 0:
                modified_lines.append(f'  {line}   ')
            else:
                modified_lines.append(f'  {line}    ')

        return f'[{self.TEXT_COLOR} on {self.BG_COLOR}]' + '\n'.join(modified_lines)
