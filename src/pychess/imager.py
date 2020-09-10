import os


from PIL import Image, ImageQt


from . import constant as c
from .squarer import Square


class BoardImage:
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

    def init(self, board, size=c.IMAGE.DEFAULT_SIZE):
        self._board = board
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

    def highlight(self, square, highlight_color):
        x, y = self.square_to_pixel(square)
        size = (self._square_size, self._square_size)
        highlight_image = Image.new('RGBA', size, color=highlight_color)
        self._board_image.alpha_composite(highlight_image, (x, y))
        self._draw_piece(self.board.get_piece(square))

    def remove_highlight(self, square):
        if square is None:
            return

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
        if image_path not in self._image_store:
            image = Image.open(image_path)
            image = image.resize(
                (
                    int(image.width * self._resize_factor),
                    int(image.height * self._resize_factor),
                ),
                resample=Image.LANCZOS,
            )
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
