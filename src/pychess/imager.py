import os


from PIL import Image, ImageQt


from . import constant as c


class BoardImage:
    def __init__(self, board):
        self._board = board
        self.init()

    @property
    def board(self):
        return self._board()

    @property
    def qt_image(self):
        return ImageQt.ImageQt(self._board_image)

    @property
    def image(self):
        return self._board_image

    @image.setter
    def image(self, val):
        self._board_image = val

    @property
    def width(self):
        return self._board_image.width

    @property
    def height(self):
        return self._board_image.height

    def init(self):
        self._board_image = Image.new(
            'RGBA',
            (c.IMAGE_WIDTH, c.IMAGE_HEIGHT),
            color=(0, 0, 0),
        )
        board_image = Image.open(c.BOARD_IMAGE_FILE_PATH)
        self._board_image.paste(board_image, (0, 0))

        self.update()

    def update(self):
        self._draw_pieces()

    def show(self, x_res=900, y_res=900):
        image = self._board_image.resize((x_res, y_res))
        image.show()

    def _draw_pieces(self):
        for piece in self._board.pieces:
            image_path = self._get_piece_image_path(piece)
            piece_image = Image.open(image_path)
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
        piece_images = getattr(c.PIECE_IMAGE, piece_name)
        image_name = getattr(piece_images, color_name)
        image_path = os.path.join(c.IMAGE_DIR, image_name)

        error_msg = f'Image path {image_path} does not exist!'
        assert(os.path.exists(image_path)), error_msg
        return image_path

    def _get_coordinates(self, piece):
        square = self._board.get_square(piece)
        row, column = square.x, square.y

        piece_image_size = (
            c.PAWN_IMAGE_SIZE
            if piece.type == c.PieceType.pawn
            else c.NON_PAWN_IMAGE_SIZE
        )

        return (
            self._get_coordinate(piece_image_size, row),
            self._get_coordinate(piece_image_size, column, reverse=True),
        )

    def _get_coordinate(self, image_size, row_or_column, reverse=False):
        position = row_or_column
        if reverse:
            position = c.SQAURES_IN_A_ROW - 1 - row_or_column

        base_offset = c.SQUARE_SIZE * position
        image_offset = int((c.SQUARE_SIZE - image_size) / 2)

        return c.BORDER_SIZE + base_offset + image_offset
