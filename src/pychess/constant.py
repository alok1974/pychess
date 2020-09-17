import os
import enum
import collections


def _declare_constants(obj_name, **name_value_dict):
    "A named tuple generator used for declaring contants"
    ConstantContainer = collections.namedtuple(
        obj_name,
        name_value_dict.keys(),
    )
    return ConstantContainer(*name_value_dict.values())


RESOURCE_DIR = os.path.join(os.path.dirname(__file__), 'resources')


class GAME:
    CODE_KNIGHT = 'n'
    PAWN_FIRST_MOVE_DISTANCE = 2
    KING_CASTLE_DISTANCE = 2
    ADDRESS_PATTERN = r"^([abcdefgh])([12345678])$"
    MOVE_PATTERN = r"^([abcdefgh][12345678])([abcdefgh][12345678])$"
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
class PieceType(enum.Enum):
    pawn = 0
    knight = 1
    bishop = 2
    rook = 3
    queen = 4
    king = 5


@enum.unique
class Color(enum.Enum):
    black = 0
    white = 1


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


class STYLESHEET:
    def _get_stylesheet(stylesheet_name):
        stylesheet = None
        stylesheet_file_path = os.path.join(
            f'{RESOURCE_DIR}/css',
            f'{stylesheet_name}.css',
        )
        with open(stylesheet_file_path, 'r') as f:
            stylesheet = f.read()

        return stylesheet

    dark_01 = _get_stylesheet('dark_01')


class APP:
    NAME = "Pychess"
    STYLESHEET = STYLESHEET.dark_01
    BUTTON_HEIGHT = 60
    LCD_HEIGHT = 40
    FONT_FAMILY = 'Andale Mono'
    FONT_FILE_PATH = os.path.join(RESOURCE_DIR, f'font/{FONT_FAMILY}.ttf')
    HIGHLIGHT_COLOR = _declare_constants(
        obj_name='HIGHLIGHT_COLOR',
        src=(165, 255, 140, 50),
        dst=(255, 240, 28, 50),
        selected=(252, 73, 3, 50),
        threatened=(255, 24, 14, 20),
    )


class IMAGE:
    NB_SQUARES = 8
    IMAGE_DIR = os.path.join(RESOURCE_DIR, 'image')
    BOARD_IMAGE_NAME = 'board.png'
    BOARD_IMAGE_FILE_PATH = os.path.join(IMAGE_DIR, BOARD_IMAGE_NAME)

    PIECE_IMAGE = _declare_constants(
        obj_name='IMAGE_NAME',
        pawn=_declare_constants(
            obj_name='PAWN_IMAGES',
            white='pawn.png',
            black='pawn_b.png'
        ),
        pawn_small=_declare_constants(
            obj_name='PAWN_SMALL_IMAGES',
            white='pawn_small.png',
            black='pawn_small_b.png'
        ),
        knight=_declare_constants(
            obj_name='KNIGHT_IMAGES',
            white='knight.png',
            black='knight_b.png'
        ),
        knight_small=_declare_constants(
            obj_name='KNIGHT_SMALL_IMAGES',
            white='knight_small.png',
            black='knight_small_b.png'
        ),
        bishop=_declare_constants(
            obj_name='BISHOP_IMAGES',
            white='bishop.png',
            black='bishop_b.png'
        ),
        bishop_small=_declare_constants(
            obj_name='BISHOP_SMALL_IMAGES',
            white='bishop_small.png',
            black='bishop_small_b.png'
        ),
        rook=_declare_constants(
            obj_name='ROOK_IMAGES',
            white='rook.png',
            black='rook_b.png'
        ),
        rook_small=_declare_constants(
            obj_name='ROOK_SMALL_IMAGES',
            white='rook_small.png',
            black='rook_small_b.png'
        ),
        queen=_declare_constants(
            obj_name='PAWN_IMAGES',
            white='queen.png',
            black='queen_b.png'
        ),
        queen_small=_declare_constants(
            obj_name='PAWN_SMALL_IMAGES',
            white='queen_small.png',
            black='queen_small_b.png'
        ),
        king=_declare_constants(
            obj_name='PAWN_IMAGES',
            white='king.png',
            black='king_b.png'
        ),
    )

    BASE_IMAGE_SIZE = 600
    SQUARE_SIZE = 68
    BORDER_SIZE = 28
    NON_PAWN_IMAGE_SIZE = 48
    PAWN_IMAGE_SIZE = 42
    SUPPORTED_SIZE = [300, 450, 600]
    DEFAULT_SIZE = 600
    CAPTURABLES_IMAGE_WIDTH = 444
    LEAD_FONT_SIZE = 18

    NON_PAWN_SMALL_IMAGE_SIZE = int(NON_PAWN_IMAGE_SIZE / 2)
    PAWN_SMALL_IMAGE_SIZE = int(PAWN_IMAGE_SIZE / 2)
    SMALL_PIECE_STR = 'small'
