import collections
import itertools
import re
import contextlib
import copy


from .. import constant as c
from ..event import Signal
from ..element.boarder import Board
from ..element.squarer import Square
from ..element.piecer import Piece
from .mover import Move


GAME_DATA = collections.namedtuple(
    'GAME_DATA',
    [
        'src', 'dst', 'captured_white', 'captured_black',
        'leader', 'lead', 'move_history', 'capturables',
    ]
)


PLAYED_MOVE = collections.namedtuple(
    'PLAYED_MOVE',
    [
        'piece',
        'src',
        'dst',
        'is_capture',
        'captured_piece',
        'castling_done',
        'is_king_side_castling',
        'disambiguate',
        'promoted_piece',
        'is_check',
        'is_mate',
        'winner',
    ]
)


class Game:
    MOVE_RESULT = collections.namedtuple(
        'MOVE_RESULT',
        [
            'success',
            'moved_piece',
            'is_castling',
            'captured_piece',
            'king_side_castle',
            'disambiguation',
            'promoted_piece',
        ]
    )

    CHECK_MATE_RESULT = collections.namedtuple(
        'CHECK_MATE_RESULT',
        [
            'is_check',
            'is_mate',
        ]
    )

    MOVE_SIGNAL = Signal(GAME_DATA)
    INVALID_MOVE_SIGNAL = Signal()
    MATE_SIGNAL = Signal(c.Color)
    PLAYER_CHANGED_SIGNAL = Signal(c.Color)
    NON_STANDARD_BOARD_SET_SIGNAL = Signal()
    STALEMATE_SIGNAL = Signal()
    PROMOTION_REQUIRED_SIGNAL = Signal(str)

    def __init__(self):
        self._move_no = 1
        self._signals_blocked = False
        self._board = Board()
        self._captured_white = []
        self._captured_black = []

        self._move_history = []
        self._game_started = False

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

        self._black_promotion_piece_type = None
        self._white_promotion_piece_type = None
        self._is_standard_type = True

    @contextlib.contextmanager
    def block_signals(self):
        current_state = self._signals_blocked
        self._signals_blocked = True
        try:
            yield
        finally:
            self._signals_blocked = current_state

    @property
    def board(self):
        return self._board

    @board.setter
    def board(self, val):
        self._board = val

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
        if self._game_started:
            return

        self._white_promotion_piece_type = options.white_promotion
        self._black_promotion_piece_type = options.black_promotion
        self._is_standard_type = options.is_standard

        self._board.set_pieces(self._is_standard_type)

        if not self._signals_blocked:
            self.NON_STANDARD_BOARD_SET_SIGNAL.emit()

    def reset(self):
        self._move_no = 1
        self._signals_blocked = False
        self._board.reset()
        self._captured_white = []
        self._captured_black = []

        self._move_history = []

        self._game_started = False
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

        self._black_promotion_piece_type = None
        self._white_promotion_piece_type = None
        self._is_standard_type = True

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

    def apply_moves(self, moves):
        with self.block_signals():
            for move, promotion in moves[:-1]:
                result = self.move((move, promotion))
                if not result:
                    error_msg = (
                        'Error happened while trying to apply the move: '
                        f'move {self._move_no}({self._current_player.name}): '
                        f'{move}'
                    )
                    raise RuntimeError(error_msg)

        # This will send the final signal to update the UI
        last_move, last_promotion = moves[-1]
        result = self.move((last_move, last_promotion))
        if not result:
            error_msg = (
                'Error happened while trying to apply the move: '
                f'move {self._move_no}({self.current_player.name}): '
                f'{last_move}'
            )
            raise RuntimeError(error_msg)

    def move(self, move_data):
        move_spec, promotion = move_data
        if self.is_game_over:
            return

        if promotion is not None:
            if self._current_player == c.Color.white:
                self._white_promotion_piece_type = promotion
            else:
                self._black_promotion_piece_type = promotion

        try:
            src, dst = self.parse_move_spec(move_spec)
        except RuntimeError:
            if not self._signals_blocked:
                self.INVALID_MOVE_SIGNAL.emit()
            return

        if self._not_players_turn(src):
            if not self._signals_blocked:
                self.INVALID_MOVE_SIGNAL.emit()
            return

        if self.move_causes_discovered_check(src, dst, self._current_player):
            if not self._signals_blocked:
                self.INVALID_MOVE_SIGNAL.emit()
            return

        if self._promotion_required(src, dst):
            if not self._signals_blocked:
                self.PROMOTION_REQUIRED_SIGNAL.emit(move_spec)
            return

        result = self._perform_move(src, dst)
        if not result.success:
            self.INVALID_MOVE_SIGNAL.emit()
            return

        move = self._record_move(result, src, dst)
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

        if not self._signals_blocked:
            self.MOVE_SIGNAL.emit(game_data)

        if self._current_player == c.Color.black:
            self._move_no += 1

        if move.is_mate:
            white_wins = True
            if self._current_player == c.Color.black:
                white_wins = False
            self.game_over(white_wins=white_wins)
            return True

        opponent = (
            c.Color.black
            if self._current_player == c.Color.white
            else c.Color.white
        )
        if self._is_stalemate(player=opponent):
            self._stalemate()
            return True

        self._toggle_player()
        return True

    def _stalemate(self):
        self._winner = None
        self._is_game_over = True

        if not self._signals_blocked:
            self.STALEMATE_SIGNAL.emit()

    def game_over(self, white_wins):
        winner = c.Color.white
        if not white_wins:
            winner = c.Color.black
        self._winner = winner
        self._is_game_over = True

        if not self._signals_blocked:
            self.MATE_SIGNAL.emit(self._winner)

    def move_causes_discovered_check(self, src, dst, player):
        with self._try_move(src, dst):
            king = Piece(c.PieceType.king, color=player)
            return self._is_capturable(king)

    def _is_stalemate(self, player):
        for piece in self._get_pieces(player):
            if self._piece_can_move(piece, player):
                return False

        return True

    def _piece_can_move(self, piece, color):
        src = self._board.get_square(piece)
        dst_incr = None
        if piece.type == c.PieceType.pawn:
            y_incr = -1 if color == c.Color.black else 1
            dst_incr = list(itertools.product((1, 0, -1), (y_incr,)))
        elif piece.type == c.PieceType.knight:
            dst_incr = (
                list(itertools.product((-1, 1), (-2, 2))) +
                list(itertools.product((-2, 2), (-1, 1)))
            )
        elif piece.type == c.PieceType.bishop:
            dst_incr = list(itertools.product((-1, 1), (-1, 1)))
        elif piece.type == c.PieceType.rook:
            dst_incr = [(0, 1), (0, -1), (-1, 0), (1, 0)]
        elif piece.type == c.PieceType.queen:
            dst_incr = (
                [(0, 1), (0, -1), (-1, 0), (1, 0)] +
                list(itertools.product((-1, 1), (-1, 1)))
            )
        elif piece.type == c.PieceType.king:
            dst_incr = [
                (-1, 1), (0, 1), (1, 1), (1, 0),
                (1, -1), (0, -1), (-1, -1), (-1, 0)
            ]

        for x_incr, y_incr in dst_incr:
            if not 0 <= src.x + x_incr <= 7 or not 0 <= src.y + y_incr <= 7:
                continue

            dst = Square((src.x + x_incr, src.y + y_incr))
            if self.move_causes_discovered_check(src, dst, color):
                continue

            if Move.is_board_move_legal(
                self._board, src, dst, piece
            ):
                self._description.append(
                    f'Not a stalemate as {piece} '
                    f'can move from {src} to {dst}'
                )
                return True

        return False

    def _record_move(self, result, src, dst):
        piece = result.moved_piece
        check_mate_result = self._detect_check_mate()

        winner = None
        if check_mate_result.is_mate:
            winner = self._current_player

        move = PLAYED_MOVE(
            piece=piece,
            src=src,
            dst=dst,
            is_capture=bool(result.captured_piece),
            captured_piece=result.captured_piece,
            castling_done=result.is_castling,
            is_king_side_castling=result.king_side_castle,
            disambiguate=result.disambiguation,
            promoted_piece=result.promoted_piece,
            is_check=check_mate_result.is_check,
            is_mate=check_mate_result.is_mate,
            winner=winner,
        )

        self._move_history.append(move)

        self._game_started = True

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

        return move

    def _not_players_turn(self, src):
        src_piece = self.board.get_piece(src)
        if src_piece is None:
            return True
        return src_piece.color != self._current_player

    def _perform_move(self, src, dst):
        castling_result = False
        captured_piece = None
        king_side_castle = False
        disambiguation = None

        is_legal = Move.is_board_move_legal(self._board, src, dst)
        if not is_legal:
            return self.MOVE_RESULT(
                success=False,
                moved_piece=None,
                is_castling=False,
                captured_piece=None,
                king_side_castle=False,
                disambiguation=None,
                promoted_piece=None,
            )

        piece_to_move = self.board.get_piece(src)
        if Move(piece_to_move, src, dst).is_valid_castling:
            if self._can_castle(piece_to_move, src, dst):
                castling_result = True
                is_short_castle = dst.x == 6
                king_side_castle = is_short_castle
                player = piece_to_move.color
                moved_piece = piece_to_move
                king_src, king_dst = self._board.castle(
                    player=player,
                    is_short_castle=is_short_castle,
                )
                assert(moved_piece.type == c.PieceType.king)
                assert(moved_piece.color == player)
                assert((king_src, king_dst) == (src, dst))
            else:
                # This was try to move the king at e1 or e8 to correct
                # castling squares but other conditions required for a legal
                # castling are not met and thus ultimately this move cannot be
                # made
                return self.MOVE_RESULT(
                    success=False,
                    moved_piece=None,
                    is_castling=False,
                    captured_piece=None,
                    king_side_castle=False,
                    disambiguation=None,
                    promoted_piece=None,
                )
        else:
            # No castling was asked for, let us proceed with a normal move
            moved_piece, captured_piece, disambiguation = self._move_piece(
                src,
                dst,
            )

        promoted_piece = self._handle_promotion(moved_piece, dst)
        self._update_capturables()

        return self.MOVE_RESULT(
            success=True,
            moved_piece=moved_piece,
            is_castling=castling_result,
            captured_piece=captured_piece,
            king_side_castle=king_side_castle,
            disambiguation=disambiguation,
            promoted_piece=promoted_piece,
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

        if piece_type is None:
            return

        promoted_piece = self._create_promoted_piece(
            piece_type=piece_type,
            color=moved_piece.color,
        )

        self.board.promote(promoted_piece, dst)

        return promoted_piece

    def _create_promoted_piece(self, piece_type, color):
        pieces = self._get_pieces(color)
        existing_pieces = [p for p in pieces if p.type == piece_type]
        if not existing_pieces:
            highest_order = -1
        else:
            highest_order = max([p.order for p in existing_pieces])

        return Piece(piece_type, color, highest_order + 1)

    def _move_piece(self, src, dst):
        disambiguation = self._disambiguate(self.board.get_piece(src), dst)
        src_piece = self.board.get_piece(src)
        captured_piece = self.board.move(src, dst)
        if captured_piece is not None:
            if captured_piece.color == c.Color.black:
                self._captured_black.append(captured_piece)
            else:
                self._captured_white.append(captured_piece)

        return src_piece, captured_piece, disambiguation

    def _disambiguate(self, piece, dst):
        if piece.type == c.PieceType.pawn:
            return

        src = self._board.get_square(piece)
        same_color_pieces = self._get_pieces(color=piece.color)
        identical_pieces = [
            p for p in same_color_pieces
            if p.type == piece.type and p != piece
        ]

        disambiguation = []
        for ip in identical_pieces:
            ip_src = self._board.get_square(ip)
            is_legal_move = Move.is_board_move_legal(
                board=self._board,
                src=ip_src,
                dst=dst,
                piece=ip,
                check_dst=False,
            )

            if is_legal_move:
                if ip_src.x_address != src.x_address:
                    disambiguation.append(src.x_address)
                elif ip_src.y_address != src.y_address:
                    disambiguation.append(src.y_address)

        if not disambiguation:
            return
        elif len(disambiguation) == 1:
            return disambiguation[0]
        else:
            return src.address

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

    @staticmethod
    def _get_castling_in_betweens(src, dst):
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

        if not self._signals_blocked:
            self.PLAYER_CHANGED_SIGNAL.emit(self._current_player)

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

                    if Move.is_board_move_legal(self._board, src, dst):
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

    def _detect_check_mate(self):
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
            return self.CHECK_MATE_RESULT(
                is_check=False,
                is_mate=False,
            )
        elif len(checking_pieces) == 1:
            checking_piece = checking_pieces[0]
            self._description.append(
                f'The {king_under_check} is under check by {checking_piece}'
            )
            if self._is_checking_piece_capturable(
                    checking_piece, king_under_check
            ):
                return self.CHECK_MATE_RESULT(
                    is_check=True,
                    is_mate=False,
                )

            elif self._is_check_blockable(checking_piece, king_under_check):
                return self.CHECK_MATE_RESULT(
                    is_check=True,
                    is_mate=False,
                )

            elif self._escape_square_exists(king_under_check):
                return self.CHECK_MATE_RESULT(
                    is_check=True,
                    is_mate=False,
                )

            else:
                return self.CHECK_MATE_RESULT(
                    is_check=True,
                    is_mate=True,
                )
        else:
            self._description.append(
                f'The {king_under_check} is being checked by the following - '
                f'{checking_pieces}'
            )
            no_escape_available = not self._escape_square_exists(
                king_under_check
            )

            if no_escape_available:
                return self.CHECK_MATE_RESULT(
                    is_check=True,
                    is_mate=True,
                )
            else:
                return self.CHECK_MATE_RESULT(
                    is_check=True,
                    is_mate=False,
                )

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
        pawn_two_square_dst = self._board.pawn_two_square_dst
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
            self._board.pawn_two_square_dst = pawn_two_square_dst
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

    def _promotion_required(self, src, dst):
        if self._board.get_piece(src).type != c.PieceType.pawn:
            return False

        if self._current_player == c.Color.black:
            if dst.y != 0:
                return False
            elif self._black_promotion_piece_type is not None:
                return False
            return True
        else:
            if dst.y != 7:
                return False
            elif self._white_promotion_piece_type is not None:
                return False
            return True
