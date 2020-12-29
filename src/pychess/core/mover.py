from .. import constant as c
from ..element.squarer import Square
from ..element.piecer import Piece


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

    @classmethod
    def is_board_move_legal(cls, board, src, dst, piece=None, check_dst=True):
        piece = piece or board.get_piece(src)
        move = cls(piece, src, dst)

        # Case I: No piece to move
        if piece is None:
            return False

        # Case II: Illegal move for piece
        if not move.is_legal:
            return False

        # Case II(a): King cannot move to a sqaure already threatened
        # by another king
        if piece.type == c.PieceType.king:
            opposing_color = (
                c.Color.black
                if piece.color == c.Color.white
                else c.Color.white
            )
            opposing_king = Piece(c.PieceType.king, opposing_color)
            opposing_king_square = board.get_square(opposing_king)
            is_destination_attacked = (
                abs(dst.x - opposing_king_square.x) <= 1 and
                abs(dst.y - opposing_king_square.y) <= 1
            )
            if is_destination_attacked:
                return False

        # Case II (b): A king cannot capture another king
        dst_piece = board.get_piece(dst)
        if dst_piece is not None:
            src_is_king = piece.type == c.PieceType.king
            dst_is_king = dst_piece.type == c.PieceType.king
            if src_is_king and dst_is_king:
                return False

        # Case III: Destination has piece of same color
        if cls._is_same_color(piece, board, dst, check_dst):
            return False

        # Case IV: Check pawn move for special cases like
        # diagonal capture, first row moves and enpassant
        if cls._illegal_pawn_move(piece, board, move):
            return False

        # Case V: Path to destination is not empty
        if cls._illegal_spanning_move(piece, board, move):
            return False

        return True

    @staticmethod
    def _is_same_color(piece, board, dst, check_dst):
        dst_piece = board.get_piece(dst)
        if dst_piece is not None:
            if piece.color == dst_piece.color:
                if check_dst:
                    return True
        return False

    @staticmethod
    def _illegal_spanning_move(piece, board, move):
        spanning_piece = [
            c.PieceType.queen,
            c.PieceType.rook,
            c.PieceType.bishop,
        ]
        if piece.type not in spanning_piece:
            return False

        in_between_squares = move.path[1:-1]
        if not all([board.is_empty(s) for s in in_between_squares]):
            return True
        return False

    @classmethod
    def _illegal_pawn_move(cls, piece, board, move):
        if cls.is_en_passant(piece, board, move.src, move.dst):
            return False

        if piece.type != c.PieceType.pawn:
            return False

        src = move.src
        dst = move.dst
        dst_piece = board.get_piece(dst)

        if move.is_orthogonal:
            if dst_piece is not None:
                return True
            elif abs(dst.y - src.y) == 2:
                # Case where the pawn is making the first row move
                # but there is another pawn in front
                direction = int((dst.y - src.y) / abs(dst.y - src.y))
                mid_square = Square((src.x, src.y + (1 * direction)))
                if not board.is_empty(mid_square):
                    return True
        elif move.is_diagonal:
            if dst_piece is None:
                return True

        return False

    @classmethod
    def is_en_passant(cls, piece, board, src, dst):
        if piece.type != c.PieceType.pawn:
            return False
        elif not cls(piece, src, dst).is_diagonal:
            return False
        elif not board.is_empty(dst):
            return False
        elif board.pawn_two_square_dst is None:
            return False
        elif board.pawn_two_square_dst.x != dst.x:
            return False
        else:
            direction = 1 if piece.color == c.Color.white else -1
            if board.pawn_two_square_dst.y + (direction * 1) != dst.y:
                return False

        return True

    def _legal_move(self, piece):
        x = self.dst.x - self.src.x
        y = self.dst.y - self.src.y
        legal_coords = [c for pth in piece.move_paths for c in pth]
        if piece.type == c.PieceType.pawn:
            if self.src.y == piece.first_row:
                legal_coords.append((0, 2))

            if piece.color == c.Color.black:
                y = -1 * y

        return (x, y) in legal_coords

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
