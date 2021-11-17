from typing import Optional, final

from rich.console import Console
from rich.markdown import Markdown
from rich.prompt import Prompt, Confirm, PromptBase, InvalidResponse

import chess
from chess.errors import InvalidFEN, DisambiguationError
from chess.piece import PieceColor

from .board import Board


console = Console()


def prompt(message: str) -> Optional[str]:
    return console.input(f'{message}\n> ')


WHITE_PRETTY_PIECES = {'R': '♜', 'N': '♞', 'B': '♝', 'Q': '♛', 'K': '♚', 'P': '♟'}
BLACK_PRETTY_PIECES = {'r': '♖', 'n': '♘', 'b': '♗', 'q': '♕', 'k': '♔', 'p': '♙'}


def display_board(board: chess.Board):
    result = ''

    for i, row in enumerate(reversed(board.rows)):
        result += f'{8 - i} '
        for piece in row:
            if not piece:
                char = '·'
            else:
                if piece.color == PieceColor.WHITE:
                    char = f'[cyan]{self.WHITE_PRETTY_PIECES[piece.fen]}[/]'
                else:
                    char = f'[orange]{self.BLACK_PRETTY_PIECES[piece.fen]}[/]'

            result += char + ' '
        if i + 1 != len(board.rows):
            result += '\n'

    turn = 'White' if board.active_color == PieceColor.WHITE else 'Black'
    console.print(Markdown(f"**It's {turn}'s turn!** | Move {board.fullmoves}"))
    console.print(result)
    console.print('  ' + ' '.join(chess.Square.FILES))


def main():
    fen = Prompt.ask('Please input a FEN string or press enter to begin')
    if not fen:
        fen = Board.DEFAULT_FEN

    board = Board.from_fen(fen)

    while True:
        console.print(board.render())
        move = Prompt.ask('Please enter a move in algebraic notation')

        if not move:
            continue

        if move.lower() in ('q', 'quit'):
            if Confirm.ask('Really quit?'):
                console.print('Goodbye!', style='bold blue')
                return

        console.print(move)
        try:
            result = board.parse_san(move)
        except InvalidFEN:
            console.print('[prompt.invalid]Please enter a valid move.')
        except DisambiguationError as e:
            move = Prompt.ask(
                'Could not disambiguate between multiple moves. Please confirm your move',
                choices=[str(m) for m in e.moves]
            )
        else:
            console.print(result)


main()
