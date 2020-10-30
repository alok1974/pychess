from PySide2 import QtWidgets, QtCore


class ButtonWidget(QtWidgets.QDialog):
    OPTION_BTN_CLICKED_SIGNAL = QtCore.Signal()
    AI_BTN_CLICKED_SIGNAL = QtCore.Signal()
    START_BTN_CLICKED_SIGNAL = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        self.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Expanding,
        )
        self.setStyleSheet('border: none;')
        self.setMaximumHeight(200)
        self._main_layout = QtWidgets.QVBoxLayout(self)

        self._options_btn = self._create_button('OPTIONS')
        self._ai_btn = self._create_button('AI')
        self._start_btn = self._create_button('START')

        self._main_layout.addWidget(self._options_btn)
        self._main_layout.addWidget(self._ai_btn)
        self._main_layout.addWidget(self._start_btn)

    def _connect_signals(self):
        self._options_btn.clicked.connect(
            lambda: self.OPTION_BTN_CLICKED_SIGNAL.emit()
        )

        self._ai_btn.clicked.connect(
            lambda: self.AI_BTN_CLICKED_SIGNAL.emit()
        )

        self._start_btn.clicked.connect(
            lambda: self.START_BTN_CLICKED_SIGNAL.emit()
        )

    def _create_button(self, text, minimum_height=50):
        btn = QtWidgets.QPushButton(text)
        btn.setStyleSheet('border: 1px solid rgb(90, 90, 90);')
        btn.setMinimumHeight(minimum_height)
        btn.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Expanding,
        )
        return btn
