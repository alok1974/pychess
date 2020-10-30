import functools


from PySide2 import QtWidgets, QtCore


from ... import constant as c


class LoadGameWidget(QtWidgets.QDialog):
    SELECTED_GAME_SIGNAL = QtCore.Signal(int)

    def __init__(self, game_info, size=c.IMAGE.DEFAULT_SIZE, parent=None):
        super().__init__(parent=parent)
        self._game_info = game_info
        self._size = int(size * 0.8)
        self._selected_index = -1
        self._setup_ui()

    def _setup_ui(self):
        self.setStyleSheet(c.APP.STYLESHEET)
        self.setWindowTitle('Select Game to load')
        self.setModal(True)

        self._main_layout = QtWidgets.QVBoxLayout(self)

        self._scroll_area = QtWidgets.QScrollArea()
        self._scroll_widget = QtWidgets.QWidget()

        self._scroll_area.setVerticalScrollBarPolicy(
            QtCore.Qt.ScrollBarAsNeeded
        )
        self._scroll_area.setHorizontalScrollBarPolicy(
            QtCore.Qt.ScrollBarAlwaysOff
        )

        self._game_data_layout = QtWidgets.QVBoxLayout()
        for index, game_data in enumerate(self._game_info):
            btn = QtWidgets.QPushButton(game_data)
            func = functools.partial(
                self._on_btn_clicked,
                index=index
            )
            btn.clicked.connect(func)
            self._game_data_layout.addWidget(btn)

        self._scroll_widget.setLayout(self._game_data_layout)
        self._scroll_area.setWidget(self._scroll_widget)
        self._main_layout.addWidget(self._scroll_area)

    def _on_btn_clicked(self, index):
        self._selected_index = index
        self.close()

    def closeEvent(self, event):
        self.SELECTED_GAME_SIGNAL.emit(self._selected_index)
