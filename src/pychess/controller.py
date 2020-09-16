import sys


from PySide2 import QtWidgets


from .gamer import Game
from .gui import MainWindow


class Controller:
    def __init__(self):
        self._app = QtWidgets.QApplication(sys.argv)
        self._main_window = MainWindow()
        self._game = Game()
        self._connect_signals()

    def _connect_signals(self):
        self._main_window.MOVE_SIGNAL.connect(self._game.move)
        self._main_window.GAME_RESET_SIGNAL.connect(self._game.reset)
        self._game.MOVE_SIGNAL.connect(self._main_window.update_move)
        self._game.INVALID_MOVE_SIGNAL.connect(
            self._main_window.update_invalid_move
        )
        self._game.PLAYER_CHANGED_SIGNAL.connect(
            self._main_window.toggle_player
        )
        self._game.MATE_SIGNAL.connect(
            self._main_window.game_over
        )

    def run(self):
        self._main_window.init_board(board=self._game.board)
        self._main_window.show()
        sys.exit(self._app.exec_())
