from . import constant as c
from .squarer import Square
from .piecer import Piece


class Move:
    degrees = True

    def __init__(self, piece, src, dst):
        self._validate(piece, src, dst)
        self._piece = piece
        self._src = src
        self._dst = dst

    @property
    def is_legal(self):
        if self._is_trying_castling():
            return self._is_legal_castling()

        return self._legal_move(self._piece)

        # return self._is_distance_legal() and self._is_direction_legal()

    @property
    def is_valid_castling(self):
        return self._is_trying_castling() and self._is_legal_castling()

    @property
    def is_diagonal(self):
        x = self.dst.x - self.src.x
        y = self.dst.y - self.src.y
        return abs(x) == abs(y)

    @property
    def is_orthogonal(self):
        x = self.dst.x - self.src.x
        y = self.dst.y - self.src.y
        return (x == 0 and y != 0) or (x != 0 and y == 0)

    @property
    def piece(self):
        return self._piece

    @property
    def src(self):
        return self._src

    @property
    def dst(self):
        return self._dst

    def _legal_move(self, piece):
        x = self.dst.x - self.src.x
        y = self.dst.y - self.src.y
        if piece.type == c.PieceType.pawn:
            first_row_pawn = self.src.y == 1
            if piece.color == c.Color.black:
                y = -1 * y
                first_row_pawn = self.src.y == 6
            return (
                (x in [-1, 0, 1] and y == 1) or
                (first_row_pawn and x == 0 and y == 2)
            )
        elif piece.type == c.PieceType.rook:
            return (x == 0 and y != 0) or (x != 0 and y == 0)
        elif piece.type == c.PieceType.bishop:
            return abs(x) == abs(y)
        elif piece.type == c.PieceType.knight:
            return (x, y) in [
                (1, 2), (1, -2), (-1, 2), (-1, -2),
                (2, 1), (2, -1), (-2, 1), (-2, -1),
            ]
        elif piece.type == c.PieceType.queen:
            return (
                (x == 0 and y != 0) or (x != 0 and y == 0) or
                (abs(x) == abs(y))
            )
        elif piece.type == c.PieceType.king:
            return (x, y) in [
                (0, 1), (1, 1), (1, 0), (1, -1),
                (0, -1), (-1, -1), (-1, 0), (-1, 1),
            ]
        else:
            error_msg = (f'Unknown piece type {piece.type}')
            raise ValueError(error_msg)

    @property
    def path(self):
        if not self.is_legal:
            return []

        piece_types = [c.PieceType.queen, c.PieceType.rook, c.PieceType.bishop]
        if self.piece.type not in piece_types:
            return [self.src, self.dst]

        x = self.dst.x - self.src.x
        y = self.dst.y - self.src.y

        coords = []
        x_incr = None
        y_incr = None
        span = None
        if y == 0 and x > 0:
            x_incr = 1
            y_incr = 0
            span = self.dst.x - self.src.x
        elif x > 0 and y > 0:
            x_incr = 1
            y_incr = 1
            span = self.dst.x - self.src.x
        elif x == 0 and y > 0:
            x_incr = 0
            y_incr = 1
            span = self.dst.y - self.src.y
        elif x < 0 and y > 0:
            x_incr = -1
            y_incr = 1
            span = self.src.x - self.dst.x
        elif x < 0 and y == 0:
            x_incr = -1
            y_incr = 0
            span = self.src.x - self.dst.x
        elif x < 0 and y < 0:
            x_incr = -1
            y_incr = -1
            span = self.src.x - self.dst.x
        elif x == 0 and y < 0:
            x_incr = 0
            y_incr = -1
            span = self.src.y - self.dst.y
        elif x > 0 and y < 0:
            x_incr = 1
            y_incr = -1
            span = self.dst.x - self.src.x
        else:
            error_msg = (
                f'Unknown span: src=({self.src.x}, {self.src.y}), '
                f'dst=({self.dst.x}, {self.dst.y}), (x, y)=({x}, {y})'
                f'move: {self}'
            )
            raise ValueError(error_msg)

        coords = [
            Square(
                (
                    self.src.x + (s * x_incr),
                    self.src.y + (s * y_incr),
                ),
            )
            for s in range(1, span)
        ]

        if span:
            coords.append(self.dst)
            coords.insert(0, self.src)

        return coords

    def _validate(self, piece, src, dst):
        if not isinstance(piece, Piece):
            error_msg = (
                f'Piece {piece} is not of type {str(Piece)}'
            )
            raise ValueError(error_msg)

        if not isinstance(src, Square) or not isinstance(dst, Square):
            error_msg = (
                f'src {src} and {dst} need to be of type {str(Square)}'
            )
            raise ValueError(error_msg)

    def _is_trying_castling(self):
        return (
            abs(self.dst.x - self.src.x) == c.GAME.KING_CASTLE_DISTANCE and
            self.piece.type == c.PieceType.king
        )

    def _is_legal_castling(self):
        if self.piece.type != c.PieceType.king:
            error_msg = 'Castling can be checked for king only!'
            raise ValueError(error_msg)

        start_src = Square('e1')
        possible_dst = [
            Square('g1'),  # Case: short castle
            Square('c1'),  # Case: long castle
        ]
        if self.piece.color == c.Color.black:
            start_src = Square('e8')
            possible_dst = [
                Square('g8'),  # Case: short castle
                Square('c8')  # Case: long castle
            ]

        return (
            self.src == start_src and
            self.dst in possible_dst
        )

    def __repr__(self):
        return (
            '<'
            f'{self.__class__.__name__}'
            ': '
            f'{self.piece.code}'
            f'{self.piece.order}'
            f'({self.piece.color_code}) '
            f'{self.src.address}'
            f' - '
            f'{self.dst.address}'
            '>'
        )

    def __eq__(self, other):
        return (
            self.piece == other.piece and
            self.src == other.src and
            self.dst == other.dst
        )

    def __neq__(self, other):
        return (
            self.piece != other.piece or
            self.src != other.src or
            self.dst != other.dst
        )
