import enum
import collections


def _declare_constants(obj_name, **name_value_dict):
    "A named tuple generator used for declaring contants"
    ConstantContainer = collections.namedtuple(
        obj_name,
        name_value_dict.keys(),
    )
    return ConstantContainer(*name_value_dict.values())


CODE_KNIGHT = 'n'
PAWN_FIRST_MOVE_DISTANCE = 2
KING_CASTLE_DISTANCE = 2
ADDRESS_PATTERN = r"^([abcdefgh])([12345678])$"


@enum.unique
class PieceType(enum.Enum):
    pawn = 0
    knight = 1
    bishop = 2
    rook = 3
    queen = 4
    king = 5


NUM_PIECES = _declare_constants(
    obj_name='NUM_PIECES',
    pawn=8,
    knight=2,
    bishop=2,
    rook=2,
    queen=1,
    king=1,
)


@enum.unique
class Color(enum.Enum):
    white = 0
    black = 1


@enum.unique
class Direction(enum.Enum):
    #       nnw n nne
    #     nw         ne
    #   wnw   \ | /    ene
    #  w      --+--       e
    #   wsw   / | \    ese
    #     sw         se
    #       ssw s sse
    n = 0
    nne = 1
    ne = 2
    ene = 3
    e = 4
    ese = 5
    se = 6
    sse = 7
    s = 8
    ssw = 9
    sw = 10
    wsw = 11
    w = 12
    wnw = 13
    nw = 14
    nnw = 15
