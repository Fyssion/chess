from .piece import PieceColor


class CastleState:
    """The castle state of the board.

    This is internally stored as four bits similar to FEN.

    Examples:
    1111 -> KQkq
    1010 -> Kk
    """

    def __init__(self, id: int = 0):
        self.id = id

    def __eq__(self, other) -> bool:
        return (
            isinstance(other, self.__class__)
            and self.id == other.id
        )

    def __repr__(self) -> str:
        return f'<CastleState fen="{self.fen}">'

    @classmethod
    def from_fen(cls, fen: str):
        castle_state = 0

        if fen != '-':
            for char in fen:
                if char == 'K':
                    castle_state |= 0b1000
                elif char == 'Q':
                    castle_state |= 0b0100
                elif char == 'k':
                    castle_state |= 0b0010
                elif char == 'q':
                    castle_state |= 0b0001

        return cls(castle_state)

    @property
    def fen(self) -> str:
        fen = ''

        if self.id:
            if self.id & 0b1000:
                fen += 'K'
            if self.id & 0b0100:
                fen += 'Q'
            if self.id & 0b0010:
                fen += 'k'
            if self.id & 0b0001:
                fen += 'q'
        else:
            fen += '-'

        return fen

    def can_castle_kingside(self, color: int) -> bool:
        comparison = 0b1000 if color == PieceColor.WHITE else 0b0010
        return bool(self.id & comparison)

    def can_castle_queenside(self, color: int) -> bool:
        comparison = 0b0100 if color == PieceColor.WHITE else 0b0001
        return bool(self.id & comparison)

    def copy(self):
        return CastleState(self.id)
