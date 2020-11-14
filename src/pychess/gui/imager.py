import os
import collections


from PIL import Image, ImageQt, ImageDraw, ImageFont


from .. import constant as c
from ..element.squarer import Square


class Coordinates:
    """
    The image is assumed to be composed as following,

     _____________________________________________________
    |                                                     |
    |     ___________________________________________     |
    |    |          |          |          |          |    |
    |    |     1    |     2    |    3     |    4     |    |
    |    |          |          |          |          |    |
    |    |__________|__________|__________|__________|    |
    |    |  square  |          |          |          |    |
    |    |   size   |          |          |          |    |
    |    |<-------->|          |          |          |    |
    |    |__________|__________|__________|__________|    |
    |    |          |          |          |          |    |
    |    |          |          |          |          |    |
    |    |          |          |          |          |    |
    |    |__________|__________|__________|__________|    |
    |    |          |          |          |          |    |
    |    |          |          |          |          |    |
    |    |          |          |          |          |    |
    |<-->|__________|__________|__________|__________|    |
    | border size                                         |
    |_____________________________________________________|

    In the above,
        nb_squares = 4
        border_size = 4 (1 whitespace == 1 unit)
        square_size = 10 (1 whitespace = 1 unit)

    With this we can define any pixel position on the image in terms of
    squares and vice versa. This class provide methods to find the square
    based on the pixel, find the top left pixel position of each square, and
    given an image size and a square coordinate find the top left position
    where the image should be drawn from (the image to be drawn is always
    assumed to be of square aspect, having same width and height)
    """
    def __init__(
            self, border_size=c.IMAGE.BORDER_SIZE,
            square_size=c.IMAGE.SQUARE_SIZE, nb_square=c.IMAGE.NB_SQUARES,
    ):

        self._border_size = border_size
        self._square_size = square_size
        self._nb_square = nb_square

    def get_image_coordinates(self, image_size, square_x, square_y):
        x, y = self.square_to_pixel(square_x, square_y)
        offset = int((self._square_size - image_size) / 2)
        return x + offset, y + offset

    def pixel_to_square(self, x, y):
        if self.pixel_on_border(x, y):
            return

        square_x = int((x - self._border_size) / self._square_size)
        square_y = c.IMAGE.NB_SQUARES - 1 - int(
            (y - self._border_size) / self._square_size
        )
        return square_x, square_y

    def square_to_pixel(self, square_x, square_y):
        x = (square_x * self._square_size) + self._border_size

        reverse_y_coordinate = c.IMAGE.NB_SQUARES - 1 - square_y
        y = (reverse_y_coordinate * self._square_size) + self._border_size

        return x, y

    def pixel_on_border(self, x, y):
        sqr_sz = self._square_size
        bdr_sz = self._border_size
        nb_sqr = c.IMAGE.NB_SQUARES

        return (
            (x - bdr_sz) < 0 or
            (y - bdr_sz) < 0 or
            (x > (bdr_sz + (nb_sqr * sqr_sz))) or
            (y > (bdr_sz + (nb_sqr * sqr_sz)))
        )


class BoardImage:
    COLOR_MOVE_HINT_CAPTURE = (255, 42, 14)
    COLOR_MOVE_HINT_EMPTY = (127, 127, 127)

    def __init__(self, board):
        self._image_store = {}
        self._coords = Coordinates()
        self.init(board=board)

    @property
    def board(self):
        return self._board

    @property
    def qt_image(self):
        return ImageQt.ImageQt(self._board_image)

    @property
    def image(self):
        return self._board_image

    @property
    def width(self):
        return self._board_image.width

    @property
    def height(self):
        return self._board_image.height

    def is_border_clicked(self, x, y):
        return self._coords.pixel_on_border(x, y)

    def handle_pause_screen(self, is_paused):
        if is_paused:
            self._pause_image = self._load_image(c.IMAGE.PAUSE_IMAGE_FILE_PATH)
            self._board_image.alpha_composite(
                self._pause_image,
                (0, 0),
            )
        else:
            self.update()

    def create_image_with_move(self, src, dst, move_text, save_to_path):
        self.highlight(
            square=src,
            highlight_color=c.APP.HIGHLIGHT_COLOR.src,
        )
        self.highlight(
            square=dst,
            highlight_color=c.APP.HIGHLIGHT_COLOR.dst,
        )
        block = 16
        compliant_dim = self.width + block - (self.width % block)
        band_hint = int(compliant_dim * 0.1)
        height_hint = compliant_dim + band_hint
        true_height = height_hint + block - (height_hint % block)
        border = int((compliant_dim - self.width) / 2)
        size = (compliant_dim, true_height)
        image = Image.new('RGBA', size, color=(59, 57, 55))
        image.alpha_composite(self._board_image, (border, border))
        font = ImageFont.truetype(
            c.APP.FONT_FILE_PATH,
            c.IMAGE.MOVIE_FONT_SIZE,
        )
        ctx = ImageDraw.Draw(image)
        ctx.multiline_text(
            (int(self.width * 0.05), self.height + 5),
            move_text,
            fill=(255, 255, 255),
            font=font,
        )
        image.save(save_to_path)

    def init(self, board):
        self._board = board
        self._threatened_squares = []
        self._selected_square = None
        self._square_size = c.IMAGE.SQUARE_SIZE
        self._border_size = c.IMAGE.BORDER_SIZE
        self._non_pawn_image_size = c.IMAGE.NON_PAWN_IMAGE_SIZE
        self._pawn_image_size = c.IMAGE.PAWN_IMAGE_SIZE
        self._init_board_image()
        self.update()

    def update(self):
        self._board_image.alpha_composite(self._base_image, (0, 0))
        self._draw_pieces()

    def show(self):
        self._board_image.show()

    def clear_threatened_squares(self):
        selected_in_threatened = (
            self._selected_square in self._threatened_squares
        )
        self._restore_color(self._threatened_squares)
        self._threatened_squares = []

        if selected_in_threatened:
            self.highlight(
                self._selected_square,
                highlight_color=c.APP.HIGHLIGHT_COLOR.selected,
                is_first_selected=True,
            )

    def highlight(self, square, highlight_color, is_first_selected=False):
        if is_first_selected:
            self._selected_square = square
            self._draw_move_hint(square)

        if self._selected_square in self._threatened_squares:
            # This square is already highlighted under the rule of
            # show threatened
            return

        x, y = self.square_to_pixel(square)
        size = (self._square_size, self._square_size)
        highlight_image = Image.new('RGBA', size, color=highlight_color)
        self._board_image.alpha_composite(highlight_image, (x, y))
        self._draw_piece(self.board.get_piece(square))

    def toggle_address(self):
        corner_pixel_color = self._base_image.getpixel((0, 0))
        above_corner_color = self._base_image.getpixel(
            (0, c.IMAGE.BORDER_SIZE + 1)
        )

        if corner_pixel_color == above_corner_color:
            # Address is hidden show it
            self._base_image = self._load_image(
                c.IMAGE.BOARD_IMAGE_FILE_PATH,
                flush=True)
        else:
            # Hide address by drawing a plain border on top of the image
            self._border_image = self._load_image(
                c.IMAGE.BORDER_IMAGE_FILE_PATH
            )
            self._base_image.alpha_composite(
                self._border_image,
                (0, 0),
            )

        self.update()

    def draw_threatened(self, pieces):
        to_draw = [self.board.get_square(p) for p in pieces]
        for s in to_draw:
            if s not in self._threatened_squares:
                self._threatened_squares.append(s)

        outline_image = Image.new(
            'RGBA',
            (self._square_size, self._square_size),
            (0, 0, 0, 0)
        )
        draw_context = ImageDraw.Draw(outline_image)
        draw_context.rectangle(
            [
                (0, 0),
                (self._square_size, self._square_size),
            ],
            fill=c.APP.HIGHLIGHT_COLOR.threatened,
            outline=(255, 0, 0, 100),
            width=4,
        )
        for piece in pieces:
            s = self.board.get_square(piece)
            x, y = self.square_to_pixel(s)
            self._board_image.alpha_composite(outline_image, (x, y))
            self._draw_piece(piece)

    def _draw_move_hint(self, square, width=0.03, circle=False):
        incr_min = int(self._square_size * (0.5 - width))
        incr_max = int(self._square_size * (0.5 + width))
        possible_destinations = self.board.move_hint(square)

        draw_context = ImageDraw.Draw(self._board_image)
        for dst, piece in possible_destinations:
            x, y = self.square_to_pixel(dst)
            fill = self.COLOR_MOVE_HINT_EMPTY
            if piece is not None:
                fill = self.COLOR_MOVE_HINT_CAPTURE

            if circle:
                draw_context.ellipse(
                    [
                        (x + incr_min, y + incr_min),
                        (x + incr_max, y + incr_max),
                    ],
                    fill=fill,
                )
            else:
                draw_context.polygon(
                    [
                        (x + incr_min, y + incr_min),
                        (x + incr_max, y + incr_min),
                        (x + incr_max, y + incr_max),
                        (x + incr_min, y + incr_max),
                    ],
                    fill=fill,
                )

    def remove_highlight(self, square):
        if square is None:
            return

        hints = [s for s, _ in self.board.move_hint(square)]
        hints.append(square)
        hints = list(
            filter(
                lambda s: s not in self._threatened_squares,
                hints,
            )
        )
        self._restore_color(hints)

    def _restore_color(self, squares):
        for square in squares:
            x, y = self.square_to_pixel(square)
            size = (self._square_size, self._square_size)
            orig_color = self._initial_square_colors[square]
            orig_square_image = Image.new('RGBA', size, color=orig_color)
            self._board_image.alpha_composite(orig_square_image, (x, y))
            piece = self.board.get_piece(square)
            self._draw_piece(piece)

    def _init_board_image(self):
        self._base_image = self._load_image(c.IMAGE.BOARD_IMAGE_FILE_PATH)
        self._board_image = Image.new(
            'RGBA',
            self._base_image.size,
            color=(0, 0, 0),
        )

        self._initial_square_colors = {
            square: self._base_image.getpixel(self.square_to_pixel(square))
            for square in self.board.squares
        }

    def _draw_pieces(self):
        for piece in self._board.pieces:
            self._draw_piece(piece)

    def _draw_piece(self, piece):
        if piece is None:
            return

        image_path = self._get_piece_image_path(piece)
        piece_image = self._load_image(image_path)
        piece_square = self._board.get_square(piece)
        # x, y = self._get_coordinates(piece_square)
        x, y = self._coords.get_image_coordinates(
            image_size=piece_image.width,
            square_x=piece_square.x,
            square_y=piece_square.y,
        )
        self._board_image.alpha_composite(
            piece_image,
            (x, y),
        )

    def _load_image(self, image_path, flush=False):
        if flush:
            image = Image.open(image_path)
            self._image_store[image_path] = image
        elif image_path not in self._image_store:
            image = Image.open(image_path)
            self._image_store[image_path] = image

        return self._image_store[image_path]

    @staticmethod
    def _get_piece_image_path(piece):
        piece_name = piece.type.name
        color_name = piece.color.name
        piece_images = getattr(c.IMAGE.PIECE_IMAGE, piece_name)
        image_name = getattr(piece_images, color_name)
        image_path = os.path.join(c.IMAGE.IMAGE_DIR, image_name)

        error_msg = f'Image path {image_path} does not exist!'
        assert(os.path.exists(image_path)), error_msg
        return image_path

    def pixel_to_square(self, x, y):
        address = self._coords.pixel_to_square(x, y)
        return Square(address)

    def square_to_pixel(self, square):
        return self._coords.square_to_pixel(square.x, square.y)


class CapturedImage:
    def __init__(self):
        self._image_store = {}
        self.init()

    @property
    def qt_image_white(self):
        return ImageQt.ImageQt(self._captured_image_white)

    @property
    def qt_image_black(self):
        return ImageQt.ImageQt(self._captured_image_black)

    @property
    def image_white(self):
        return self._captured_image_white

    @property
    def image_black(self):
        return self._captured_image_black

    def init(self):
        self._image_width = c.IMAGE.CAPTURABLES_IMAGE_WIDTH
        self._image_height = c.APP.LCD_HEIGHT
        self._pawn_height = c.IMAGE.PAWN_SMALL_IMAGE_SIZE
        self._non_pawn_height = c.IMAGE.NON_PAWN_SMALL_IMAGE_SIZE
        self._lead_font_size = c.IMAGE.LEAD_FONT_SIZE

        self._x_coord_black = None
        self._x_coord_white = None
        self._init_captured_images()

    def _init_captured_images(self):
        self._captured_image_white = Image.new(
            'RGBA',
            (self._image_width, self._image_height),
            color=(0, 0, 0, 0),
        )

        self._captured_image_black = Image.new(
            'RGBA',
            (self._image_width, self._image_height),
            color=(0, 0, 0, 0),
        )

    def update(self, captured_white, captured_black, leader, lead):
        self._init_captured_images()
        self._draw_captured(captured_white)
        self._draw_captured(captured_black)
        self._draw_lead(leader, lead)

    def _draw_captured(self, captured):
        if not captured:
            return

        color = captured[0].color
        if color == c.Color.black:
            image_to_use = self._captured_image_black
        else:
            image_to_use = self._captured_image_white

        x = 10
        groups = collections.Counter([p.type for p in captured])
        for piece_type in c.PieceType:
            if piece_type not in groups:
                continue
            count = groups[piece_type]
            piece_image_path = self._get_piece_image_path(piece_type, color)
            piece_image = self._load_image(piece_image_path)
            y = self._get_y_coordinate(piece_type)
            for _ in range(count):
                image_to_use.alpha_composite(
                    piece_image,
                    (x, y),
                )
                x += 6

            x += piece_image.width + 6

        if color == c.Color.black:
            self._x_coord_black = x
        else:
            self._x_coord_white = x

    def _draw_lead(self, leader, lead):
        if leader is None:
            return

        if leader == c.Color.black:
            image_to_use = self._captured_image_white
            x_coord = self._x_coord_white
        else:
            image_to_use = self._captured_image_black
            x_coord = self._x_coord_black

        text = f'+{lead}'
        draw_context = ImageDraw.Draw(image_to_use)
        font = ImageFont.truetype(
            c.APP.FONT_FILE_PATH,
            size=self._lead_font_size,
        )
        _, font_height = font.getsize(text)
        draw_context.text(
            (
                x_coord,
                int((image_to_use.height - font_height) / 2),
            ),
            text,
            font=font,
            fill=(230, 230, 230, 255),
            align="center",
        )

    def draw_winner(self, winner):
        image_to_use = None
        if winner == c.Color.black:
            image_to_use = self._captured_image_white
        else:
            image_to_use = self._captured_image_black

        text = f'{winner.name.upper()}\nWINS!'
        draw_context = ImageDraw.Draw(image_to_use)
        font = ImageFont.truetype(
            c.APP.FONT_FILE_PATH,
            size=16,
            layout_engine=ImageFont.LAYOUT_BASIC,
        )
        font_widht, font_height = font.getsize(text)
        draw_context.text(
            (
                image_to_use.width - 75,
                1,
            ),
            text,
            font=font,
            fill=(230, 230, 230, 255),
            align="center",
        )

    def _get_y_coordinate(self, piece_type):
        non_pawn_y_coord = int((self._image_height - self._pawn_height) / 2)
        offset = self._non_pawn_height - self._pawn_height
        if piece_type != c.PieceType.pawn:
            return non_pawn_y_coord
        else:
            return non_pawn_y_coord + offset

    @staticmethod
    def _get_piece_image_path(piece_type, color):
        piece_name = f'{piece_type.name}_{c.IMAGE.SMALL_PIECE_STR}'
        color_name = color.name
        piece_images = getattr(c.IMAGE.PIECE_IMAGE, piece_name)
        image_name = getattr(piece_images, color_name)
        image_path = os.path.join(c.IMAGE.IMAGE_DIR, image_name)

        error_msg = f'Image path {image_path} does not exist!'
        assert(os.path.exists(image_path)), error_msg
        return image_path

    def _load_image(self, image_path):
        if image_path not in self._image_store:
            image = Image.open(image_path)
            self._image_store[image_path] = image

        return self._image_store[image_path]
