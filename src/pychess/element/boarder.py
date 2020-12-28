import itertools
import random


from .. import constant as c
from ..core.mover import Move
from .squarer import Square
from .piecer import Piece


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

    @property
    def pawn_two_square_dst(self):
        return self._pawn_two_square_dst

    @pawn_two_square_dst.setter
    def pawn_two_square_dst(self, val):
        self._pawn_two_square_dst = val

    def move_hint(self, square):
        if self.is_empty(square):
            return []

        piece = self.get_piece(square)
        mult = 1
        move_paths = list(piece.move_paths)
        if piece.type == c.PieceType.pawn:
            if square.y == piece.first_row:
                move_paths.append(((0, 2),))

            if piece.color == c.Color.black:
                mult = -1

        possible_dst = []
        for pth in move_paths:
            # Filter outside 0 and 7 range
            pth = list(
                filter(
                    lambda x:  (
                        0 <= square.x + x[0] <= 7 and
                        0 <= square.y + (mult * x[1]) <= 7
                    ),
                    pth,
                )
            )

            for x_i, y_i in pth:
                s = Square((square.x + x_i, square.y + (mult * y_i)))
                if self.is_empty(s):
                    if piece.type == c.PieceType.pawn and x_i != 0:
                        pass
                    else:
                        possible_dst.append((s, None))
                else:
                    # Add hint for opponent's piece as it can be captured
                    hit_piece = self.get_piece(s)
                    if hit_piece.color != piece.color:
                        if piece.type == c.PieceType.pawn and x_i == 0:
                            pass
                        else:
                            possible_dst.append((s, hit_piece))
                    break

        return possible_dst

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

    def move(self, src, dst):
        piece_to_move = self.clear_square(src)
        if Move.is_en_passant(piece_to_move, self, src, dst):
            direction = 1 if piece_to_move.color == c.Color.black else -1
            capture_sqr = Square(
                (
                    dst.x,
                    dst.y + (direction * 1),
                )
            )
            captured_piece = self.clear_square(capture_sqr)
        else:
            captured_piece = self.clear_square(dst)

        self.add_piece(piece_to_move, dst)
        self._update_pawn_two_square_dst(piece_to_move, src, dst)
        return captured_piece

    def promote(self, promoted_piece, dst):
        self.clear_square(dst)
        self.add_piece(promoted_piece, dst)

    def castle(self, player, is_short_castle):
        king_src_x = 'e'
        king_dst_x = None
        rook_src_x = None
        rook_dst_x = None

        if is_short_castle:
            king_dst_x = 'g'
            rook_src_x = 'h'
            rook_dst_x = 'f'
        else:
            king_dst_x = 'c'
            rook_src_x = 'a'
            rook_dst_x = 'd'

        rank = '1' if player == c.Color.white else '8'

        # Move rook
        rook_src = Square(f'{rook_src_x}{rank}')
        rook_dst = Square(f'{rook_dst_x}{rank}')
        self.move(rook_src, rook_dst)

        # Move king
        king_src = Square(f'{king_src_x}{rank}')
        king_dst = Square(f'{king_dst_x}{rank}')
        self.move(king_src, king_dst)

        return king_src, king_dst

    def is_empty(self, square):
        return self.data[square] is None

    def clear(self):
        self._clear()

    def reset(self):
        self._pawn_two_square_dst = None
        self._clear()
        self._set_pieces()

    def set_pieces(self, is_standard):
        self._set_pieces(is_standard=is_standard)

    def _update_pawn_two_square_dst(self, moved_piece, src, dst):
        if moved_piece.type != c.PieceType.pawn or abs(dst.y - src.y) != 2:
            self._pawn_two_square_dst = None
        else:
            self._pawn_two_square_dst = dst

    def _clear(self):
        self._data = dict(
            [
                (Square(t), None)
                for t in itertools.product(range(8), range(8))
            ]
        )

        self.reverse = {}

    def _set_pieces(self, is_standard=True):
        order = list(range(8))
        if not is_standard:
            order = self._chess_960_order()

        self._set_color_pieces(color=c.Color.white, order=order)
        self._set_color_pieces(color=c.Color.black, order=order)

    def _chess_960_order(self):
        """
        The order is following
        [
            _, # index 0 : file for the rook 0
            _, # index 1 : file for the knight 0
            _, # index 2 : file for bishop 0
            _, # index 3 : file for queen
            _, # index 4 : file for king
            _, # index 5 : file for bishop 1
            _, # index 6 : file for knight 1
            _, # index 7 : file for rook 1
        ]
        """
        orders = {}

        remaining_files = list(range(8))

        # Place the king on any square except 'a'(0) and 'h'(7) file
        kings_file = random.randint(1, 6)
        orders[4] = kings_file
        remaining_files.remove(kings_file)

        # Place the rooks on either side of the king
        rook_0_file = random.choice(remaining_files)
        orders[0] = rook_0_file
        remaining_files.remove(rook_0_file)

        rook_1_file_choices = []
        for file_ in remaining_files:
            if rook_0_file > kings_file:
                if file_ < kings_file:
                    rook_1_file_choices.append(file_)
            else:
                if file_ > kings_file:
                    rook_1_file_choices.append(file_)

        rook_1_file = random.choice(rook_1_file_choices)
        orders[7] = rook_1_file
        remaining_files.remove(rook_1_file)

        # Place the bishops on opposite colors
        bishop_0_file = random.choice(remaining_files)
        orders[2] = bishop_0_file
        remaining_files.remove(bishop_0_file)

        # Next bishop should be on opposite color square. We just have to
        # make sure that the next bishop is on odd numbered file if the
        # first bishop is on the even numbered file else opposite
        is_even = not(bishop_0_file % 2)
        bishop_1_possible_files = [
            file_
            for file_ in remaining_files
            if file_ % 2 == is_even
        ]
        bishop_1_file = random.choice(bishop_1_possible_files)
        orders[5] = bishop_1_file
        remaining_files.remove(bishop_1_file)

        # Place the rest of the pieces
        random.shuffle(remaining_files)
        orders[1] = remaining_files.pop()
        orders[3] = remaining_files.pop()
        orders[6] = remaining_files.pop()

        return [
            orders[i]
            for i in range(8)
        ]

    def _set_color_pieces(self, color, order):
        row_1 = 0
        row_2 = 1
        if color == c.Color.black:
            row_1 = 7
            row_2 = 6

        self._data[Square((order[0], row_1))] = Piece(
            c.PieceType.rook,
            color,
            0,
        )

        self._data[Square((order[1], row_1))] = Piece(
            c.PieceType.knight,
            color,
            0,
        )

        self._data[Square((order[2], row_1))] = Piece(
            c.PieceType.bishop,
            color,
            0,
        )

        self._data[Square((order[3], row_1))] = Piece(
            c.PieceType.queen,
            color,
            0,
        )

        self._data[Square((order[4], row_1))] = Piece(
            c.PieceType.king,
            color,
            0,
        )

        self._data[Square((order[5], row_1))] = Piece(
            c.PieceType.bishop,
            color,
            1,
        )

        self._data[Square((order[6], row_1))] = Piece(
            c.PieceType.knight,
            color,
            1,
        )

        self._data[Square((order[7], row_1))] = Piece(
            c.PieceType.rook,
            color,
            1,
        )

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
