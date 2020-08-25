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


@enum.unique
class Direction(enum.Enum):
    #  nw  n  ne
    #    \ | /
    #  w --+-- e
    #    / | \
    #  sw  s  se
    nw = 0
    n = 1
    ne = 2
    w = 3
    e = 4
    sw = 5
    s = 7
    se = 8
