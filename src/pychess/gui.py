from PySide2 import QtWidgets


from .constant import APP


class MainWindow(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        self.setWindowTitle(APP.NAME)
        self.setStyleSheet(APP.STYLESHEET)

    def _connect_signals(self):
        pass


def run():
    import sys
    app = QtWidgets.QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    sys.exit(app.exec_())
