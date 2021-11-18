from .board import Board
from .square import Square
from .piece import PieceColor, King


PRETTY_PIECES = {'R': '♜', 'N': '♞', 'B': '♝', 'Q': '♛', 'K': '♚', 'P': '♟',
                 'r': '♖', 'n': '♘', 'b': '♗', 'q': '♕', 'k': '♔', 'p': '♙', ' ': '·'}


def display_board(board: Board):
    result = ''

    for i, row in enumerate(reversed(board.rows)):
        result += f'{8 - i} '
        for piece in row:
            if not piece:
                char = ' '
            else:
                char = piece.fen
                if piece.color == PieceColor.WHITE:
                    char = char.upper()

            result += PRETTY_PIECES[char] + ' '
        if i + 1 != len(board.rows):
            result += '\n'

    turn = 'White' if board.active_color == PieceColor.WHITE else 'Black'
    print(f"It's {turn}'s turn! | Move {board.fullmoves}")
    print(result)
    print('  ' + ' '.join(Square.FILES))


def display_moves(moves: list[Square]):
    board = Board()
    for move in moves:
        board.rows[move.row][move.column] = King(color=PieceColor.WHITE)
    display_board(board)


print('Inputting default board layout...')
board = Board.default()
display_board(board)
print(bin(board.castle_state.id), board.en_passant_state)
print(board.fen)

# new_fen = 'rnbqkbnr/pp1ppppp/8/2p5/4P3/8/PPPP1PPP/RNBQKBNR w KQkq c6 0 2'
# print(f'Inputting new board layout: FEN {new_fen}')
# new_board = Board.from_fen(new_fen)
# display_board(new_board)
# assert new_board.en_passant_state
# print(bin(new_board.castle_state), new_board.en_passant_state.san)
# print(new_board.fen)

new_fen = '8/3R4/8/3q4/8/8/3r4/8 w KQkq - 0 1'
# new_fen = '8/3R4/2R1r3/3p4/8/8/3r4/8 w KQkq - 0 1'
# new_fen = '8/2p5/8/3p4/2R1r3/8/3P4/8 w KQkq - 0 1'
print(f'Inputting new board layout: FEN {new_fen}')
new_board = Board.from_fen(new_fen)
display_board(new_board)
print(new_board.fen)
square = Square(4, 3)
# square = Square(6, 2)

moves = new_board.get(square).moves(new_board, square)
display_moves(moves)
