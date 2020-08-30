from .boarder import Board
from .mover import Move
from .constant import PieceType, Color


class Game:
    def __init__(self):
        self._board = Board()
        self._captured_white = []
        self._captured_black = []
        self._move_history = []

    def reset(self):
        self._board.clear()

    def is_game_over(self):
        pass

    def move(self, src, dst):
        piece_to_move = self._board.get_piece(src)

        # Case I: No piece to move
        if piece_to_move is None:
            return

        # Case II: Illegal move for piece
        mv = Move(piece_to_move, src, dst)
        if not mv.is_move_legal(piece_to_move, src, dst):
            return

        # Case III: Destination has piece of same color
        dst_piece = self._board.get_piece(dst)
        if dst_piece is not None:
            if piece_to_move.color == dst_piece.color:
                return

        # Case IV: Path to destination is not empty
        if piece_to_move.PieceType in [
                PieceType.queen,
                PieceType.rook,
                PieceType.rook,
        ]:
            in_between_squares = mv.path[1:-1]
            if not all([self._board.is_empty(s) for s in in_between_squares]):
                return

        dst_piece = self._board.clear_square(dst)
        if dst_piece.color == Color.black:
            self._captured_black.append(dst)
        else:
            self._captured_white.append(dst)

        src_piece = self._board.clear_square(src)
        self._board.add_piece(src_piece, src)
