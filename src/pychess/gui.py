from PySide2 import QtWidgets


class MainWindow(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        pass

    def _connect_signals(self):
        pass


def run():
    import sys
    app = QtWidgets.QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    sys.exit(app.exec_())
