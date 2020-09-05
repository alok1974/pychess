import os


from PIL import Image, ImageQt


from . import constant as C


class BoardImage:
    def __init__(self, board):
        self.init(board=board)

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

    def init(self, board):
        self._board = board
        self._base_image = self._load_image(C.IMAGE.BOARD_IMAGE_FILE_PATH)
        self._board_image = Image.new(
            'RGBA',
            self._base_image.size,
            color=(0, 0, 0),
        )
        self._board_image.paste(self._base_image, (0, 0))

        self.update()

    def update(self, board=None):
        self._board_image.paste(self._base_image, (0, 0))
        self._draw_pieces()

    def show(self):
        self._board_image.show()

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

    def _get_piece_image_path(self, piece):
        piece_name = piece.type.name
        color_name = piece.color.name
        piece_images = getattr(C.IMAGE.PIECE_IMAGE, piece_name)
        image_name = getattr(piece_images, color_name)
        image_path = os.path.join(C.IMAGE.IMAGE_DIR, image_name)

        error_msg = f'Image path {image_path} does not exist!'
        assert(os.path.exists(image_path)), error_msg
        return image_path

    def _get_coordinates(self, piece):
        square = self._board.get_square(piece)
        row, column = square.x, square.y

        piece_image_size = (
            C.IMAGE.PAWN_IMAGE_SIZE
            if piece.type == C.PieceType.pawn
            else C.IMAGE.NON_PAWN_IMAGE_SIZE
        )

        return (
            self._get_coordinate(piece_image_size, row),
            self._get_coordinate(piece_image_size, column, reverse=True),
        )

    def _get_coordinate(self, image_size, row_or_column, reverse=False):
        position = row_or_column
        if reverse:
            position = C.IMAGE.NB_SQUARES - 1 - row_or_column

        base_offset = C.IMAGE.SQUARE_SIZE * position
        image_offset = int((C.IMAGE.SQUARE_SIZE - image_size) / 2)

        return C.IMAGE.BORDER_SIZE + base_offset + image_offset

    def _load_image(self, image_path):
        image = Image.open(image_path)
        return image.resize(
            (
                int(image.width * C.IMAGE.RESIZE_FACTOR),
                int(image.height * C.IMAGE.RESIZE_FACTOR),
            )
        )
