import sys


from PySide2 import QtWidgets


from .gamer import Game
from .gui import MainWindow


class Controller:
    def __init__(self):
        self._app = QtWidgets.QApplication(sys.argv)
        self._main_window = MainWindow()
        self._gui = self._main_window.main_widget
        self._game = Game()
        self._connect_signals()

    def _connect_signals(self):
        # Signals from the gui
        self._gui.MOVE_SIGNAL.connect(self._game.move)
        self._gui.GAME_RESET_SIGNAL.connect(self._game.reset)
        self._gui.GAME_OPTIONS_SET_SIGNAL.connect(
            self._game.set_game_options
        )
        self._gui.GAME_OVER_SIGNAL.connect(self._game.game_over)
        self._gui.BULK_MOVE_SIGNAL.connect(self._game.apply_moves)

        # Signals from the game
        self._game.MOVE_SIGNAL.connect(self._gui.update_move)
        self._game.INVALID_MOVE_SIGNAL.connect(
            self._gui.update_invalid_move
        )
        self._game.PLAYER_CHANGED_SIGNAL.connect(
            self._gui.toggle_player
        )
        self._game.MATE_SIGNAL.connect(
            self._gui.game_over
        )
        self._game.NON_STANDARD_BOARD_SET_SIGNAL.connect(
            self._gui.board_updated
        )

    def run(self):
        self._gui.init_board(board=self._game.board)
        self._main_window.show()
        sys.exit(self._app.exec_())
