class Square:
    """A square on the board."""

    __slots__ = ('row', 'column')

    FILES = ('a', 'b', 'c', 'd', 'e', 'f', 'g', 'h')
    row: int
    column: int

    def __init__(self, row: int, column: int):
        self.row = row
        self.column = column

    def __eq__(self, other) -> bool:
        return (
            isinstance(other, self.__class__)
            and self.row == other.row
            and self.column == other.column
        )

    def __repr__(self):
        return f'<Square file="{self.file}", rank="{self.rank}">'

    @classmethod
    def from_san(cls, san: str):
        file, rank = list(san)
        return cls(int(rank) - 1, cls.FILES.index(file))

    @property
    def rank(self):
        return self.row + 1

    @property
    def file(self):
        return self.FILES[self.column]

    @property
    def san(self) -> str:
        return f'{self.file}{self.rank}'

    def is_valid(self) -> bool:
        return 0 <= self.row <= 7 and 0 <= self.column <= 7
