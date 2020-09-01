import math
import decimal


from .constant import (
    Direction,
    PieceType,
    Color,
    PAWN_FIRST_MOVE_DISTANCE,
    KING_CASTLE_DISTANCE,
)
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
        return self.angle in [45.0, 135.0, 225.0, 315.0]

    @property
    def is_orthogonal(self):
        return self.angle in [0.0, 90.0, 180.0, 270.0]

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
        is_pawn = self.piece.type == PieceType.pawn
        is_black = self.piece.color == Color.black
        if is_pawn and is_black:
            y = -1 * y

        result = math.atan2(y, x)
        if self.degrees:
            result = decimal.Decimal(str(math.degrees(result)))
            result = result.quantize(decimal.Decimal('1.000000000000'))
            result = float(result)
            if result < 0:
                result = 360.0 + result
        return result

    @property
    def direction(self):
        if self.angle == 0:
            return Direction.e
        elif 0.0 < self.angle < 45.0:
            return Direction.ene
        elif self.angle == 45.0:
            return Direction.ne
        elif 45.0 < self.angle < 90.0:
            return Direction.nne
        elif self.angle == 90.0:
            return Direction.n
        elif 90.0 < self.angle < 135.0:
            return Direction.nnw
        elif self.angle == 135.0:
            return Direction.nw
        elif 135.0 < self.angle < 180.0:
            return Direction.wnw
        elif self.angle == 180.0:
            return Direction.w
        elif 180.0 < self.angle < 225.0:
            return Direction.wsw
        elif self.angle == 225.0:
            return Direction.sw
        elif 225.0 < self.angle < 270.0:
            return Direction.ssw
        elif self.angle == 270.0:
            return Direction.s
        elif 270.0 < self.angle < 315.0:
            return Direction.sse
        elif self.angle == 315.0:
            return Direction.se
        elif 315.0 < self.angle < 360.0:
            return Direction.ese

    @property
    def path(self):
        if not self.is_legal:
            return []

        piece_types = [PieceType.queen, PieceType.rook, PieceType.bishop]
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
        elif self.angle == 45.0:
            x_incr = 1
            y_incr = 1
            span = self.dst.x - self.src.x
        elif self.angle == 90.0:
            x_incr = 0
            y_incr = 1
            span = self.dst.y - self.src.y
        elif self.angle == 135.0:
            x_incr = -1
            y_incr = 1
            span = self.src.x - self.dst.x
        elif self.angle == 180.0:
            x_incr = -1
            y_incr = 0
            span = self.src.x - self.dst.x
        elif self.angle == 225.0:
            x_incr = -1
            y_incr = -1
            span = self.src.x - self.dst.x
        elif self.angle == 270.0:
            x_incr = 0
            y_incr = -1
            span = self.src.y - self.dst.y
        elif self.angle == 315.0:
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

        if self.piece.type == PieceType.pawn:  # Case: pawn first move
            first_row = 1
            if self.piece.color == Color.black:
                first_row = 6

            if self.src.y == first_row:
                allowed_distance = (
                    self.piece.travel_distance +
                    [PAWN_FIRST_MOVE_DISTANCE]
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
            self.distance == KING_CASTLE_DISTANCE and
            self.piece.type == PieceType.king
        )

    def _is_legal_castling(self):
        if self.piece.type != PieceType.king:
            error_msg = 'Castling can be checked for king only!'
            raise ValueError(error_msg)

        start_src = Square('e1')
        possible_dst = [
            Square('g1'),  # Case: short castle
            Square('c1'),  # Case: long castle
        ]
        if self.piece.color == Color.black:
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
