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


RESOURCE_DIR = os.path.join(os.path.dirname(__file__), 'resource')


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
    TYPE = _declare_constants(
        obj_name='TYPE',
        std='STANDARD',
        c9lx='CHESS 960',
    )
    DEFAULT_PLAY_TIME = 10
    DEFAULT_BONUS_TIME = 0


@enum.unique
class EngineType(enum.Enum):
    stockfish = 0
    leela = 1


@enum.unique
class ToolCommand(enum.Enum):
    reset = 0
    new = 1
    load = 2
    option = 3
    border = 4
    pause = 5
    play = 6
    save = 7
    threat = 8
    zen = 9


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
    MEDIUM_HEIGHT = 30

    FONT_FAMILY = 'Andale Mono'
    FONT_FILE_PATH = os.path.join(RESOURCE_DIR, f'font/{FONT_FAMILY}.ttf')

    CHESS_FONT_FAMILY = 'DejaVuSans'
    CHESS_FONT_FILE_PATH = os.path.join(
        RESOURCE_DIR, f'font/{CHESS_FONT_FAMILY}.ttf'
    )

    PIECE_UNICODE = _declare_constants(
        obj_name='PIECE_UNICODE',
        pawn=_declare_constants(
            obj_name='PAWN_UNICODE',
            white='\U00002659',
            black='\U0000265F',
        ),
        knight=_declare_constants(
            obj_name='KNIGHT_UNICODE',
            white='\U00002658',
            black='\U0000265E',
        ),
        bishop=_declare_constants(
            obj_name='BISHOP_UNICODE',
            white='\U00002657',
            black='\U0000265D',
        ),
        rook=_declare_constants(
            obj_name='ROOK_UNICODE',
            white='\U00002656',
            black='\U0000265C',
        ),
        queen=_declare_constants(
            obj_name='QUEEN_UNICODE',
            white='\U00002655',
            black='\U0000265B',
        ),
        king=_declare_constants(
            obj_name='KING_UNICODE',
            white='\U00002654',
            black='\U0000265A',
        ),
    )

    HIGHLIGHT_COLOR = _declare_constants(
        obj_name='HIGHLIGHT_COLOR',
        src=(165, 255, 140, 50),
        dst=(255, 240, 28, 50),
        selected=(252, 73, 3, 50),
        threatened=(255, 24, 14, 20),
    )
    MOVE_WIDGET_WIDTH = 400
    COLLAPSE_BTN_WIDTH = 20
    AI_BTN_WIDTH = 200
    AI_BTN_HEIGHT = 50


class IMAGE:
    NB_SQUARES = 8

    IMAGE_DIR = os.path.join(RESOURCE_DIR, 'image')

    BOARD_IMAGE_NAME = 'board.png'
    BOARD_IMAGE_FILE_PATH = os.path.join(IMAGE_DIR, BOARD_IMAGE_NAME)

    SPLASH_IMAGE_NAME = 'splash.png'
    SPLASH_IMAGE_FILE_PATH = os.path.join(IMAGE_DIR, SPLASH_IMAGE_NAME)

    PAUSE_IMAGE_NAME = 'pause.png'
    PAUSE_IMAGE_FILE_PATH = os.path.join(IMAGE_DIR, PAUSE_IMAGE_NAME)

    BORDER_IMAGE_NAME = 'border.png'
    BORDER_IMAGE_FILE_PATH = os.path.join(IMAGE_DIR, BORDER_IMAGE_NAME)

    PYCHESS_IMAGE_NAME = 'pychess.png'
    PYCHESS_IMAGE_FILE_PATH = os.path.join(IMAGE_DIR, PYCHESS_IMAGE_NAME)

    GRID_IMAGE_NAME = 'grid.png'
    GRID_IMAGE_FILE_PATH = os.path.join(IMAGE_DIR, GRID_IMAGE_NAME)

    BTN_IMAGE = _declare_constants(
        obj_name='BTN_IMAGE',
        reset=_declare_constants(
            obj_name='RESET_IMAGES',
            default='btn_reset.png',
            active='btn_reset_a.png',
            tooltip='Reset',
            cmd=ToolCommand.reset,
        ),
        new=_declare_constants(
            obj_name='NEW_IMAGES',
            default='btn_new.png',
            active='btn_new_a.png',
            tooltip='Start a new game',
            cmd=ToolCommand.new,
        ),
        threat=_declare_constants(
            obj_name='THREAT_IMAGES',
            default='btn_threat.png',
            active='btn_threat_a.png',
            tooltip='Toggle threatened pieces display',
            cmd=ToolCommand.threat,
        ),
        border=_declare_constants(
            obj_name='BORDER_IMAGES',
            default='btn_border.png',
            active='btn_border_a.png',
            tooltip='Toggle square address display',
            cmd=ToolCommand.border,
        ),
        load=_declare_constants(
            obj_name='LOAD_IMAGES',
            default='btn_load.png',
            active='btn_load_a.png',
            tooltip='Load game from pgn file',
            cmd=ToolCommand.load,
        ),
        option=_declare_constants(
            obj_name='OPTION_IMAGES',
            default='btn_option.png',
            active='btn_option_a.png',
            tooltip='Open settings',
            cmd=ToolCommand.option,
        ),
        pause=_declare_constants(
            obj_name='PAUSE_IMAGES',
            default='btn_pause.png',
            active='btn_pause_a.png',
            tooltip='Toggle pause/resume game',
            cmd=ToolCommand.pause,
        ),
        play=_declare_constants(
            obj_name='PLAY_IMAGES',
            default='btn_play.png',
            active='btn_play_a.png',
            tooltip='Toggle pause/resume game',
            cmd=ToolCommand.play,
        ),
        save=_declare_constants(
            obj_name='SAVE_IMAGES',
            default='btn_save.png',
            active='btn_save_a.png',
            tooltip='Save game as pgn file',
            cmd=ToolCommand.save,
        ),
        zen=_declare_constants(
            obj_name='ZEN_IMAGES',
            default='btn_zen.png',
            active='btn_zen_a.png',
            tooltip='Zen mode minimal UI',
            cmd=ToolCommand.zen,
        ),
    )

    PIECE_IMAGE = _declare_constants(
        obj_name='PIECE_IMAGE',
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
            obj_name='QUEEN_IMAGES',
            white='queen.png',
            black='queen_b.png'
        ),
        queen_small=_declare_constants(
            obj_name='QUEEN_SMALL_IMAGES',
            white='queen_small.png',
            black='queen_small_b.png'
        ),
        king=_declare_constants(
            obj_name='KING_IMAGES',
            white='king.png',
            black='king_b.png'
        ),
    )

    BASE_IMAGE_SIZE = 600
    SQUARE_SIZE = 68
    BORDER_SIZE = 28
    NON_PAWN_IMAGE_SIZE = 48
    PAWN_IMAGE_SIZE = 42
    DEFAULT_SIZE = 600
    CAPTURABLES_IMAGE_WIDTH = 600
    LEAD_FONT_SIZE = 18
    MOVIE_FONT_SIZE = 18
    SPLASH_RECT_SIZE = int(BASE_IMAGE_SIZE / NB_SQUARES)

    NON_PAWN_SMALL_IMAGE_SIZE = int(NON_PAWN_IMAGE_SIZE / 2)
    PAWN_SMALL_IMAGE_SIZE = int(PAWN_IMAGE_SIZE / 2)
    SMALL_PIECE_STR = 'small'
