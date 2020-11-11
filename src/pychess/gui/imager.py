import os
import collections


from PIL import Image, ImageQt, ImageDraw, ImageFont


from .. import constant as c
from ..element.squarer import Square


class BoardImage:
    COLOR_MOVE_HINT_CAPTURE = (255, 42, 14)
    COLOR_MOVE_HINT_EMPTY = (127, 127, 127)

    def __init__(self, board, size=c.IMAGE.DEFAULT_SIZE):
        self._image_store = {}
        self.init(board=board, size=size)

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

    def handle_pause_screen(self, is_paused):
        if is_paused:
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
            size=int(c.IMAGE.MOVIE_FONT_SIZE * self._resize_factor),
        )
        ctx = ImageDraw.Draw(image)
        ctx.multiline_text(
            (int(self.width * 0.05), self.height + 5),
            move_text,
            fill=(255, 255, 255),
            font=font,
        )
        image.save(save_to_path)

    def init(self, board, size=c.IMAGE.DEFAULT_SIZE):
        self._board = board
        self._threatened_squares = []
        self._selected_square = None
        self.resize(size=size)
        self.update()

    def resize(self, size=c.IMAGE.DEFAULT_SIZE):
        if size not in c.IMAGE.SUPPORTED_SIZE:
            error_msg = (
                f'Unable to resize image - invalid size {size}, '
                f'supported sizes are {c.IMAGE.SUPPORTED_SIZE}'
            )
            raise RuntimeError(error_msg)

        self._resize_factor = float(size / c.IMAGE.BASE_IMAGE_SIZE)
        self._square_size = int(c.IMAGE.SQUARE_SIZE * self._resize_factor)
        self._border_size = int(c.IMAGE.BORDER_SIZE * self._resize_factor)
        self._non_pawn_image_size = int(
            c.IMAGE.NON_PAWN_IMAGE_SIZE * self._resize_factor
        )
        self._pawn_image_size = int(
            c.IMAGE.PAWN_IMAGE_SIZE * self._resize_factor
        )
        self._init_board_image()

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
        self._pause_image = self._load_image(c.IMAGE.PAUSE_IMAGE_FILE_PATH)

    def _draw_pieces(self):
        for piece in self._board.pieces:
            self._draw_piece(piece)

    def _draw_piece(self, piece):
        if piece is None:
            return
        image_path = self._get_piece_image_path(piece)
        piece_image = self._load_image(image_path)
        x, y = self._get_coordinates(piece)
        self._board_image.alpha_composite(
            piece_image,
            (x, y),
        )

    def _get_coordinates(self, piece):
        square = self._board.get_square(piece)
        row, column = square.x, square.y

        piece_image_size = (
            self._pawn_image_size
            if piece.type == c.PieceType.pawn
            else self._non_pawn_image_size
        )

        return (
            self._get_coordinate(piece_image_size, row),
            self._get_coordinate(piece_image_size, column, reverse=True),
        )

    def _get_coordinate(self, image_size, row_or_column, reverse=False):
        position = row_or_column
        if reverse:
            position = c.IMAGE.NB_SQUARES - 1 - row_or_column

        base_offset = self._square_size * position
        image_offset = int((self._square_size - image_size) / 2)

        return self._border_size + base_offset + image_offset

    def _load_image(self, image_path):
        size = int(self._resize_factor * c.IMAGE.DEFAULT_SIZE)
        if (image_path, size) not in self._image_store:
            image = Image.open(image_path)
            image = self._resize_image(image)
            self._image_store[(image_path, size)] = image

        return self._image_store[(image_path, size)]

    def _resize_image(self, image):
        if self._resize_factor == float(1):
            return image

        return image.resize(
            (
                int(image.width * self._resize_factor),
                int(image.height * self._resize_factor),
            ),
            resample=Image.LANCZOS,
        )

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
        pixel_on_border = self._pixel_on_border(
            square_size=self._square_size,
            nb_squares=c.IMAGE.NB_SQUARES,
            border_size=self._border_size,
            x=x,
            y=y,
        )

        if pixel_on_border:
            return

        square_x = int((x - self._border_size) / self._square_size)
        square_y = c.IMAGE.NB_SQUARES - 1 - int(
            (y - self._border_size) / self._square_size
        )
        return Square((square_x, square_y))

    def square_to_pixel(self, square):
        x = (square.x * self._square_size) + self._border_size

        reverse_y_coordinate = c.IMAGE.NB_SQUARES - 1 - square.y
        y = (reverse_y_coordinate * self._square_size) + self._border_size

        return x, y

    @staticmethod
    def _pixel_on_border(square_size, nb_squares, border_size, x, y):
        return (
            (x - border_size) < 0 or
            (y - border_size) < 0 or
            (x > (border_size + (nb_squares * square_size))) or
            (y > (border_size + (nb_squares * square_size)))
        )


class CapturedImage:
    def __init__(self, size=c.IMAGE.DEFAULT_SIZE):
        self._image_store = {}
        self.init(size=size)

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

    def init(self, size=c.IMAGE.DEFAULT_SIZE):
        self._resize_factor = int(size / c.IMAGE.DEFAULT_SIZE)

        self._image_width = int(
            c.IMAGE.CAPTURABLES_IMAGE_WIDTH * self._resize_factor
        )

        self._image_height = int(
            c.APP.LCD_HEIGHT * self._resize_factor
        )

        self._pawn_height = int(
            c.IMAGE.PAWN_SMALL_IMAGE_SIZE * self._resize_factor
        )

        self._non_pawn_height = int(
            c.IMAGE.NON_PAWN_SMALL_IMAGE_SIZE * self._resize_factor
        )

        self._lead_font_size = int(
            c.IMAGE.LEAD_FONT_SIZE * self._resize_factor
        )

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
        size = int(self._resize_factor * c.IMAGE.DEFAULT_SIZE)
        if (image_path, size) not in self._image_store:
            image = Image.open(image_path)
            image = self._resize_image(image)
            self._image_store[(image_path, size)] = image

        return self._image_store[(image_path, size)]

    def _resize_image(self, image):
        if self._resize_factor == float(1):
            return image

        return image.resize(
            (
                int(image.width * self._resize_factor),
                int(image.height * self._resize_factor),
            ),
            resample=Image.LANCZOS,
        )
