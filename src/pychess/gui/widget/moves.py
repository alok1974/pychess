import collections


from PySide2 import QtWidgets, QtGui, QtCore


WORD_DATA = collections.namedtuple(
    'WORD_DATA',
    [
        'move_index',
        'start',
        'length'
    ],
)


class MoveWidget(QtWidgets.QDialog):
    MOVE_SELECTED_SIGNAL = QtCore.Signal(int)
    FIRST_BTN_CLICKED_SIGNAL = QtCore.Signal()
    PREV_BTN_CLICKED_SIGNAL = QtCore.Signal()
    NEXT_BTN_CLICKED_SIGNAL = QtCore.Signal()
    LAST_BTN_CLICKED_SIGNAL = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self._highlight_format = QtGui.QTextCharFormat()
        self._highlight_format.setForeground(
            QtGui.QBrush(QtGui.QColor("red"))
        )
        self._highlight_format.setBackground(
            QtGui.QBrush(QtGui.QColor("yellow"))
        )
        self._highlight_format.setFontWeight(QtGui.QFont.Bold)

        self._cursor_pos_map = {}
        self._move_index_word_data = {}
        self._last_highlighted = None
        self._setup_ui()
        self._connect_signals()

    def reset(self):
        self._cursor_pos_map = {}
        self._move_index_word_data = {}
        self._last_highlighted = None
        self._textedit.clear()

    def _setup_ui(self):
        self.setStyleSheet('border: none;')
        self.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Expanding,
        )

        self._main_layout = QtWidgets.QVBoxLayout(self)

        self._textedit = self._create_text_edit()
        self._main_layout.addWidget(self._textedit)

        (
            btn_widget,
            self._first_btn,
            self._prev_btn,
            self._next_btn,
            self._last_btn,
        ) = self._create_btn_widget()
        self._main_layout.addWidget(btn_widget)

    def _create_text_edit(self):
        textedit = QtWidgets.QTextEdit()
        textedit.setStyleSheet('border: 1px solid rgb(90, 90, 90)')
        textedit.setReadOnly(True)
        textedit.setMinimumWidth(600)
        textedit.setTextInteractionFlags(QtCore.Qt.NoTextInteraction)
        textedit.viewport().setCursor(
            QtGui.QCursor(QtCore.Qt.PointingHandCursor)
        )
        textedit.zoomIn(12)
        return textedit

    def _create_btn_widget(self):
        widget = QtWidgets.QWidget()
        widget.setMaximumHeight(50)
        widget.setStyleSheet('border: none;')
        layout = QtWidgets.QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)

        first_btn = self._create_btn('|<')
        layout.addWidget(first_btn)

        prev_btn = self._create_btn('<')
        layout.addWidget(prev_btn)

        next_btn = self._create_btn('>')
        layout.addWidget(next_btn)

        last_btn = self._create_btn('>|')
        layout.addWidget(last_btn)

        return widget, first_btn, prev_btn, next_btn, last_btn

    def _create_btn(self, text):
        btn = QtWidgets.QPushButton(text)
        btn.setStyleSheet('border: 1px solid rgb(90, 90, 90)')
        btn.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Expanding,
        )
        return btn

    def _connect_signals(self):
        self._textedit.mousePressEvent = self._on_move_mouse_press

        self._first_btn.clicked.connect(
            lambda: self.FIRST_BTN_CLICKED_SIGNAL.emit()
        )

        self._prev_btn.clicked.connect(
            lambda: self.PREV_BTN_CLICKED_SIGNAL.emit()
        )

        self._next_btn.clicked.connect(
            lambda: self.NEXT_BTN_CLICKED_SIGNAL.emit()
        )

        self._last_btn.clicked.connect(
            lambda: self.LAST_BTN_CLICKED_SIGNAL.emit()
        )

    def _on_move_mouse_press(self, event):
        move_index = self._index_from_mouse_pos(event.pos())
        if move_index is None:
            return

        self.MOVE_SELECTED_SIGNAL.emit(move_index)
        self.highlight_move(move_index=move_index)

    def _index_from_mouse_pos(self, mouse_pos):
        cursor = self._textedit.cursorForPosition(mouse_pos)
        pos = cursor.position()

        word_data = self._cursor_pos_map.get(pos, None)
        if word_data is None:
            return

        return word_data.move_index

    def display_moves(self, moves):
        cur_pos = 0
        move_index = -1
        for index, m1, m2 in enumerate(moves):
            move_index += 1

            move_num = f'{index + 1}.'
            mid_space = ' '
            trailing_space = '  '
            move_string = f'{move_num}{m1}{mid_space}{m2}{trailing_space}'

            self._add_word_data(
                pos=cur_pos,
                word=m1,
                word_starts_at=len(move_num),
                move_index=move_index,
            )

            move_index += 1
            self._add_word_data(
                pos=cur_pos,
                word=m2,
                word_starts_at=(len(move_num) + len(m1) + len(mid_space)),
                move_index=move_index,
            )

            cur_pos += len(move_string)

            self._textedit.insertPlainText(move_string)

    def _add_word_data(self, pos, word, word_starts_at, move_index):
        word_data = WORD_DATA(
            move_index=move_index,
            start=(pos + word_starts_at),
            length=len(word),
        )

        if move_index not in self._move_index_word_data:
            self._move_index_word_data[move_index] = word_data

        # Added 1 in the range below
        # to get the cursor after word ends
        for i_word in range(len(word) + 1):
            char_pos = pos + word_starts_at + i_word
            self._cursor_pos_map[char_pos] = word_data

    def highlight_move(self, move_index):
        word_data = self._move_index_word_data[move_index]
        self._format_word(
            word_data,
            self._highlight_format,
        )

        # Remove hightlight from last highlighted
        self._format_word(self._last_highlighted)
        self._last_highlighted = word_data

    def _format_word(self, word_data, char_format=None):
        if word_data is None:
            return

        if char_format is None:
            char_format = QtGui.QTextCharFormat()
            char_format.setForeground(
                QtGui.QBrush(QtGui.QColor(221, 221, 221))
            )
            char_format.setBackground(
                QtGui.QBrush(QtGui.QColor(25, 25, 25))
            )
            char_format.setFontWeight(QtGui.QFont.Normal)

        cursor = self._textedit.textCursor()
        cursor.setPosition(word_data.start)
        cursor.movePosition(
            QtGui.QTextCursor.NextCharacter,
            QtGui.QTextCursor.KeepAnchor,
            word_data.length,
        )
        cursor.mergeCharFormat(char_format)
