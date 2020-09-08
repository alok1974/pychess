import itertools


from .squarer import Square
from .piecer import Piece
from . import constant as c


class Board:
    def __init__(self):
        self._data = None
        self._reverse = None
        self.reset()

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, val):
        self._data = val

    @property
    def reverse(self):
        return self._reverse

    @reverse.setter
    def reverse(self, val):
        self._reverse = val

    @property
    def pieces(self):
        return list(self.reverse.keys())

    @property
    def squares(self):
        return list(self.data.keys())

    def get_piece(self, square):
        return self.data[square]

    def add_piece(self, piece, square):
        if piece is None:
            return

        if piece in self.reverse.keys():
            square = self.get_square(piece)
            error_msg = (
                f'The piece {piece} already exists on the board at {square} '
                'cannot add it again!'
            )
            raise RuntimeError(error_msg)
        self.data[square] = piece
        self.reverse[piece] = square

    def get_square(self, piece):
        self._validate_piece(piece)
        return self._reverse[piece]

    def clear_square(self, square):
        existing_piece = self.data[square]
        self.data[square] = None

        if existing_piece is not None:
            self.reverse.pop(existing_piece)

        return existing_piece

    def is_empty(self, square):
        return self.data[square] is None

    def clear(self):
        self._clear_board()

    def reset(self):
        self._clear_board()
        self._set_board()

    def _clear_board(self):
        self._data = dict(
            [
                (Square(t), None)
                for t in itertools.product(range(8), range(8))
            ]
        )

        self.reverse = {}

    def _set_board(self):
        self._set_color_pieces(color=c.Color.white)
        self._set_color_pieces(color=c.Color.black)

    def _set_color_pieces(self, color):
        row_1 = 0
        row_2 = 1
        if color == c.Color.black:
            row_1 = 7
            row_2 = 6

        self._data[Square((0, row_1))] = Piece(c.PieceType.rook, color, 0)
        self._data[Square((1, row_1))] = Piece(c.PieceType.knight, color, 0)
        self._data[Square((2, row_1))] = Piece(c.PieceType.bishop, color, 0)
        self._data[Square((3, row_1))] = Piece(c.PieceType.queen, color, 0)
        self._data[Square((4, row_1))] = Piece(c.PieceType.king, color, 0)
        self._data[Square((5, row_1))] = Piece(c.PieceType.bishop, color, 1)
        self._data[Square((6, row_1))] = Piece(c.PieceType.knight, color, 1)
        self._data[Square((7, row_1))] = Piece(c.PieceType.rook, color, 1)

        for i in range(8):
            self._data[Square((i, row_2))] = Piece(c.PieceType.pawn, color, i)

        self.reverse.update(
            {v: k for k, v in self._data.items() if v is not None}
        )

    def _validate_piece(self, piece):
        if piece not in self.reverse:
            error_msg = f'The piece {piece} is not found on board'
            raise RuntimeError(error_msg)

    def __repr__(self):
        """
        Will produce an output like this

           a b c d e f g h
        8 |_|#|_|#|_|#|_|#| 8
        7 |#|_|#|_|#|_|#|_| 7
        6 |_|#|_|#|_|#|_|#| 6
        5 |#|_|#|_|#|_|#|_| 5
        4 |_|#|_|#|_|#|_|#| 4
        3 |#|_|#|_|#|_|#|_| 3
        2 |_|#|_|#|_|#|_|#| 2
        1 |#|_|#|_|#|_|#|_| 1
           a b c d e f g h
        """
        header_footer = '    a b c d e f g h'
        out = []
        out.append(header_footer)
        for y in reversed(range(8)):
            line_data = []
            for x in range(8):
                filler = '#' if (x + y) % 2 == 0 else '_'
                piece = self.data[Square((x, y))]
                if piece is None:
                    line_data.append(filler)
                else:
                    piece_code = piece.code
                    if piece.color == c.Color.white:
                        piece_code = piece_code.upper()
                    line_data.append(piece_code)

            line_string_inner = '|'.join(line_data)
            line_string = f'|{line_string_inner}|'
            line = f' {y + 1} {line_string} {y + 1}'
            out.append(line)

        out.append(header_footer)
        return '\n'.join(out)
