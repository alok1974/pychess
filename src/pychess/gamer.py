import collections
import itertools
import re
import contextlib
import copy


from .boarder import Board
from .mover import Move
from . import constant as c
from .piecer import Piece
from .squarer import Square
from .event import Signal


GAME_DATA = collections.namedtuple(
    'GAME_DATA',
    [
        'src', 'dst', 'captured_white', 'captured_black',
        'leader', 'lead', 'move_history', 'capturables'
    ]
)


class Game:
    MOVE_RESULT = collections.namedtuple(
        'MOVE_RESULT',
        ['success', 'moved_piece', 'is_castling']
    )

    MOVE_SIGNAL = Signal(GAME_DATA)
    INVALID_MOVE_SIGNAL = Signal()
    MATE_SIGNAL = Signal(c.Color)
    PLAYER_CHANGED_SIGNAL = Signal(c.Color)
    NON_STANDARD_BOARD_SET_SIGNAL = Signal()

    def __init__(self):
        self._board = Board()
        self._captured_white = []
        self._captured_black = []
        self._move_history = []
        self._capturables = {}
        self._pieces_checking_black = []
        self._pieces_checking_white = []
        self._current_player = c.Color.white
        self._next_player = c.Color.black
        self._winner = None
        self._is_game_over = False
        self._description = []

        self._black_king_moved = False
        self._black_rook_moved = False
        self._white_king_moved = False
        self._white_rook_moved = False

        self._black_promotion_piece_type = c.PieceType.queen
        self._white_promotion_piece_type = c.PieceType.queen

    @property
    def board(self):
        return self._board

    @property
    def description(self):
        return '\n'.join(self._description)

    @property
    def captured_black(self):
        return self._captured_black

    @property
    def captured_white(self):
        return self._captured_white

    @property
    def white_points(self):
        return sum([p.worth for p in self.captured_black])

    @property
    def black_points(self):
        return sum([p.worth for p in self.captured_white])

    @property
    def winner(self):
        return self._winner

    @property
    def leader(self):
        if self.black_points == self.white_points:
            return
        elif self.black_points > self.white_points:
            return c.Color.black
        else:
            return c.Color.white

    @property
    def lead(self):
        return abs(self.black_points - self.white_points)

    @property
    def pieces_checking_black(self):
        return self._pieces_checking_black

    @property
    def pieces_checking_white(self):
        return self._pieces_checking_white

    @property
    def move_history(self):
        return self._move_history

    @property
    def capturables(self):
        return self._capturables

    def set_game_options(self, options):
        if self._move_history:
            return

        (
            self._black_promotion_piece_type,
            self._white_promotion_piece_type,
            self._is_standard_type,
        ) = options

        self._board.set_pieces(self._is_standard_type)
        self.NON_STANDARD_BOARD_SET_SIGNAL.emit()

    def reset(self):
        self._board.reset()
        self._captured_white = []
        self._captured_black = []
        self._move_history = []
        self._capturables = {}
        self._pieces_checking_black = []
        self._pieces_checking_white = []
        self._current_player = c.Color.white
        self._next_player = c.Color.black
        self._winner = None
        self._is_game_over = False
        self._description = []

        self._black_king_moved = False
        self._black_rook_moved = False
        self._white_king_moved = False
        self._white_rook_moved = False

        self._black_promotion_piece_type = c.PieceType.queen
        self._white_promotion_piece_type = c.PieceType.queen

    @property
    def is_game_over(self):
        return self._is_game_over

    @staticmethod
    def parse_move_spec(move_spec):
        src = None
        dst = None
        if isinstance(move_spec, tuple):
            if len(move_spec) != 2:
                error_msg = (
                    f'{move_spec} tuple should have exactly two elements!'
                )
                raise RuntimeError(error_msg)

            both_string = all([isinstance(a, str) for a in move_spec])
            both_tuple = all([isinstance(a, tuple) for a in move_spec])
            both_squares = all([isinstance(a, Square) for a in move_spec])
            if both_string:
                for addr in move_spec:
                    mo = re.match(c.GAME.ADDRESS_PATTERN, addr)
                    if mo is None:
                        error_msg = (
                            f'Malformed address! The address {addr} supplied '
                            f'in arg `move_spec={move_spec}` should be of '
                            'the format \'<alpha><number>\' where alpha is '
                            'one of [a, b, c, d, e, f, g, h] and number '
                            'is from 1 to 8'
                        )
                        raise RuntimeError(error_msg)
                x_addr, y_addr = move_spec
                src, dst = Square(x_addr), Square(y_addr)
            elif both_tuple:
                for addr in move_spec:
                    valid_len = len(addr) == 2
                    valid_contents = all([n in range(8) for n in addr])
                    if not valid_len or not valid_contents:
                        error_msg = (
                            f'The address {addr} supplied in arg '
                            f'`move_spec={move_spec}` should exactly be a '
                            'tuple of the form (a, b) where both a and b '
                            'are one of the numbers 0 to 7'
                        )
                        raise RuntimeError(error_msg)
                x, y = move_spec
                src, dst = Square(x), Square(y)
            elif both_squares:
                src, dst = move_spec
            else:
                error_msg = (
                    f'`move_spec={move_spec}` should contain either 2 '
                    'strings or 2 tuples'
                )
                raise RuntimeError(error_msg)
        elif isinstance(move_spec, str):
            valid_len = len(move_spec) == 4
            mo = re.match(c.GAME.MOVE_PATTERN, move_spec)
            if not valid_len or mo is None:
                error_msg = (
                    f'`move_spec={move_spec}` should be of the form '
                    '<alpha1><n1><alpha2><n2>, where alpha1 and alpha2 should '
                    'one of [a, b, c, d, e, f, g, h] and n1 and n2 should be '
                    'a number between 1 to 8'
                )
                raise RuntimeError(error_msg)
            x_addr, y_addr = mo.groups()
            src, dst = Square(x_addr), Square(y_addr)
        else:
            error_msg = (
                f'`move_spec={move_spec}` should either be a tuple or a string'
            )
            raise RuntimeError(error_msg)

        if src == dst:
            error_msg = (
                f'`move_spec={move_spec}` should have distinct source and '
                'destination'
            )
            raise RuntimeError(error_msg)

        return src, dst

    def move(self, move_spec):
        if self.is_game_over:
            return

        try:
            src, dst = self.parse_move_spec(move_spec)
        except RuntimeError:
            self.INVALID_MOVE_SIGNAL.emit()
            return

        if self._not_players_turn(src, dst):
            self.INVALID_MOVE_SIGNAL.emit()
            return

        if self._move_causes_discovered_check(src, dst):
            self.INVALID_MOVE_SIGNAL.emit()
            return

        result = self._perform_move(src, dst)
        if not result.success:
            self.INVALID_MOVE_SIGNAL.emit()
            return

        self._record_move(result.moved_piece, src, dst)
        game_data = GAME_DATA(
            src=src,
            dst=dst,
            captured_white=self.captured_white,
            captured_black=self.captured_black,
            leader=self.leader,
            lead=self.lead,
            move_history=self.move_history,
            capturables=self.capturables
        )

        self.MOVE_SIGNAL.emit(game_data)

        if self._is_mate():
            self._winner = self._current_player
            self._is_game_over = True
            self.MATE_SIGNAL.emit(self._winner)
            return

        self._toggle_player()

    def _move_causes_discovered_check(self, src, dst):
        with self._try_move(src, dst):
            king = Piece(c.PieceType.king, color=self._current_player)
            if self._is_capturable(king):
                return True
            else:
                return False

    def _record_move(self, piece, src, dst):
        mv = Move(piece, src, dst)
        self._move_history.append(mv)

        if piece.type == c.PieceType.king:
            if piece.color == c.Color.black:
                self._black_king_moved = True
            else:
                self._white_king_moved = True

        if piece.type == c.PieceType.rook:
            if piece.color == c.Color.black:
                self._black_rook_moved = True
            else:
                self._white_rook_moved = True

    def _not_players_turn(self, src, dst):
        src_piece = self.board.get_piece(src)
        if src_piece is None:
            return True
        return src_piece.color != self._current_player

    def _perform_move(self, src, dst):
        castling_result = False
        is_legal = self._is_move_legal(src, dst)
        if not is_legal:
            return self.MOVE_RESULT(
                success=False,
                moved_piece=None,
                is_castling=castling_result,
            )

        piece_to_move = self.board.get_piece(src)
        if Move(piece_to_move, src, dst).is_valid_castling:
            if self._can_castle(piece_to_move, src, dst):
                castling_result = True
                rook_src = None
                rook_dst = None
                if dst.x == 6:  # short castle
                    rook_src = Square((7, src.y))
                    rook_dst = Square((5, src.y))

                if dst.x == 2:  # long castle
                    rook_src = Square((0, src.y))
                    rook_dst = Square((3, src.y))

                # Make rook move
                self._move_piece(rook_src, rook_dst)

                # Make king move
                moved_piece = self._move_piece(src, dst)
            else:
                # This was try to move the king at e1 or e8 to correct
                # castling squares but other conditions required for a legal
                # castling are not met and thus ultimately this move cannot be
                # made
                return self.MOVE_RESULT(
                    success=False,
                    moved_piece=None,
                    is_castling=castling_result,
                )
        else:
            # No castling was asked for, let us proceed with a normal move
            moved_piece = self._move_piece(src, dst)

        self._handle_promotion(moved_piece, dst)
        self._update_capturables()

        return self.MOVE_RESULT(
            success=True,
            moved_piece=moved_piece,
            is_castling=castling_result,
        )

    def _handle_promotion(self, moved_piece, dst):
        if moved_piece.type != c.PieceType.pawn:
            return

        if moved_piece.color == c.Color.white:
            last_row = 7
        else:
            last_row = 0

        if dst.y != last_row:
            return

        if moved_piece.color == c.Color.black:
            piece_type = self._black_promotion_piece_type
        else:
            piece_type = self._white_promotion_piece_type

        promoted_piece = self._create_promoted_piece(
            piece_type=piece_type,
            color=moved_piece.color,
        )

        self.board.clear_square(dst)
        self.board.add_piece(promoted_piece, dst)

    def _create_promoted_piece(self, piece_type, color):
        pieces = self._get_pieces(color)
        existing_pieces = [p for p in pieces if p.type == piece_type]
        if not existing_pieces:
            highest_order = -1
        else:
            highest_order = max([p.order for p in existing_pieces])

        return Piece(piece_type, color, highest_order + 1)

    def _move_piece(self, src, dst):
        dst_piece = self.board.clear_square(dst)
        if dst_piece is not None:
            if dst_piece.color == c.Color.black:
                self._captured_black.append(dst_piece)
            else:
                self._captured_white.append(dst_piece)

        src_piece = self.board.clear_square(src)
        self.board.add_piece(src_piece, dst)
        return src_piece

    def _can_castle(self, king, src, dst):
        if king.type != c.PieceType.king:
            return False

        prev_moves = (
            [self._black_king_moved, self._black_rook_moved]
            if king.color == c.Color.black
            else [self._white_king_moved, self._white_rook_moved]
        )

        if any(prev_moves):
            return False

        if self._is_capturable(king):
            return False

        in_betweens = self._get_castling_in_betweens(src, dst)
        if not all(map(lambda x: self.board.is_empty(x), in_betweens)):
            return False

        if self._in_betweens_under_attack(in_betweens):
            return False

        return True

    def _in_betweens_under_attack(self, in_betweens):
        src_y = in_betweens[0].y
        src_x = None
        if len(in_betweens) == 3:
            # Long castle, rook at 'a'
            src_x = 0
        elif len(in_betweens) == 2:
            # Short castle rook at 'h'
            src_x = 7

        src = Square((src_x, src_y))
        rook_for_testing = self.board.get_piece(src)
        for dst in in_betweens:
            # Skip over 'b' file as this is not needed to be checked
            # although a in between square but only squares where king
            # jumps overs should be checked
            if dst.x == 1:
                continue

            with self._try_move(src, dst):
                if self._is_capturable(rook_for_testing):
                    return True

        return False

    def _get_castling_in_betweens(self, src, dst):
        if src.x > dst.x:
            # b, c and d squares
            x_vals = [1, 2, 3]
        else:
            # f and g squares
            x_vals = [5, 6]

        return [Square((x, src.y)) for x in x_vals]

    def _toggle_player(self):
        if self._current_player == c.Color.black:
            self._current_player = c.Color.white
            self._next_player = c.Color.black
        else:
            self._current_player = c.Color.black
            self._next_player = c.Color.white

        self.PLAYER_CHANGED_SIGNAL.emit(self._current_player)

    def _is_move_legal(self, src, dst):
        piece_to_move = self.board.get_piece(src)

        # Case I: No piece to move
        if piece_to_move is None:
            return False

        # Case II: Illegal move for piece
        mv = Move(piece_to_move, src, dst)
        if not mv.is_legal:
            return False

        # Case III: Destination has piece of same color
        dst_piece = self.board.get_piece(dst)
        if dst_piece is not None:
            if piece_to_move.color == dst_piece.color:
                return False

        # Case IV: Special case for pawn as it can only capture only
        # with a diagonal move
        if piece_to_move.type == c.PieceType.pawn:
            if mv.is_orthogonal and dst_piece is not None:
                return False
            elif mv.is_diagonal and dst_piece is None:
                return False

        # Case V: Path to destination is not empty
        if piece_to_move.type in [
                c.PieceType.queen,
                c.PieceType.rook,
                c.PieceType.bishop,
        ]:
            in_between_squares = mv.path[1:-1]
            if not all([self.board.is_empty(s) for s in in_between_squares]):
                return False

        return True

    def _update_capturables(self):
        self._capturables = {
            c.Color.white: {},
            c.Color.black: {},
        }
        self._pieces_checking_black = []
        self._pieces_checking_white = []

        for color in [c.Color.white, c.Color.black]:
            threatening_color = (
                c.Color.black
                if color == c.Color.white
                else c.Color.white
            )

            threatening_pieces = self._get_pieces(threatening_color)
            threatened_pieces = self._get_pieces(color)

            for threatening_piece in threatening_pieces:
                for threatened_piece in threatened_pieces:
                    src = self.board.get_square(threatening_piece)
                    dst = self.board.get_square(threatened_piece)

                    if self._is_move_legal(src, dst):
                        self._capturables[color].setdefault(
                            threatening_piece, []
                        ).append(threatened_piece)

                        # look for checks
                        if threatened_piece.type == c.PieceType.king:
                            if threatened_piece.color == c.Color.white:
                                self._pieces_checking_white.append(
                                    threatening_piece
                                )
                            else:
                                self._pieces_checking_black.append(
                                    threatening_piece
                                )

    def _is_mate(self):
        self._description = []

        if self._current_player == c.Color.white:
            king_under_check = Piece(c.PieceType.king, c.Color.black)
            checking_pieces = self._pieces_checking_black
        else:
            king_under_check = Piece(c.PieceType.king, c.Color.white)
            checking_pieces = self._pieces_checking_white

        if len(checking_pieces) == 0:
            self._description.append(
                'No piece is checking the king and hence no mate.'
            )
            return False
        elif len(checking_pieces) == 1:
            checking_piece = checking_pieces[0]
            self._description.append(
                f'The {king_under_check} is under check by {checking_piece}'
            )
            if self._is_checking_piece_capturable(
                    checking_piece, king_under_check
            ):
                return False

            elif self._is_check_blockable(checking_piece, king_under_check):
                return False
            elif self._escape_square_exists(king_under_check):
                return False
            else:
                return True
        else:
            self._description.append(
                f'The {king_under_check} is being checked by the following - '
                f'{checking_pieces}'
            )
            return not self._escape_square_exists(king_under_check)

    def _is_capturable(self, piece):
        if not self._capturables:
            return False

        capturables = self._capturables[piece.color]
        for _, threatened in capturables.items():
            if piece in threatened:
                return True

        return False

    def _is_check_blockable(self, piece, king):
        src = self.board.get_square(piece)
        dst = self.board.get_square(king)
        checking_move = Move(piece, src, dst)
        path = checking_move.path[1:-1]
        blocking_pieces = [
            bp
            for bp in self.board.pieces
            if bp.color == king.color and
            bp != king
        ]
        for checking_path_square in path:
            for blocking_piece in blocking_pieces:
                blocking_origin = self.board.get_square(blocking_piece)
                with self._try_move(blocking_origin, checking_path_square):
                    self._description.append(
                        f'\nTrying blocking move by blocking piece '
                        f'{blocking_piece}, from {blocking_origin} to '
                        f'{checking_path_square}\n'
                        'After this move, the caturables are: '
                        f'{self._capturables[king.color]}\n\n'
                    )
                    capturing_pieces = self._get_threatening_pieces(king)
                    if not capturing_pieces:
                        self._description.append(
                            'The check on {king} can be averted by blocking '
                            f'the cheking piece {piece} by moving '
                            f'{blocking_piece} from {blocking_origin} '
                            f'to {checking_path_square}.'
                        )
                        return True

        self._description.append(
            f'There is no way to block {piece} from giving check '
            f'to {king}'
        )
        return False

    def _is_checking_piece_capturable(self, checking_piece, checked_king):
        pieces_threatening_checking_piece = self._get_threatening_pieces(
            piece=checking_piece,
        )

        pieces_that_can_capture_safely = []
        for threatening_piece in pieces_threatening_checking_piece:
            src = self._board.get_square(threatening_piece)
            dst = self._board.get_square(checking_piece)
            with self._try_move(src, dst):
                pieces_checking_after_move = (
                    self._pieces_checking_black
                    if checked_king.color == c.Color.black
                    else self._pieces_checking_white
                )
                if not pieces_checking_after_move:
                    pieces_that_can_capture_safely.append(threatening_piece)

        if pieces_that_can_capture_safely:
            self._description.append(
                f'{checking_piece} checking {checked_king} can be captured'
                f'by the following pieces - {pieces_that_can_capture_safely}.'
            )
            return True
        else:
            self._description.append(
                f'{checking_piece} checking {checked_king} cannot be'
                f'captured by any of the {checked_king.color.name} pieces.'
            )
            return False

    def _get_threatening_pieces(self, piece):
        threatening_pieces = []
        capturables = self._capturables[piece.color]
        for threatening_piece, threatened_pieces in capturables.items():
            if piece in threatened_pieces:
                threatening_pieces.append(threatening_piece)

        return threatening_pieces

    def _get_pieces(self, color):
        return [
            piece
            for piece in self.board.pieces
            if piece.color == color
        ]

    def _escape_square_exists(self, king):
        def filter_self_color(square):
            if self.board.is_empty(square):
                return True
            piece = self.board.get_piece(square)
            return piece.color != king.color

        king_square = self.board.get_square(king)

        # All squares surrounding the king
        surrounding = [
            Square((king_square.x + incr_x, king_square.y + incr_y))
            for incr_x, incr_y in itertools.product([1, -1, 0], [1, -1, 0])
            if 0 <= king_square.x + incr_x < 8 and
            0 <= king_square.y + incr_y < 8 and
            (incr_x, incr_y) != (0, 0)
        ]

        # Remove those squares from surrounding that are occupied by the pieces
        # of the same color as the king. The remaining squares are either
        # empty or are covered by opponent pieces that the king can potentially
        # capture.
        surrounding = list(filter(filter_self_color, surrounding))

        # Now remove the sqaures where king cannot move due to threat from
        # other pieces
        escape_squares = []
        for surr_square in surrounding:
            with self._try_move(king_square, surr_square):
                capturing_pieces = self._get_threatening_pieces(king)
                if not capturing_pieces:
                    escape_squares.append(surr_square)

        # If there are still squares left in surrounding, these are the ones
        # where the king can safely move to escape the check
        if len(escape_squares) != 0:
            self._description.append(
                f'{king} can safely escape to these squares -  '
                f'{escape_squares}'
            )
            return True
        else:
            self._description.append(
                f'There are no squares where {king} can safely escape to'
            )
            return False

    @contextlib.contextmanager
    def _try_move(self, src, dst):
        board_copy = self._board.data.copy()
        reverse_copy = self._board.reverse.copy()
        captured_black_copy = copy.copy(self._captured_black)
        captured_white_copy = copy.copy(self._captured_white)
        capturables_copy = self._capturables.copy()
        pieces_checking_black_copy = copy.copy(self._pieces_checking_black)
        pieces_checking_white_copy = copy.copy(self._pieces_checking_white)
        move_history_copy = copy.copy(self._move_history)

        self._perform_move(src, dst)
        try:
            yield
        finally:
            self._board.data = board_copy.copy()
            self._board.reverse = reverse_copy.copy()
            self._captured_black = copy.copy(captured_black_copy)
            self._captured_white = copy.copy(captured_white_copy)
            self._capturables = capturables_copy.copy()

            self._pieces_checking_black = copy.copy(
                pieces_checking_black_copy
            )

            self._pieces_checking_white = copy.copy(
                pieces_checking_white_copy
            )

            self._move_history = copy.copy(move_history_copy)
