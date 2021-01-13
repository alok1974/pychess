import sys


from PySide2 import QtWidgets, QtGui


from .core.gamer import Game
from .gui.main import MainWidget
from . import constant as c


def run():
    app = QtWidgets.QApplication(sys.argv)

    QtGui.QFontDatabase.addApplicationFont(c.APP.FONT_FILE_PATH)
    QtGui.QFontDatabase.addApplicationFont(c.APP.CHESS_FONT_FILE_PATH)

    game = Game()
    w = MainWidget(board=game.board)
    w.MOVE_SIGNAL.connect(game.move)
    w.GAME_RESET_SIGNAL.connect(game.reset)
    w.GAME_OPTIONS_SET_SIGNAL.connect(game.set_game_options)
    w.GAME_OVER_SIGNAL.connect(game.game_over)
    w.BULK_MOVE_SIGNAL.connect(game.apply_moves)

    game.MOVE_SIGNAL.connect(w.update_move)
    game.INVALID_MOVE_SIGNAL.connect(w.update_invalid_move)
    game.PLAYER_CHANGED_SIGNAL.connect(w.set_current_player)
    game.MATE_SIGNAL.connect(w.game_over)
    game.NON_STANDARD_BOARD_SET_SIGNAL.connect(w.update_board)
    game.STALEMATE_SIGNAL.connect(w.stalemate)
    game.PROMOTION_REQUIRED_SIGNAL.connect(w.promotion_required)

    w.show()
    app.setStyleSheet(c.APP.STYLESHEET)
    sys.exit(app.exec_())
