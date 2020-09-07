import sys


from PySide2 import QtWidgets


from .gamer import Game
from .gui import MainWindow


def run():
    app = QtWidgets.QApplication(sys.argv)
    mw = MainWindow()
    game = Game()
    mw.MOVE_SIGNAL.connect(game.move)
    game.MOVE_SIGNAL.connect(mw.update)
    game.INVALID_MOVE_SPEC_SIGNAL.connect(mw.clear_moves)
    mw.init_board(board=game.board)
    mw.show()
    sys.exit(app.exec_())
