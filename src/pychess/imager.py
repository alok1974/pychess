import os


from PIL import Image, ImageQt


from . import constant as c
from .piecer import generate_pieces, get_piece_row_place


class BoardImage:
    def __init__(self, board):
        self.init_image(board=board)

    @property
    def qt_image(self):
        return ImageQt.ImageQt(self._board_image)

    @property
    def board(self):
        return self._board

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

    def init_image(self, board):
        self._board = board
        self._board_image = Image.new(
            'RGBA',
            (c.IMAGE_WIDTH, c.IMAGE_HEIGHT),
            color=(0, 0, 0),
        )
        board_image = Image.open(c.BOARD_IMAGE_FILE_PATH)
        self._board_image.paste(board_image, (0, 0))
        self._set_pieces()

    def show(self):
        self._board_image.show()

    def _set_pieces(self):
        for piece in generate_pieces():
            image_path = self._get_piece_image_path(piece)
            piece_image = Image.open(image_path)
            piece_image.load()  # needed for alpha comp
            x, y = self._get_piece_coord(piece)
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

    def _get_piece_coord(self, piece):
        row = self._get_piece_row(piece)
        place = get_piece_row_place(piece)
        piece_image_size = (
            c.PAWN_IMAGE_SIZE
            if piece.type == c.PieceType.pawn
            else c.NON_PAWN_IMAGE_SIZE
        )

        x = int(
            c.BORDER_SIZE + (c.SQUARE_SIZE * place) +
            ((c.SQUARE_SIZE - piece_image_size) / 2)
        )

        y = int(
            c.BORDER_SIZE + (c.SQUARE_SIZE * (c.SQAURES_IN_A_ROW - 1 - row)) +
            ((c.SQUARE_SIZE - piece_image_size) / 2)
        )
        return x, y

    def _get_piece_row(self, piece):
        row = None
        if piece.color == c.Color.black:
            row = 6 if piece.type == c.PieceType.pawn else 7
        elif piece.color == c.Color.white:
            row = 1 if piece.type == c.PieceType.pawn else 0
        else:
            error_msg = (f'Undefined color {piece.color}!')
            raise ValueError(error_msg)

        return row
