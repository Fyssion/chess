from rich.console import Console
from rich.prompt import Prompt, Confirm, PromptBase, InvalidResponse

import chess
from chess.errors import InvalidFEN, InvalidMove, DisambiguationError
from chess.piece import PieceColor

from .board import Board


console = Console()


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
                board.unmake_move(board.move_history[-1])
            should_print = True
            continue

        if move.lower() == 'fen':
            console.print(board.fen)
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
            should_print = True


main()
