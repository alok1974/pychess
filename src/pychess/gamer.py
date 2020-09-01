from collections import namedtuple


from .boarder import Board
from .mover import Move
from .constant import PieceType, Color


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
        self._to_move = Color.white
        self._winner = None

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
        self._to_move = Color.white
        self._winner = None

    @property
    def is_game_over(self):
        pass

    def move(self, src, dst):
        result = self._perform_move(src, dst)
        if not result.success:
            return

        self._move_history.append(Move(result.moved_piece, src, dst))
        self._get_capturables()
        self._toggle_to_move()

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

    def _toggle_to_move(self):
        if self._to_move == Color.black:
            self._to_move = Color.white
        else:
            self._to_move = Color.black

    def _is_move_legal(self, src, dst, check_to_move=True):
        piece_to_move = self.board.get_piece(src)

        # Case I: No piece to move
        if piece_to_move is None:
            return False

        # Case II: Not this player's turn
        if check_to_move:
            if piece_to_move.color != self._to_move:
                return False

        # Case III: Illegal move for piece
        mv = Move(piece_to_move, src, dst)
        if not mv.is_legal:
            return False

        # Case IV: Destination has piece of same color
        dst_piece = self.board.get_piece(dst)
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
                    if self._is_move_legal(src, dst, check_to_move=False):
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
        is_under_check = bool(
            self._pieces_checking_black
            if self._to_move == Color.black
            else self._pieces_checking_white
        )

        if is_under_check:
            # Case I: Checking pieces can be captured
            pass

    def _get_pieces_on_board(self, color):
        return [
            piece
            for piece in self.board.pieces
            if piece.color == color
        ]
