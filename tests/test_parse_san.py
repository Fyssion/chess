import chess
from chess.errors import InvalidMove, DisambiguationError, PromotionError
from chess.castle_state import CastleState
from chess.piece import PieceColor


def create_move(
    from_san: str,
    to_san: str,
    castle: str,
    capture_str: str = None,
    en_passant_str: str = None,
    promotion_str: str = None,
    color: int = PieceColor.WHITE
):
    from_square = chess.Square.from_san(from_san)
    to_square = chess.Square.from_san(to_san)
    castle_state = CastleState.from_fen(castle)
    capture = None
    en_passant = None
    promotion = None
    if capture_str:
        opposite = PieceColor.WHITE if color == PieceColor.BLACK else PieceColor.BLACK
        capture = chess.Piece.from_fen(capture_str, opposite)
    if en_passant_str:
        en_passant = chess.Square.from_san(en_passant_str)
    if promotion_str:
        promotion = chess.Piece.from_fen(promotion_str, color)

    return chess.Move(from_square, to_square, castle_state, capture=capture, en_passant=en_passant, promotion=promotion)


# TODO:
# en passant
# castling
# checks


# fen: {san: Move}
successes = {
    'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1': {
        'd3': create_move('d2', 'd3', 'KQkq'),
        'd4': create_move('d2', 'd4', 'KQkq'),
        'Nc3': create_move('b1', 'c3', 'KQkq')
    },
    'rnbq1bnr/pppPpk2/5ppp/8/8/8/PPPP1PPP/RNBQKBNR w KQ - 1 5': {
        'c8Q': create_move('d7', 'c8', 'KQ', capture_str='B', promotion_str='Q')
    }
}

failures = {
    'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1': {
        'c3': DisambiguationError,
        'Qd2': InvalidMove
    },
    'rnbq1bnr/pppPpk2/5ppp/8/8/8/PPPP1PPP/RNBQKBNR w KQ - 1 5': {
        'c8': PromotionError
    }
}


def test_success():
    for fen, moves in successes.items():
        board = chess.Board.from_fen(fen)

        for test, expected in moves.items():
            move = board.parse_san(test)

            assert move.from_square == expected.from_square
            assert move.to_square == expected.to_square
            assert move.capture == expected.capture
            assert move.en_passant == expected.en_passant
            assert move.castle == expected.castle
            assert move.promotion == expected.promotion
            assert move.castle_state == expected.castle_state

            assert move == expected


def test_failures():
    for fen, moves in failures.items():
        board = chess.Board.from_fen(fen)

        for test, Error in moves.items():
            try:
                board.parse_san(test)
            except Exception as e:
                assert isinstance(e, Error)
