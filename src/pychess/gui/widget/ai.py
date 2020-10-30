from PySide2 import QtWidgets, QtCore


from ... import constant as c


class Player(QtWidgets.QDialog):
    CHOSEN_COLOR_SIGNAL = QtCore.Signal(c.Color)

    def __init__(self, size=c.IMAGE.DEFAULT_SIZE, parent=None):
        self._resize_factor = size / c.IMAGE.DEFAULT_SIZE
        self._parent = parent
        super().__init__(parent=parent)
        self._setup_ui()

    def _setup_ui(self):
        self.setWindowTitle('Play against computer')
        self.setModal(True)

        self._main_layout = QtWidgets.QVBoxLayout(self)

        self._white_btn = self._create_btn(c.Color.white)
        self._main_layout.addWidget(self._white_btn)

        self._black_btn = self._create_btn(c.Color.black)
        self._main_layout.addWidget(self._black_btn)

    def _set_player(self, color):
        self.CHOSEN_COLOR_SIGNAL.emit(color)
        self.close()

    def _create_btn(self, color):
        if color == c.Color.white:
            btn_text = 'Computer vs. Human'
        else:
            btn_text = 'Human vs. Computer'

        btn = QtWidgets.QPushButton(btn_text)
        btn.setMinimumWidth(int(200 * self._resize_factor))
        btn.setMinimumHeight(int(50 * self._resize_factor))
        btn.clicked.connect(lambda: self._set_player(color))
        return btn
