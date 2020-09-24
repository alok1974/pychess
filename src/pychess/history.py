import collections


from .boarder import Board


PLAY_RESULT = collections.namedtuple('PLAY_RESULT', ['board', 'move'])


class Player:
    def __init__(self, history):
        self._history = history
        self._last_index = len(self._history) - 1
        self._first_index = -1
        self._current_index = self._last_index

    @property
    def is_at_end(self):
        return self._current_index == self._last_index

    @property
    def is_at_beginning(self):
        return self._current_index == self._first_index

    def move_forward(self):
        return self._perform_move(step=1)

    def move_backward(self):
        return self._perform_move(step=-1)

    def move_to(self, index):
        delta = index - self._current_index
        move_func = self.move_forward if delta > 0 else self.move_backward

        play_result = PLAY_RESULT(board=Board(), move=None)
        for _ in range(abs(delta)):
            play_result = move_func()

        return play_result

    def _perform_move(self, step):
        board = Board()
        self._update_index(step=step)
        if self._current_index == self._first_index:
            return PLAY_RESULT(
                board=board,
                move=None,
            )

        for i, move in enumerate(self._history):
            if i > self._current_index:
                break
            self._apply_move(board, move)

        return PLAY_RESULT(
            board=board,
            move=self._history[self._current_index],
        )

    def _update_index(self, step):
        self._current_index += step

        if self._current_index > self._last_index:
            self._current_index = self._last_index

        if self._current_index < self._first_index:
            self._current_index = self._first_index

    @staticmethod
    def _apply_move(board, move):
        board.clear_square(move.dst)
        piece = board.clear_square(move.src)
        board.add_piece(piece, move.dst)
