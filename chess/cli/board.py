import chess
from chess.piece import PieceColor, PieceType


class Board(chess.Board):
    WHITE_PRETTY_PIECES = {'r': '♜', 'n': '♞', 'b': '♝', 'q': '♛', 'k': '♚', 'p': '♟'}
    BLACK_PRETTY_PIECES = {'r': '♖', 'n': '♘', 'b': '♗', 'q': '♕', 'k': '♔', 'p': '♙'}

    def render(self) -> str:
        result = ''
        is_in_check = self.is_in_check()

        for i, row in enumerate(reversed(self.rows)):
            result += f'[dim]{8 - i}[/] '
            for j, piece in enumerate(row):
                if not piece:
                    char = ' '
                else:
                    if piece.color == PieceColor.WHITE:
                        char = f'[white]{piece.fen.upper()}[/]'
                        # char = self.WHITE_PRETTY_PIECES[piece.fen]
                    else:
                        char = f'[black]{piece.fen}[/]'
                        # char = self.BLACK_PRETTY_PIECES[piece.fen]

                color = 'grey' if (i + j) % 2 else 'cyan'

                if is_in_check and piece and piece.color == self.active_color and piece.type == PieceType.KING:
                    color = 'red'

                result += f'[white on {color}] {char} [/]'

            if i + 1 != len(self.rows):
                result += '\n'

        turn = 'White' if self.active_color == PieceColor.WHITE else 'Black'
        check = f'[bold red]{turn} is in check![/]\n' if is_in_check else ''
        return (
            f"[bold blue]It's [bold magenta]{turn}'s[/] turn![/] | Move {self.fullmoves}\n"
            f"{check}"
            f'{result}\n'
            '  [dim] ' + '  '.join(chess.Square.FILES) + '[/]'
        )
