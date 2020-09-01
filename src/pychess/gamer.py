from collections import namedtuple
import itertools


from .boarder import Board
from .mover import Move
from .constant import PieceType, Color
from .piecer import Piece
from .squarer import Square


class Game:
    MOVE_RESULT = namedtuple(
        'MOVE_RESULT',
        ['success', 'moved_piece']
    )

    def __init__(self):
        self._board = Board()
        self._captured_white = []
        self._captured_black = []
        self._move_history = []
        self._capturables = []
        self._pieces_checking_black = []
        self._pieces_checking_white = []
        self._current_player = Color.white
        self._winner = None
        self._is_game_over = False

    @property
    def board(self):
        return self._board

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
            return Color.black
        else:
            return Color.white

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

    def reset(self):
        self.board.clear()
        self._captured_white = []
        self._captured_black = []
        self._move_history = []
        self._capturables = []
        self._pieces_checking_black = []
        self._pieces_checking_white = []
        self._current_player = Color.white
        self._winner = None
        self._is_game_over = False

    @property
    def is_game_over(self):
        return self._is_game_over

    def move(self, src, dst):
        if self.is_game_over:
            return

        result = self._perform_move(src, dst)
        if not result.success:
            return

        self._move_history.append(Move(result.moved_piece, src, dst))
        self._get_capturables()

        if self._is_mate():
            self._winner = self._current_player
            self._is_game_over = True
            return

        self._toggle_player()

    def _perform_move(self, src, dst):
        if not self._is_move_legal(src, dst):
            return self.MOVE_RESULT(success=False, moved_piece=None)

        dst_piece = self.board.clear_square(dst)
        if dst_piece is not None:
            if dst_piece.color == Color.black:
                self._captured_black.append(dst_piece)
            else:
                self._captured_white.append(dst_piece)

        src_piece = self.board.clear_square(src)
        self.board.add_piece(src_piece, dst)
        return self.MOVE_RESULT(success=True, moved_piece=src_piece)

    def _toggle_player(self):
        if self._current_player == Color.black:
            self._current_player = Color.white
        else:
            self._current_player = Color.black

    def _is_move_legal(
            self, src, dst,
            check_current_player=True,
            check_self_color=True, dst_piece=None,
    ):
        piece_to_move = self.board.get_piece(src)

        # Case I: No piece to move
        if piece_to_move is None:
            return False

        # Case II: Not this player's turn
        if check_current_player:
            if piece_to_move.color != self._current_player:
                return False

        # Case III: Illegal move for piece
        mv = Move(piece_to_move, src, dst)
        if not mv.is_legal:
            return False

        # Case IV: Destination has piece of same color
        dst_piece = dst_piece or self.board.get_piece(dst)
        if check_self_color:
            if dst_piece is not None:
                if piece_to_move.color == dst_piece.color:
                    return False

        # Case V: Special case for pawn as it can only capture only
        # with a diagonal move
        if piece_to_move.type == PieceType.pawn:
            if mv.is_orthogonal and dst_piece is not None:
                return
            elif mv.is_diagonal and dst_piece is None:
                return

        # Case V: Path to destination is not empty
        if piece_to_move.type in [
                PieceType.queen,
                PieceType.rook,
                PieceType.bishop,
        ]:
            in_between_squares = mv.path[1:-1]
            if not all([self.board.is_empty(s) for s in in_between_squares]):
                return False

        return True

    def _get_capturables(self):
        self._capturables = {
            Color.white: {},
            Color.black: {},
        }
        for color in [Color.white, Color.black]:
            threatening_color = (
                Color.black
                if color == Color.white
                else Color.white
            )

            threatening_pieces = self._get_pieces_on_board(threatening_color)
            threatened_pieces = self._get_pieces_on_board(color)

            for threatening_piece in threatening_pieces:
                for threatened_piece in threatened_pieces:
                    src = self.board.get_square(threatening_piece)
                    dst = self.board.get_square(threatened_piece)

                    if self._is_move_legal(
                            src, dst, check_current_player=False
                    ):
                        self._capturables[color].setdefault(
                            threatening_piece, []
                        ).append(threatened_piece)

                        # look for checks
                        if threatened_piece.type == PieceType.king:
                            if threatened_piece.color == Color.white:
                                self._pieces_checking_white.append(
                                    threatening_piece
                                )
                            else:
                                self._pieces_checking_black.append(
                                    threatening_piece
                                )

    def _is_mate(self):
        checking_pieces = (
            self._pieces_checking_black
            if self._current_player == Color.white
            else self._pieces_checking_black
        )

        if self._current_player == Color.white:
            king_under_check = Piece(PieceType.king, Color.black)
            checking_pieces = self._pieces_checking_black
        else:
            king_under_check = Piece(PieceType.king, Color.white)
            checking_pieces = self._pieces_checking_white

        if len(checking_pieces) == 0:
            # No piece is checking the king and hence no mate
            return False
        elif len(checking_pieces) == 1:
            checking_piece = checking_pieces[0]
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
            return not self._escape_square_exists(king_under_check)

    def _escape_square_exists(self, king):
        def filter_self_color(square):
            return self.board.get_piece(square).color != king.color

        src = self.board.get_square(king)
        # All squares surrounding the king
        surrounding = [
            Square((src.x + incr_x, src.y + incr_y))
            for incr_x, incr_y in itertools.product([1, -1, 0], [1, -1, 0])
            if 0 <= src.x + incr_x < 8 and
            0 <= src.y + incr_y < 8 and
            (incr_x, incr_y) != (0, 0)
        ]

        # Remove those squares from surrounding that are occupied by the pieces
        # of the same color as the king
        surrounding = list(filter(filter_self_color, surrounding))

        opponent_pieces = [
            (piece, self.board.get_square(piece))
            for piece in self.board.pieces
            if piece.color != king.color
        ]

        for s in surrounding:
            for piece, piece_square in opponent_pieces:
                if self._is_move_legal(
                        piece_square, s,
                        check_current_player=False,
                        dst_piece=king,
                ):
                    return False

        return True

    def _is_check_blockable(self, piece, king):
        unblockable = (
            piece.type == PieceType.pawn or
            piece.type == PieceType.knight or
            piece.type == PieceType.king
        )
        if unblockable:
            # There is no way to bock the path of a pawn or a knight or a king
            return False

        src = self.board.get_square(piece)
        dst = self.board.get_square(king)
        checking_move = Move(piece, src, dst)
        path = checking_move.path[1:-1]
        blocking_pieces = [
            p
            for p in self.board.pieces
            if piece.color == king.color and
            piece != king
        ]
        for checking_path_square in path:
            for blocking_piece in blocking_pieces:
                blocking_square = self.board.get(blocking_piece)
                blocking_move = Move(
                    blocking_piece,
                    blocking_square,
                    checking_path_square,
                )
                if blocking_move.is_legal:
                    return True
        return False

    def _is_checking_piece_capturable(self, piece, checked_king):
        capturables = self.capturables[self._current_player]
        for threatening_piece, threatened_pieces in capturables.items():
            if piece in threatened_pieces:
                if threatening_piece == checked_king:
                    return self._is_capturable_by_king(
                        threatening_piece,
                        checked_king
                    )
                else:
                    return True

        return False

    def _is_capturable_by_king(self, piece, king):
        dst = self.board.get_square(piece)
        opponent_pieces = [
            op
            for op in self.board.pieces
            if op.color == self._current_player and
            op != piece
        ]

        for opponent_piece in opponent_pieces:
            src = self.board.get_square(opponent_piece)
            kwargs = {
                'src': src,
                'dst': dst,
                'check_current_player': False,
                'check_self_color': False,
            }
            if self._is_move_legal(**kwargs):
                # The king can be captured after it captures
                # the checking piece, hence the king cannot capture this piece
                return False

        # We have checked every piece of opponent, nothing
        # is supporting the checking piece and it can be
        # captured by the king.
        return True

    def _get_pieces_on_board(self, color):
        return [
            piece
            for piece in self.board.pieces
            if piece.color == color
        ]
