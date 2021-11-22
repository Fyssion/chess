from typing import Optional

import chess
from chess.move import Move
from chess.piece import Piece, PieceColor, PieceType
from .base import Engine


PIECE_SQUARE_TABLES = {
    PieceType.PAWN: [
            (  0,   0,   0,   0,   0,   0,   0,   0),
            ( 78,  83,  86,  73, 102,  82,  85,  90),
            (  7,  29,  21,  44,  40,  31,  44,   7),
            (-17,  16,  -2,  15,  14,   0,  15, -13),
            (-26,   3,  10,   9,   6,   1,   0, -23),
            (-22,   9,   5, -11, -10,  -2,   3, -19),
            (-31,   8,  -7, -37, -36, -14,   3, -31),
            (  0,   0,   0,   0,   0,   0,   0,   0)
        ],
    PieceType.KNIGHT: [
           (-66, -53, -75, -75, -10, -55, -58, -70),
           ( -3,  -6, 100, -36,   4,  62,  -4, -14),
           ( 10,  67,   1,  74,  73,  27,  62,  -2),
           ( 24,  24,  45,  37,  33,  41,  25,  17),
           ( -1,   5,  31,  21,  22,  35,   2,   0),
           (-18,  10,  13,  22,  18,  15,  11, -14),
           (-23, -15,   2,   0,   2,   0, -23, -20),
           (-74, -23, -26, -24, -19, -35, -22, -69)
        ],
    PieceType.BISHOP: [
           (-59, -78, -82, -76, -23,-107, -37, -50),
           (-11,  20,  35, -42, -39,  31,   2, -22),
           ( -9,  39, -32,  41,  52, -10,  28, -14),
           ( 25,  17,  20,  34,  26,  25,  15,  10),
           ( 13,  10,  17,  23,  17,  16,   0,   7),
           ( 14,  25,  24,  15,   8,  25,  20,  15),
           ( 19,  20,  11,   6,   7,   6,  20,  16),
           ( -7,   2, -15, -12, -14, -15, -10, -10)
        ],
    PieceType.ROOK: [
           ( 35,  29,  33,   4,  37,  33,  56,  50),
           ( 55,  29,  56,  67,  55,  62,  34,  60),
           ( 19,  35,  28,  33,  45,  27,  25,  15),
           (  0,   5,  16,  13,  18,  -4,  -9,  -6),
           (-28, -35, -16, -21, -13, -29, -46, -30),
           (-42, -28, -42, -25, -25, -35, -26, -46),
           (-53, -38, -31, -26, -29, -43, -44, -53),
           (-30, -24, -18,   5,  -2, -18, -31, -32)
        ],
    PieceType.QUEEN: [
           (  6,   1,  -8,-104,  69,  24,  88,  26),
           ( 14,  32,  60, -10,  20,  76,  57,  24),
           ( -2,  43,  32,  60,  72,  63,  43,   2),
           (  1, -16,  22,  17,  25,  20, -13,  -6),
           (-14, -15,  -2,  -5,  -1, -10, -20, -22),
           (-30,  -6, -13, -11, -16, -11, -16, -27),
           (-36, -18,   0, -19, -15, -15, -21, -38),
           (-39, -30, -31, -13, -31, -36, -34, -42)
        ],
    PieceType.KING: [
           (  4,  54,  47, -99, -99,  60,  83, -62),
           (-32,  10,  55,  56,  56,  55,  10,   3),
           (-62,  12, -57,  44, -67,  28,  37, -31),
           (-55,  50,  11,  -4, -19,  13,   0, -49),
           (-55, -43, -52, -28, -51, -47,  -8, -50),
           (-47, -42, -43, -79, -64, -32, -29, -32),
           ( -4,   3, -14, -50, -57, -18,  13,   4),
           ( 17,  30,  -3, -14,   6,  -1,  40,  18)
        ],
}


class OysterEngine(Engine):
    """A chess engine named Oyster."""

    def __init__(self):
        self.move_table: dict[str, Move] = {}
        self.score_table: dict[Move, float] = {}

        self.counter = 0

    PIECE_SCORES = {
        PieceType.KING: 200,
        PieceType.QUEEN: 9,
        PieceType.ROOK: 5,
        PieceType.BISHOP: 3,
        PieceType.KNIGHT: 3,
        PieceType.PAWN: 1
    }

    MATE_LOWER = PIECE_SCORES[PieceType.KING] - 10*PIECE_SCORES[PieceType.QUEEN]
    MATE_UPPER = PIECE_SCORES[PieceType.KING] + 10*PIECE_SCORES[PieceType.QUEEN]

    def evaluate(self, board: chess.Board) -> float:
        score: float = 0

        # calculate piece scores
        for i, row in enumerate(board.rows):
            for j, piece in enumerate(row):
                if not piece:
                    continue
                negative = -1 if piece.color == PieceColor.BLACK else 1
                score += self.PIECE_SCORES[piece.type] * negative

                table = PIECE_SQUARE_TABLES[piece.type]
                table = list(reversed(table)) if piece.color == PieceColor.WHITE else table

                score += table[i][j]

        # TODO: doubled, blocked, isolated pawns

        # calculate mobility
        white_mobility = len(list(board.legal_moves()))
        # change active color to other and find legal moves
        board.active_color = PieceColor.BLACK if board.active_color == PieceColor.WHITE else PieceColor.WHITE
        black_mobility = len(list(board.legal_moves()))
        board.active_color = PieceColor.BLACK if board.active_color == PieceColor.WHITE else PieceColor.WHITE

        score += 0.1 * (white_mobility - black_mobility)

        who_to_move = -1 if board.active_color == PieceColor.BLACK else 1
        return score * who_to_move

    def negamax(self, board: chess.Board, depth: int, alpha: float, beta: float) -> float:
        self.counter += 1

        if depth == 0:
            return self.evaluate(board)

        best_score = self.MATE_UPPER * -1

        for move in board.legal_moves():
            board.make_move(move)
            score = -self.negamax(board, depth - 1, alpha, beta)
            board.unmake_move(move)

            if score > best_score:
                best_score = score

            if best_score > alpha:
                alpha = best_score

            if beta <= alpha:
                return best_score

        return best_score

    def negamax_root(self, board: chess.Board, depth: int) -> Move:
        best_score: float = self.MATE_UPPER * -1
        best_move: Optional[Move] = None

        for move in board.legal_moves():
            board.make_move(move)
            score = -self.negamax(board, depth - 1, self.MATE_UPPER * -1, self.MATE_UPPER)
            board.unmake_move(move)

            if score > best_score:
                best_score = score
                best_move = move

        assert best_move
        return best_move

    def get_move(self, board: chess.Board):
        self.counter = 0
        best_move = self.negamax_root(board, depth=2)
        return best_move
