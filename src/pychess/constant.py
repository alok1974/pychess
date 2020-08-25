import enum


@enum.unique
class Pieces(enum.Enum):
    pawn = 0
    rook = 1
    knight = 2
    bishop = 3
    queen = 4
    king = 5


@enum.unique
class Color(enum.Enum):
    black = 0
    white = 1
