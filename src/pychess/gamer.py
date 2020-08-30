from .boarder import Board
from .mover import Move
from .constant import PieceType, Color


class Game:
    def __init__(self):
        self._board = Board()
        self._captured_white = []
        self._captured_black = []
        self._move_history = []

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

    def reset(self):
        self.board.clear()

    def is_game_over(self):
        pass

    def move(self, src, dst):
        piece_to_move = self.board.get_piece(src)

        # Case I: No piece to move
        if piece_to_move is None:
            print('piece to move is None')
            return

        # Case II: Illegal move for piece
        mv = Move(piece_to_move, src, dst)
        if not mv.is_legal:
            print('move is illegal')
            return

        # Case III: Destination has piece of same color
        dst_piece = self.board.get_piece(dst)
        if dst_piece is not None:
            if piece_to_move.color == dst_piece.color:
                print('trying to capture piece of same color')
                return

        # Case IV: Path to destination is not empty
        if piece_to_move.type in [
                PieceType.queen,
                PieceType.rook,
                PieceType.rook,
        ]:
            in_between_squares = mv.path[1:-1]
            if not all([self.board.is_empty(s) for s in in_between_squares]):
                print('path is obstructed')
                return

        dst_piece = self.board.clear_square(dst)
        if dst_piece is not None:
            if dst_piece.color == Color.black:
                self._captured_black.append(dst_piece)
            else:
                self._captured_white.append(dst_piece)

        src_piece = self.board.clear_square(src)
        self.board.add_piece(src_piece, dst)
