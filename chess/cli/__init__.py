import random
from typing import Optional

from rich.console import Console
from rich.progress import Progress
from rich.prompt import Prompt, Confirm, PromptBase, InvalidResponse

import chess
from chess.errors import InvalidFEN, InvalidMove, DisambiguationError, PromotionError
from chess.piece import PieceColor
from chess.engines import Engine, OysterEngine

from .board import Board


console = Console()


# TODO:
# make this code look nicer
# add a command parser?
# use better colors


def main():
    help_message = (
        '[blue]Hello![/] Welcome to [red]chess[/].\n'
        '[underline red]Commands:[/]\n'
        '[bold magenta]undo[/] - Undoes the last move\n'
        '[bold magenta]fen[/] - Prints the board\'s FEN string\n'
        '[bold magenta]help[/] - Shows this message\n'
        '[bold magenta]quit[/] - Quits the program'
    )

    console.print(help_message, '\n')

    while True:
        fen = Prompt.ask('Please input a FEN string or press enter to begin')
        if not fen:
            fen = Board.DEFAULT_FEN

        try:
            board = Board.from_fen(fen)
        except InvalidFEN:
            console.print('[prompt.invalid]Please enter a valid FEN string.')
        else:
            break

    engine: Optional[Engine] = None
    player_color: Optional[int] = None
    play_engine = Confirm.ask('Do you want to play against an engine?')
    if play_engine:
        white_or_black = Prompt.ask('Please enter your piece color (or r for random)', choices=['w', 'b', 'r'], default='r')
        if white_or_black == 'w':
            player_color = PieceColor.WHITE
        elif white_or_black == 'b':
            player_color = PieceColor.BLACK
        else:
            player_color = random.choice((PieceColor.WHITE, PieceColor.BLACK))

        # TODO: add engine choosing process
        engine = OysterEngine()

    should_print: bool = True

    while True:
        if should_print:
            console.print(board.render())

        should_print = False

        if board.is_checkmate():
            color = 'White' if board.active_color == PieceColor.BLACK else 'Black'
            console.print(f'[bold magenta]Checkmate![/] {color} wins.')
            break

        if board.is_stalemate():
            console.print('Stalemate!')
            break

        if engine and board.active_color != player_color:
            with Progress(console=console, transient=True) as progress:
                progress.add_task("[yellow]Thinking", total=1000, start=False)
                board.make_move(engine.get_move(board))
            console.print(f'Evaluated {engine.counter} positions.')
            should_print = True
            continue

        move = Prompt.ask('Please enter a [magenta]move in algebraic notation[/] or a [magenta]command[/]')

        if not move:
            continue

        # TODO: command parser yay!

        if move.lower() == 'help':
            console.print(help_message)
            continue

        if move.lower() in ('q', 'quit'):
            if Confirm.ask('Really quit?'):
                console.print('Goodbye!', style='bold blue')
                return

        if move.lower() in ('u', 'undo'):
            if not board.move_history:
                console.print('[prompt.invalid]No move to undo.')
            else:
                print(board.move_history[-1].castle_state)
                board.unmake_move(board.move_history[-1])
            should_print = True
            continue

        if move.lower() == 'fen':
            console.print(board.fen)
            continue

        if move.lower() == 'board':
            should_print = True
            continue

        try:
            print(board.push_san(move).castle_state)
        except InvalidMove:
            console.print('[prompt.invalid]Please enter a valid move.')
        except PromotionError:
            promotion = Prompt.ask('Please enter a piece to promote to', choices=['Q', 'R', 'B', 'N'])
            console.print(move + promotion)
            board.push_san(move + promotion)
            should_print = True
        except DisambiguationError as e:
            move = Prompt.ask(
                'Could not disambiguate between multiple moves. Please select a move',
                choices=[m.uci for m in e.moves]
            )
            board.push_san(move)
            should_print = True
        else:
            should_print = True
