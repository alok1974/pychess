import collections
import getpass


from PySide2 import QtWidgets, QtCore, block_signals


from ... import constant as c


class SaveGameDataWidget(QtWidgets.QDialog):
    DONE_SIGNAL = QtCore.Signal(tuple)

    PGN_GAME_DATA = collections.namedtuple(
        'GAME_DATA',
        [
            'event', 'site', 'date', 'round', 'black', 'white'
        ]
    )

    def __init__(self, size=c.IMAGE.DEFAULT_SIZE, parent=None):
        super().__init__(parent=parent)
        self._size = int(size / 2)

        self._event = ''
        self._site = ''
        self._date = ''
        self._round = ''
        self._white = ''
        self._black = ''

        self._force_quit = False

        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        self.windowTitle = 'Enter game details'
        self.setStyleSheet(c.APP.STYLESHEET)
        # self.setFixedSize(self._size, self._size)
        self.setModal(True)

        self._main_layout = QtWidgets.QVBoxLayout(self)

        layout, self._event_text = self._create_field('Event', 'Casual')
        self._main_layout.addLayout(layout)

        layout, self._site_text = self._create_field('Site', 'Home')
        self._main_layout.addLayout(layout)

        date = self._get_current_date()
        layout, self._date_text = self._create_field('Date', date)
        self._main_layout.addLayout(layout)

        layout, self._round_text = self._create_field('Round', '1')
        self._main_layout.addLayout(layout)

        layout, self._white_text = self._create_field('White')
        self._main_layout.addLayout(layout)

        layout, self._black_text = self._create_field('Black')
        self._main_layout.addLayout(layout)

        layout = QtWidgets.QHBoxLayout()
        self._ok_btn = QtWidgets.QPushButton('Save Game')
        self._cancel_btn = QtWidgets.QPushButton('Cancel')
        layout.addWidget(self._cancel_btn)
        layout.addWidget(self._ok_btn)

        self._main_layout.addLayout(layout)

    def _connect_signals(self):
        self._ok_btn.clicked.connect(self._on_ok_btn_clicked)
        self._cancel_btn.clicked.connect(self._on_cancel_btn_clicked)

    def _on_ok_btn_clicked(self):
        self.close()

    def _on_cancel_btn_clicked(self):
        self._force_quit = True
        self.close()

    def _get_current_date(self):
        from datetime import datetime
        n = datetime.now()
        return f'{n.year}.{n.month}.{n.day}'

    def _create_field(self, name, default_val=''):
        layout = QtWidgets.QHBoxLayout()
        label = QtWidgets.QLabel(name)
        line_edit = QtWidgets.QLineEdit(default_val)
        line_edit.setMinimumWidth(int(self._size * 0.7))
        layout.addWidget(label)
        layout.addStretch(1)
        layout.addWidget(line_edit)

        return layout, line_edit

    def showEvent(self, event):
        widgets = [
            self._event_text,
            self._site_text,
            self._date_text,
            self._round_text,
            self._white_text,
            self._black_text,
        ]
        with block_signals(widgets):
            self._event_text.setText('Casual game')
            self._site_text.setText('Home')
            self._date_text.setText(self._get_current_date())
            self._round_text.setText('1')
            self._white_text.setText(getpass.getuser().capitalize())
            self._black_text.setText('')

    def closeEvent(self, event):
        if self._force_quit:
            self._force_quit = False
            event.accept()
            return

        data = [
            self._event_text.text(), self._site_text.text(),
            self._date_text.text(), self._round_text.text(),
            self._white_text.text(), self._black_text.text(),
        ]

        if not all(data):
            msg_box = QtWidgets.QMessageBox()
            msg_box.setText("Missing details! Please fill all fields.")
            msg_box.exec_()
            event.ignore()
            return

        game_data = self.PGN_GAME_DATA(
            event=self._event_text.text(),
            site=self._site_text.text(),
            date=self._date_text.text(),
            round=self._round_text.text(),
            white=self._white_text.text(),
            black=self._black_text.text(),
        )
        self.DONE_SIGNAL.emit(game_data)
