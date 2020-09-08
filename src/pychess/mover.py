import math
# import decimal

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

        return self._is_distance_legal() and self._is_direction_legal()

    @property
    def is_diagonal(self):
        return self.angle in [
            math.radians(45.0),
            math.radians(135.0),
            math.radians(-135.0),
            math.radians(-45.0),
        ]

    @property
    def is_orthogonal(self):
        return self.angle in [
            math.radians(0.0),
            math.radians(90.0),
            math.radians(180.0),
            math.radians(-90.0),
        ]

    @property
    def piece(self):
        return self._piece

    @property
    def src(self):
        return self._src

    @property
    def dst(self):
        return self._dst

    @property
    def distance(self):
        return math.sqrt(
            (self.dst.x - self.src.x) ** 2 +
            (self.dst.y - self.src.y) ** 2
        )

    @property
    def angle(self):
        x, y = self.dst.x - self.src.x, self.dst.y - self.src.y

        # Reverse directions for black pawn
        is_pawn = self.piece.type == c.PieceType.pawn
        is_black = self.piece.color == c.Color.black
        if is_pawn and is_black:
            y = -1 * y

        return math.atan2(y, x)

    @property
    def direction(self):
        if self.angle == 0.0:
            return c.Direction.e
        elif 0.0 < self.angle < math.radians(45.0):
            return c.Direction.ene
        elif self.angle == math.radians(45.0):
            return c.Direction.ne
        elif math.radians(45.0) < self.angle < math.radians(90.0):
            return c.Direction.nne
        elif self.angle == math.radians(90.0):
            return c.Direction.n
        elif math.radians(90.0) < self.angle < math.radians(135.0):
            return c.Direction.nnw
        elif self.angle == math.radians(135.0):
            return c.Direction.nw
        elif math.radians(135.0) < self.angle < math.radians(180.0):
            return c.Direction.wnw
        elif self.angle == math.radians(180.0):
            return c.Direction.w
        elif math.radians(-180.0) < self.angle < math.radians(-135.0):
            return c.Direction.wsw
        elif self.angle == math.radians(-135.0):
            return c.Direction.sw
        elif math.radians(-135.0) < self.angle < math.radians(-90.0):
            return c.Direction.ssw
        elif self.angle == math.radians(-90.0):
            return c.Direction.s
        elif math.radians(-90.0) < self.angle < math.radians(-45.0):
            return c.Direction.sse
        elif self.angle == math.radians(-45.0):
            return c.Direction.se
        elif math.radians(-45.0) < self.angle < 0.0:
            return c.Direction.ese

    @property
    def path(self):
        if not self.is_legal:
            return []

        piece_types = [c.PieceType.queen, c.PieceType.rook, c.PieceType.bishop]
        if self.piece.type not in piece_types:
            return [self.src, self.dst]

        coords = []
        x_incr = None
        y_incr = None
        span = None
        if self.angle == 0.0:
            x_incr = 1
            y_incr = 0
            span = self.dst.x - self.src.x
        elif self.angle == math.radians(45.0):
            x_incr = 1
            y_incr = 1
            span = self.dst.x - self.src.x
        elif self.angle == math.radians(90.0):
            x_incr = 0
            y_incr = 1
            span = self.dst.y - self.src.y
        elif self.angle == math.radians(135.0):
            x_incr = -1
            y_incr = 1
            span = self.src.x - self.dst.x
        elif self.angle == math.radians(180.0):
            x_incr = -1
            y_incr = 0
            span = self.src.x - self.dst.x
        elif self.angle == math.radians(-135.0):
            x_incr = -1
            y_incr = -1
            span = self.src.x - self.dst.x
        elif self.angle == math.radians(-90.0):
            x_incr = 0
            y_incr = -1
            span = self.src.y - self.dst.y
        elif self.angle == math.radians(-45.0):
            x_incr = 1
            y_incr = -1
            span = self.dst.x - self.src.x

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

    def _is_distance_legal(self):
        if self.piece.travel_distance == [0]:
            return True

        if self.piece.type == c.PieceType.pawn:  # Case: pawn first move
            first_row = 1
            if self.piece.color == c.Color.black:
                first_row = 6

            if self.src.y == first_row:
                allowed_distance = (
                    self.piece.travel_distance +
                    [c.GAME.PAWN_FIRST_MOVE_DISTANCE]
                )
                return self.distance in allowed_distance
            else:
                return self.distance in self.piece.travel_distance
        else:
            return self.distance in self.piece.travel_distance

    def _is_direction_legal(self):
        return self.direction in self.piece.allowed_move_direction

    def _is_trying_castling(self):
        return (
            self.distance == c.GAME.KING_CASTLE_DISTANCE and
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
