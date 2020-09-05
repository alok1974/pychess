import os


from PIL import Image, ImageQt


from . import constant as c


class BoardImage:
    def __init__(self, board, size=c.IMAGE.DEFAULT_SIZE):
        self.init(board=board, size=size)

    @property
    def board(self):
        return self._board()

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
        self._board_image.paste(self._base_image, (0, 0))
        self._draw_pieces()

    def show(self):
        self._board_image.show()

    def _init_board_image(self):
        self._base_image = self._load_image(c.IMAGE.BOARD_IMAGE_FILE_PATH)
        self._board_image = Image.new(
            'RGBA',
            self._base_image.size,
            color=(0, 0, 0),
        )

    def _draw_pieces(self):
        for piece in self._board.pieces:
            image_path = self._get_piece_image_path(piece)
            piece_image = self._load_image(image_path)
            piece_image.load()  # needed for alpha comp
            x, y = self._get_coordinates(piece)
            self._board_image.paste(
                piece_image,
                (x, y),
                mask=piece_image.split()[3],  # needed for alpha tranparency
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
        image = Image.open(image_path)
        return image.resize(
            (
                int(image.width * self._resize_factor),
                int(image.height * self._resize_factor),
            )
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
