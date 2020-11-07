import os
import contextlib
import collections
import functools
import enum
import re


from PySide2 import QtWidgets, QtCore, QtGui


from .. import constant as c, imager
from ..pgn import REGEX, NAMEDTUPLES


@contextlib.contextmanager
def block_signals(widgets):
    signal_states = []
    for widget in widgets:
        signal_states.append(
            (widget, widget.signalsBlocked())
        )
    try:
        yield
    finally:
        for widget, is_signal_blocked in signal_states:
            widget.blockSignals(is_signal_blocked)


class AIPlayer(QtWidgets.QDialog):
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


class BoardWidget(QtWidgets.QDialog):
    MOVE_SIGNAL = QtCore.Signal(str)
    WHITE_RESIGN_BTN_CLICKED_SIGNAL = QtCore.Signal()
    BLACK_RESIGN_BTN_CLICKED_SIGNAL = QtCore.Signal()

    def __init__(self, board, parent=None):
        super().__init__(parent=parent)

        self._board = board
        self._board_image = imager.BoardImage(
            self._board,
            size=c.IMAGE.DEFAULT_SIZE,
        )
        self._captured_image = imager.CapturedImage(
            size=c.IMAGE.DEFAULT_SIZE,
        )
        self._setup_ui()
        self._connect_signals()

    @property
    def board(self):
        return self._board

    @property
    def image_height(self):
        return self._board_image.image.height

    def init_board(self):
        self.reset()

    def update_board(self):
        self._update()

    def reset(self):
        self._board_image = imager.BoardImage(
            self._board,
            size=c.IMAGE.DEFAULT_SIZE,
        )
        self._captured_image = imager.CapturedImage(
            size=c.IMAGE.DEFAULT_SIZE,
        )

        self._board_image.update()
        self._update_image_label()
        self._update_captured_image_labels()

        self._first_square = None
        self._second_square = None

        self._current_player = c.Color.white

        self._game_loaded = False
        self._is_paused = True
        self._is_game_over = False
        self._has_game_started = False

        self._show_threatened = False
        self._inspecting_history = False

        self._white_timer_lcd.display(
            self._format_time(c.GAME.DEFAULT_PLAY_TIME * 60)
        )
        self._black_timer_lcd.display(
            self._format_time(c.GAME.DEFAULT_PLAY_TIME * 60)
        )

    def _setup_ui(self):
        self.setStyleSheet('border: none;')
        main_layout = QtWidgets.QVBoxLayout(self)

        # Add black panel widget
        (
            black_widget,
            self._black_timer_lcd,
            self._black_resign_btn
        ) = self._create_panel_widget(color=c.Color.black)
        main_layout.addWidget(black_widget)

        # Add black capture image
        self._captured_pixmap_black = QtGui.QPixmap.fromImage(
            self._captured_image.qt_image_black
        )
        self._captured_label_black = QtWidgets.QLabel()
        self._captured_label_black.setPixmap(self._captured_pixmap_black)
        main_layout.addWidget(self._captured_label_black)

        # Add main board image
        self._image_layout = self._create_image_layout()
        main_layout.addLayout(self._image_layout)

        # Add white capture image
        self._captured_pixmap_white = QtGui.QPixmap.fromImage(
            self._captured_image.qt_image_white)
        self._captured_label_white = QtWidgets.QLabel()
        self._captured_label_white.setPixmap(self._captured_pixmap_white)

        main_layout.addWidget(self._captured_label_white)

        # Add white panel widget
        (
            white_widget,
            self._white_timer_lcd,
            self._white_resign_btn,
        ) = self._create_panel_widget(color=c.Color.white)
        main_layout.addWidget(white_widget)

    def _create_image_layout(self):
        # Create Pixmap
        self._pixmap = QtGui.QPixmap.fromImage(self._board_image.qt_image)

        # Create Label and add the pixmap
        self._image_label = QtWidgets.QLabel()
        self._image_label.setPixmap(self._pixmap)
        self._image_label.setMinimumWidth(self._board_image.qt_image.width())
        self._image_label.setMinimumHeight(self._board_image.qt_image.height())
        self._image_label.setCursor(
            QtGui.QCursor(QtCore.Qt.PointingHandCursor)
        )

        # Create an innner layout to prohibit horizontal stretching of the
        # image label
        self._image_layout_inner = QtWidgets.QHBoxLayout()
        self._image_layout_inner.addWidget(self._image_label)

        # Adding a spacer to the right of the label to make sure that the
        # image label does not stretch otherwise we cannot get the right
        # mouse position to pick the pixel
        self._image_layout_inner.addStretch(1)

        # Create an outer layout to prohibit the vertical stretching
        # of the image label
        self._image_layout = QtWidgets.QVBoxLayout()
        self._image_layout.addLayout(self._image_layout_inner)

        # Adding a spacer to the bottom of the label to make sure that the
        # image label does not stretch otherwise we cannot get the right
        # mouse position to pick the pixel
        self._image_layout.addStretch(1)
        return self._image_layout

    def _create_panel_widget(self, color, min_height=50):
        widget = QtWidgets.QWidget()
        widget.setStyleSheet('border: none;')
        layout = QtWidgets.QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        lcd = self._create_lcd(
            color=color,
            min_height=min_height,
        )
        btn = self._create_btn(
            text='RESIGN',
            min_height=min_height,
        )
        layout.addWidget(lcd, 1)
        layout.addWidget(btn, 2)

        widget.setMaximumWidth(self._board_image.image.width)

        return widget, lcd, btn

    def _create_lcd(self, color, min_height=None):
        lcd = QtWidgets.QLCDNumber()
        if min_height is not None:
            lcd.setMinimumHeight(min_height)
        lcd.setDigitCount(8)
        lcd.display('00:00:00')
        lcd.setSegmentStyle(QtWidgets.QLCDNumber.Flat)

        if color == c.Color.black:
            foreground = 'rgb(230, 230, 230)'
            background = 'rgb(0, 0 ,0)'
        else:
            foreground = 'rgb(0, 0, 0)'
            background = 'rgb(230, 230, 230)'

        lcd.setStyleSheet(
            f'color: {foreground};'
            f'background-color: {background};'
            'border: none;'
        )

        lcd.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Expanding,
        )

        return lcd

    def _create_btn(self, text, min_height=None):
        btn = QtWidgets.QPushButton(str(text).upper())
        if min_height is not None:
            btn.setMinimumHeight(min_height)

        btn.setStyleSheet('border: 1px solid #5A5A5A;')

        btn.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Expanding,
        )

        return btn

    def _connect_signals(self):
        self._image_label.mousePressEvent = self._on_image_clicked
        self._white_resign_btn.clicked.connect(
            lambda: self.WHITE_RESIGN_BTN_CLICKED_SIGNAL.emit()
        )

        self._black_resign_btn.clicked.connect(
            lambda: self.BLACK_RESIGN_BTN_CLICKED_SIGNAL.emit()
        )

    @property
    def is_game_over(self):
        return self._is_game_over

    @is_game_over.setter
    def is_game_over(self, val):
        self._is_game_over = val

    @property
    def inspecting_history(self):
        return self._inspecting_history

    @inspecting_history.setter
    def inspecting_history(self, val):
        self._inspecting_history = val

    @property
    def is_paused(self):
        return self._is_paused

    @is_paused.setter
    def is_paused(self, val):
        self._is_paused = val

    @property
    def game_loaded(self):
        return self._game_loaded

    @game_loaded.setter
    def game_loaded(self, val):
        self._game_loaded = val

    def _is_image_clickable(self):
        return not any(
            [
                self._game_loaded,
                self._is_paused,
                self._is_game_over,
                self._inspecting_history,
            ]
        )

    def _on_image_clicked(self, event):
        if not self._is_image_clickable():
            return

        if event.button() != QtCore.Qt.MouseButton.LeftButton:
            return

        square = self._board_image.pixel_to_square(event.x(), event.y())
        if self._first_square is None:
            if not self._is_selection_valid(square):
                return

            self._first_square = square
            self._highlight(
                square,
                highlight_color=c.APP.HIGHLIGHT_COLOR.selected,
                is_first_selected=True,
            )
        else:
            self._second_square = square

        both_cell_selected = all([self._first_square, self._second_square])
        if both_cell_selected:
            move = f'{self._first_square.address}{self._second_square.address}'
            self.MOVE_SIGNAL.emit(move)

    def _is_selection_valid(self, square):
        if square is None:
            return False

        if self._board_image.board.is_empty(square):
            return False

        selected_color = self._board_image.board.get_piece(square).color
        if selected_color != self._current_player:
            return False

        return True

    def clear_moves(self):
        self._first_square = None
        self._second_square = None

    def update_invalid_move(self):
        if not self._is_selection_valid(self._second_square):
            return

        self._remove_highlight(self._first_square)
        self._first_square = self._second_square
        self._second_square = None
        self._highlight(
            self._first_square,
            highlight_color=c.APP.HIGHLIGHT_COLOR.selected,
            is_first_selected=True,
        )

    def _highlight(self, square, highlight_color, is_first_selected=False):
        self._board_image.highlight(
            square,
            highlight_color=highlight_color,
            is_first_selected=is_first_selected,
        )
        self._update_image_label()

    def _remove_highlight(self, square):
        self._board_image.remove_highlight(square)
        self._update_image_label()

    def _update(self):
        self._board_image.update()
        self._update_image_label()

    def update_move(self, game_data):
        self._game_data = game_data
        self._update()

        self.highlight_move(src=game_data.src, dst=game_data.dst)

        self.clear_moves()

        self._captured_image.update(
            captured_white=game_data.captured_white,
            captured_black=game_data.captured_black,
            leader=game_data.leader,
            lead=game_data.lead
        )

        self._update_captured_image_labels()

    def highlight_move(self, src, dst):
        self._highlight(src, highlight_color=c.APP.HIGHLIGHT_COLOR.src)
        self._highlight(dst, highlight_color=c.APP.HIGHLIGHT_COLOR.dst)

    def set_current_player(self, color):
        self._current_player = color
        if self._show_threatened:
            self._display_threatened()

    def _display_threatened(self):
        threatened = self._get_threatened(self._current_player)
        self._board_image.draw_threatened(threatened)
        self._update_image_label()

    def _hide_threatened(self):
        self._board_image.clear_threatened_squares()
        self._update_image_label()

    def _get_threatened(self, color):
        if self._game_data is None:
            return []

        total_threatened = []
        capturables = self._game_data.capturables[color]
        for _, threatened in capturables.items():
            total_threatened.extend(threatened)

        total_threatened = list(set(total_threatened))

        return total_threatened

    def _update_image_label(self):
        self._pixmap = QtGui.QPixmap.fromImage(self._board_image.qt_image)
        self._image_label.setPixmap(self._pixmap)

    def _update_captured_image_labels(self):
        self._captured_pixmap_white = QtGui.QPixmap.fromImage(
            self._captured_image.qt_image_white)
        self._captured_label_white.setPixmap(self._captured_pixmap_white)

        self._captured_pixmap_black = QtGui.QPixmap.fromImage(
            self._captured_image.qt_image_black)
        self._captured_label_black.setPixmap(self._captured_pixmap_black)

    def mousePressEvent(self, event):
        # NOTE: This event will be fired only when
        # the user has clicke somewhere in the gui
        # OUTSIDE of the chess board image. We can
        # easily clear the first and the second square
        # selections
        self._first_square = None
        self._second_square = None

    def _toggle_show_threatened(self):
        self._show_threatened = not self._show_threatened

        if not self._show_threatened:
            self._hide_threatened()
        else:
            self._display_threatened()

    def display_time_white(self, seconds):
        self._white_timer_lcd.display(
            self._format_time(seconds)
        )

    def display_time_black(self, seconds):
        self._black_timer_lcd.display(
            self._format_time(seconds)
        )

    @staticmethod
    def _format_time(total_seconds):
        seconds, hours_minutes = total_seconds % 60, int(total_seconds / 60)
        if hours_minutes > 60:
            minutes, hours = hours_minutes % 60, int(hours_minutes / 60)
        else:
            minutes = hours_minutes
            hours = 0

        hours = str(hours).zfill(2)
        minutes = str(minutes).zfill(2)
        seconds = str(seconds).zfill(2)

        return f'{hours}:{minutes}:{seconds}'

    def game_over(self, winner):
        self._winner = winner
        self._is_game_over = True
        self._captured_image.draw_winner(winner)
        self._update_captured_image_labels()


class ButtonWidget(QtWidgets.QDialog):
    OPTION_BTN_CLICKED_SIGNAL = QtCore.Signal()
    AI_BTN_CLICKED_SIGNAL = QtCore.Signal()
    RESET_BTN_CLICKED_SIGNAL = QtCore.Signal()
    START_BTN_CLICKED_SIGNAL = QtCore.Signal()

    @enum.unique
    class BUTTON_TYPE(enum.Enum):
        options = 0
        ai = 1
        reset = 2
        start = 3

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
        self.setMaximumHeight(250)
        self._main_layout = QtWidgets.QVBoxLayout(self)

        self.options_btn = self._create_button('OPTIONS')
        self.ai_btn = self._create_button('AI')
        self.reset_btn = self._create_button('RESET')
        self.start_btn = self._create_button('START')

        self._main_layout.addWidget(self.options_btn)
        self._main_layout.addWidget(self.ai_btn)
        self._main_layout.addWidget(self.reset_btn)
        self._main_layout.addWidget(self.start_btn)

    def reset(self):
        self.update_btn_text(self.BUTTON_TYPE.start, 'START')

    def update_btn_text(self, btn_type, text):
        btn = None
        if btn_type == self.BUTTON_TYPE.start:
            btn = self.start_btn
        elif btn_type == self.BUTTON_TYPE.options:
            btn = self.options_btn
        elif btn_type == self.BUTTON_TYPE.reset:
            btn = self.reset_btn
        elif btn_type == self.BUTTON_TYPE.ai:
            btn = self.ai_btn
        else:
            error_msg = f"Unknown button type {btn_type}"
            raise TypeError(error_msg)

        btn.setText(text)

    def _connect_signals(self):
        self.options_btn.clicked.connect(
            lambda: self.OPTION_BTN_CLICKED_SIGNAL.emit()
        )

        self.ai_btn.clicked.connect(
            lambda: self.AI_BTN_CLICKED_SIGNAL.emit()
        )

        self.reset_btn.clicked.connect(
            lambda: self.RESET_BTN_CLICKED_SIGNAL.emit()
        )

        self.start_btn.clicked.connect(
            lambda: self.START_BTN_CLICKED_SIGNAL.emit()
        )

    def _create_button(self, text, minimum_height=40):
        btn = QtWidgets.QPushButton(text)
        btn.setStyleSheet('border: 1px solid rgb(90, 90, 90);')
        btn.setMinimumHeight(minimum_height)
        btn.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Expanding,
        )
        return btn


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


class MoveWidget(QtWidgets.QDialog):
    MOVE_SELECTED_SIGNAL = QtCore.Signal(int)
    FIRST_BTN_CLICKED_SIGNAL = QtCore.Signal()
    PREV_BTN_CLICKED_SIGNAL = QtCore.Signal()
    NEXT_BTN_CLICKED_SIGNAL = QtCore.Signal()
    LAST_BTN_CLICKED_SIGNAL = QtCore.Signal()

    WORD_DATA = collections.namedtuple(
        'WORD_DATA',
        [
            'move_index',
            'start',
            'length',
            'word',
        ],
    )

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self._highlight_format = self._highlight_format()
        self._plain_format = self._plain_format()

        self._font = self._load_chess_fonts()

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

    def display_win(self, winner):
        winning_text = '1-0'
        if winner == c.Color.black:
            winning_text = '0-1'

        self._textedit.insertPlainText(winning_text)

    def display_moves(self, moves):
        self.reset()
        cur_pos = 0
        move_index = -1
        for index, m1, m2 in moves:
            # Seding reverse color for the unicode fonts as our
            # UI theme is dark
            m1 = self._apply_chess_fonts(m1, c.Color.black)  # white move
            m2 = self._apply_chess_fonts(m2, c.Color.white)  # black move
            move_num = f'{index}.'
            mid_space = ' '
            trailing_space = '  '
            move_string = f'{move_num}{m1}{mid_space}{m2}{trailing_space}'

            if m1:
                move_index += 1
                self._add_word_data(
                    pos=cur_pos,
                    word=m1,
                    word_starts_at=len(move_num),
                    move_index=move_index,
                )

            if m2:
                move_index += 1
                self._add_word_data(
                    pos=cur_pos,
                    word=m2,
                    word_starts_at=(len(move_num) + len(m1) + len(mid_space)),
                    move_index=move_index,
                )

            cur_pos += len(move_string)

            self._textedit.insertPlainText(move_string)

    def _load_chess_fonts(self):
        font_id = QtGui.QFontDatabase().addApplicationFont(
            c.APP.CHESS_FONT_FILE_PATH
        )
        if font_id == -1:
            error_msg = (
                f'Could not load font from {c.APP.CHESS_FONT_FILE_PATH}'
            )
            raise RuntimeError(error_msg)

        self._font = QtGui.QFont(c.APP.CHESS_FONT_FAMILY)

    def _apply_chess_fonts(self, text, color):
        piece_str = None
        m = re.match(REGEX.SINGLE_MOVE, text)
        if m is not None:
            result = NAMEDTUPLES.PARSE_SINGLE_MOVE_RESULT(*m.groups())
            piece_str = self._get_piece_str(result)
            if piece_str is not None:
                unicode_symbol = self._get_unicode(piece_str, color)
                if piece_str != 'P':
                    text = text[1:]
                text = f'{unicode_symbol}{text}'
        return text

    @staticmethod
    def _get_piece_str(parse_result):
        piece_str = None
        if parse_result.piece is not None:
            if not parse_result.piece:
                piece_str = 'P'
            else:
                piece_str = parse_result.piece[0]
                if piece_str in ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']:
                    piece_str = 'P'
        return piece_str

    @staticmethod
    def _get_unicode(piece_string, color):
        piece_name = None
        if piece_string == 'B':
            piece_name = c.PieceType.bishop.name
        elif piece_string == 'K':
            piece_name = c.PieceType.king.name
        elif piece_string == 'N':
            piece_name = c.PieceType.knight.name
        elif piece_string == 'P':
            piece_name = c.PieceType.pawn.name
        elif piece_string == 'R':
            piece_name = c.PieceType.rook.name
        elif piece_string == 'Q':
            piece_name = c.PieceType.queen.name
        else:
            raise ValueError(f'Unknown piece string {piece_string}')

        unicodes = getattr(c.APP.PIECE_UNICODE, piece_name)
        return getattr(unicodes, color.name)

    def _highlight_last(self):
        max_index = max(
            [
                int(k)
                for k in self._move_index_word_data.keys()
            ]
        )
        word = self._move_index_word_data[max_index]
        if word == '':
            max_index = max_index - 1
        self.highlight_move(move_index=max_index)

    def highlight_move(self, move_index):
        # Remove hightlight from last highlighted
        self._remove_highlight(word_data=self._last_highlighted)

        if move_index == -1:
            return

        word_data = self._move_index_word_data[move_index]
        self._add_highlight(word_data=word_data)

        self._last_highlighted = word_data

    def _setup_ui(self):
        self.setStyleSheet('border: none;')
        self.setMinimumWidth(c.APP.MOVE_WIDGET_WIDTH)
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

    @staticmethod
    def _create_text_edit():
        textedit = QtWidgets.QTextEdit()
        textedit.setFontFamily(c.APP.CHESS_FONT_FAMILY)
        textedit.setStyleSheet('border: 1px solid rgb(90, 90, 90)')
        textedit.setReadOnly(True)
        textedit.setTextInteractionFlags(QtCore.Qt.NoTextInteraction)
        textedit.viewport().setCursor(
            QtGui.QCursor(QtCore.Qt.PointingHandCursor)
        )
        textedit.zoomIn(14)
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

    @staticmethod
    def _create_btn(text):
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

    def _add_word_data(self, pos, word, word_starts_at, move_index):
        word_data = self.WORD_DATA(
            move_index=move_index,
            start=(pos + word_starts_at),
            length=len(word),
            word=word,
        )

        if move_index not in self._move_index_word_data:
            self._move_index_word_data[move_index] = word_data

        # Added 1 in the range below
        # to get the cursor after word ends
        for i_word in range(len(word) + 1):
            char_pos = pos + word_starts_at + i_word
            self._cursor_pos_map[char_pos] = word_data

    @staticmethod
    def _highlight_format():
        char_format = QtGui.QTextCharFormat()
        char_format.setForeground(QtGui.QBrush(QtGui.QColor("red")))
        char_format.setBackground(QtGui.QBrush(QtGui.QColor("yellow")))
        char_format.setFontWeight(QtGui.QFont.Bold)
        return char_format

    @staticmethod
    def _plain_format():
        char_format = QtGui.QTextCharFormat()
        char_format.setForeground(QtGui.QBrush(QtGui.QColor(221, 221, 221)))
        char_format.setBackground(QtGui.QBrush(QtGui.QColor(25, 25, 25)))
        char_format.setFontWeight(QtGui.QFont.Normal)
        return char_format

    def _add_highlight(self, word_data):
        self._format_word(word_data, char_format=self._highlight_format)

    def _remove_highlight(self, word_data):
        self._format_word(word_data, char_format=self._plain_format)

    def _format_word(self, word_data, char_format):
        if word_data is None:
            return

        cursor = self._textedit.textCursor()
        cursor.setPosition(word_data.start)
        cursor.movePosition(
            QtGui.QTextCursor.NextCharacter,
            QtGui.QTextCursor.KeepAnchor,
            word_data.length,
        )
        cursor.mergeCharFormat(char_format)


class OptionWidget(QtWidgets.QDialog):
    PROMOTION_PIECES = [
        c.PieceType.queen,
        c.PieceType.rook,
        c.PieceType.bishop,
        c.PieceType.knight,
    ]

    DONE_SIGNAL = QtCore.Signal()

    def __init__(self, size=c.IMAGE.DEFAULT_SIZE, parent=None):
        super().__init__(parent=parent)
        self._size = int(size * 0.8)

        self._default_play_time = c.GAME.DEFAULT_PLAY_TIME
        self._default_bonus_time = c.GAME.DEFAULT_BONUS_TIME

        self._play_time = self._default_play_time
        self._bonus_time = self._default_bonus_time

        self._default_white_promotion = c.PieceType.queen
        self._default_black_promotion = c.PieceType.queen

        self._is_standard_type = True
        self._white_promotion = self._default_white_promotion
        self._black_promotion = self._default_black_promotion

        self._resize_factor = float(self._size / c.IMAGE.DEFAULT_SIZE)
        self._image_store = {}
        self._setup_ui()
        self._connect_signals()

    def reset(self):
        self._play_time = self._default_play_time
        self._bonus_time = self._default_bonus_time
        self._is_standard_type = True
        self._white_promotion = c.PieceType.queen
        self._black_promotion = c.PieceType.queen

        widgets = [
            self._play_time_slider, self._bonus_time_slider,
            self._standard_button, self._chess960_button,
            self._white_promotion_combobox, self._black_promotion_combobox,

        ]

        with block_signals(widgets):
            self._play_time_slider.setValue(self._default_play_time)
            self._bonus_time_slider.setValue(self._default_bonus_time)

            self._standard_button.setChecked(True)
            self._chess960_button.setChecked(False)

            self._white_promotion_combobox.setCurrentIndex(
                self._get_piece_type_index(
                    self._default_white_promotion
                )
            )

            self._black_promotion_combobox.setCurrentIndex(
                self._get_piece_type_index(
                    self._default_black_promotion
                )
            )

    def _get_piece_type_index(self, piece_type):
        return self.PROMOTION_PIECES.index(piece_type)

    @property
    def play_time(self):
        return self._play_time

    @property
    def bonus_time(self):
        return self._bonus_time

    @property
    def is_standard_type(self):
        return self._is_standard_type

    @property
    def white_promotion(self):
        return self._white_promotion

    @property
    def black_promotion(self):
        return self._black_promotion

    def _setup_ui(self):
        self.setModal(True)
        self.setMaximumSize(c.IMAGE.DEFAULT_SIZE, c.IMAGE.DEFAULT_SIZE)
        self._main_layout = QtWidgets.QVBoxLayout(self)

        time_widget = self._create_time_widget()
        self._main_layout.addWidget(time_widget)

        self._main_layout.addSpacerItem(
            QtWidgets.QSpacerItem(1, int(self._resize_factor * 20)),
        )

        game_widget = self._create_game_widget()
        self._main_layout.addWidget(game_widget)

        self._main_layout.addSpacerItem(
            QtWidgets.QSpacerItem(1, int(self._resize_factor * 20)),
        )

        promotion_widget = self._create_promotion_widget()
        self._main_layout.addWidget(promotion_widget)

    def _create_time_widget(self):
        widget = QtWidgets.QWidget()
        widget.setMaximumHeight(
            int(self._resize_factor * 220)
        )
        widget.setStyleSheet(
            'QWidget { border: 1px solid #5A5A5A }'
        )

        layout = QtWidgets.QVBoxLayout(widget)
        layout_label = self._create_label('GAME TIME')
        layout.addWidget(layout_label)

        self._play_time_slider_value_label = self._create_label(
            f'{str(self._default_play_time).zfill(2)} min',
        )
        self._play_time_slider = self._create_slider(
            min_val=1,
            max_val=60,
            default_val=self._default_play_time,
            step=1,
        )
        play_time_layout = self._create_time_layout(
            slider=self._play_time_slider,
            value_label=self._play_time_slider_value_label,
            title='TIME EACH PLAYER ',
        )

        self._bonus_time_slider_value_label = self._create_label(
            f'{str(self._default_bonus_time).zfill(2)} sec',
        )
        self._bonus_time_slider = self._create_slider(
            min_val=0,
            max_val=60,
            default_val=self._default_bonus_time,
            step=1,
        )
        bonus_time_layout = self._create_time_layout(
            slider=self._bonus_time_slider,
            value_label=self._bonus_time_slider_value_label,
            title='BONUS PER MOVE',
        )

        layout.addLayout(play_time_layout)
        layout.addSpacerItem(
            QtWidgets.QSpacerItem(1, int(self._resize_factor * 20))
        )
        layout.addLayout(bonus_time_layout)

        return widget

    def _create_game_widget(self):
        widget = QtWidgets.QWidget()
        widget.setMaximumHeight(
            int(self._resize_factor * 100)
        )
        widget.setStyleSheet(
            'QWidget { border: 1px solid #5A5A5A }'
        )

        layout = QtWidgets.QVBoxLayout(widget)
        layout_label = self._create_label('GAME TYPE')
        layout.addWidget(layout_label)

        layout.addStretch(1)

        btn_layout = QtWidgets.QHBoxLayout()
        self._standard_button = self._create_radio_button(
            c.GAME.TYPE.std,
            True,
        )
        self._chess960_button = self._create_radio_button(
            c.GAME.TYPE.c9lx,
            False,
        )

        btn_layout.addWidget(self._standard_button)
        btn_layout.addWidget(self._chess960_button)

        layout.addLayout(btn_layout)

        return widget

    def _create_promotion_widget(self):
        widget = QtWidgets.QWidget()
        widget.setMaximumHeight(
            int(self._resize_factor * 150)
        )
        widget.setStyleSheet(
            'QWidget { border: 1px solid #5A5A5A }'
        )

        layout = QtWidgets.QVBoxLayout(widget)
        layout_label = self._create_label('PAWN PROMOTIONS')
        layout.addWidget(layout_label)

        layout.addStretch(1)

        combo_layout = QtWidgets.QHBoxLayout()

        widgets = self._create_promotion_layout(c.Color.white)
        self._white_promotion_layout, self._white_promotion_combobox = widgets
        combo_layout.addLayout(self._white_promotion_layout)

        combo_layout.addStretch(1)

        widgets = self._create_promotion_layout(c.Color.black)
        self._black_promotion_layout, self._black_promotion_combobox = widgets
        combo_layout.addLayout(self._black_promotion_layout)

        layout.addLayout(combo_layout)

        return widget

    def _create_time_layout(self, slider, value_label, title):
        layout = QtWidgets.QVBoxLayout()

        label_layout = QtWidgets.QHBoxLayout()
        slider_label = self._create_label(title)

        label_layout.addWidget(slider_label)
        label_layout.addStretch(1)
        label_layout.addWidget(value_label)

        layout.addLayout(label_layout)
        layout.addWidget(slider)

        return layout

    def _create_promotion_layout(self, color):
        layout = QtWidgets.QHBoxLayout()
        label = self._create_label(
            f'{color.name.upper()}',
        )
        label.setAlignment(QtCore.Qt.AlignCenter)
        combobox = QtWidgets.QComboBox()
        combobox.setMinimumWidth(
            int(self._resize_factor * 150)
        )
        combobox.setMinimumHeight(
            int(self._resize_factor * 30)
        )

        for item in [t.name for t in self.PROMOTION_PIECES]:
            combobox.addItem(
                self._create_icon(f'{item}_small', color),
                '',
            )

        layout.addWidget(label)
        layout.addWidget(combobox)
        layout.addStretch(1)

        return layout, combobox

    def _create_icon(self, piece_name, color):
        def _get_piece_image_path(piece_name, color):
            color_name = color.name
            piece_images = getattr(c.IMAGE.PIECE_IMAGE, piece_name)
            image_name = getattr(piece_images, color_name)
            image_path = os.path.join(c.IMAGE.IMAGE_DIR, image_name)

            error_msg = f'Image path {image_path} does not exist!'
            assert(os.path.exists(image_path)), error_msg
            return image_path

        icon = QtGui.QIcon()
        image_path = _get_piece_image_path(piece_name, color)
        icon.addFile(image_path)
        return icon

    @staticmethod
    def _create_label(name):
        label = QtWidgets.QLabel(name)
        label.setStyleSheet('QWidget { border: none }')
        return label

    def _create_slider(self, min_val, max_val, default_val, step=1):
        slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        slider.setMinimum(min_val)
        slider.setMaximum(max_val)
        slider.setSingleStep(step)
        slider.setMinimumWidth(int(self._resize_factor * 300))
        slider.setValue(default_val)
        return slider

    @staticmethod
    def _create_radio_button(name, check_state):
        btn = QtWidgets.QRadioButton(name)
        btn.setChecked(check_state)
        btn.setStyleSheet('QWidget { border: none }')
        return btn

    def _connect_signals(self):
        self._play_time_slider.valueChanged.connect(
            self._on_play_time_slider_changed
        )

        self._bonus_time_slider.valueChanged.connect(
            self._on_bonus_time_slider_changed
        )

        self._chess960_button.toggled.connect(
            lambda: self._on_game_type_btn_toggled(self._chess960_button)
        )

        self._standard_button.toggled.connect(
            lambda: self._on_game_type_btn_toggled(self._standard_button)
        )

        self._black_promotion_combobox.currentIndexChanged.connect(
            self._on_black_combo_index_changed,
        )

        self._white_promotion_combobox.currentIndexChanged.connect(
            self._on_white_combo_index_changed,
        )

    def _on_play_time_slider_changed(self, val):
        self._play_time = val
        self._play_time_slider_value_label.setText(f'{str(val).zfill(2)} min')

    def _on_bonus_time_slider_changed(self, val):
        self._bonus_time = val
        self._bonus_time_slider_value_label.setText(f'{str(val).zfill(2)} sec')

    def _on_game_type_btn_toggled(self, btn):
        if btn.text() == c.GAME.TYPE.std:
            self._is_standard_type = btn.isChecked()

        if btn.text() == c.GAME.TYPE.c9lx:
            self._is_standard_type = not btn.isChecked()

    def _on_white_combo_index_changed(self, index):
        self._white_promotion = self.PROMOTION_PIECES[index]

    def _on_black_combo_index_changed(self, index):
        self._black_promotion = self.PROMOTION_PIECES[index]

    def closeEvent(self, event):
        self.DONE_SIGNAL.emit()
