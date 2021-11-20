from typing import Optional, final

from rich.console import Console
from rich.markdown import Markdown
from rich.prompt import Prompt, Confirm, PromptBase, InvalidResponse

import chess
from chess.errors import InvalidMove, DisambiguationError
from chess.piece import PieceColor

from .board import Board


console = Console()


def main():
    fen = Prompt.ask('Please input a FEN string or press enter to begin')
    if not fen:
        fen = Board.DEFAULT_FEN

    board = Board.from_fen(fen)

    while True:
        console.print(board.render())

        if board.is_checkmate():
            color = 'White' if board.active_color == PieceColor.BLACK else 'Black'
            console.print(f'[bold magenta]Checkmate![/] {color} wins.')
            break

        if board.is_stalemate():
            console.print('Stalemate!')
            break

        move = Prompt.ask('Please enter a move in algebraic notation')

        if not move:
            continue

        if move.lower() in ('q', 'quit'):
            if Confirm.ask('Really quit?'):
                console.print('Goodbye!', style='bold blue')
                return

        if move.lower() in ('u', 'undo'):
            if not board.move_history:
                console.print('[prompt.invalid]No move to undo.')
            else:
                board.unmake_move(board.move_history[-1])
            continue

        try:
            result = board.push_san(move)
        except InvalidMove:
            console.print('[prompt.invalid]Please enter a valid move.')
        except DisambiguationError as e:
            move = Prompt.ask(
                'Could not disambiguate between multiple moves. Please confirm your move',
                choices=[str(m) for m in e.moves]
            )
        else:
            console.print(result)


main()
