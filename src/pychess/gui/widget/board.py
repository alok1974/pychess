from PySide2 import QtWidgets, QtCore, QtGui


from ... import imager
from ... import constant as c


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

    def init_board(self):
        self.reset()

    def board_updated(self):
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

    def set_game_over(self):
        self._is_game_over = True

    def set_inspect_history(self):
        self._inspect_history = True

    def set_paused(self):
        self._is_paused = True

    def set_game_loaded(self):
        self._game_loaded = True

    def _is_image_clickable(self):
        return True   # not any(
        #     [
        #         self._game_loaded,
        #         self._is_paused,
        #         self._is_game_over,
        #         self._inspecting_history,
        #     ]
        # )

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

        src = game_data.src
        self._highlight(src, highlight_color=c.APP.HIGHLIGHT_COLOR.src)

        dst = game_data.dst
        self._highlight(dst, highlight_color=c.APP.HIGHLIGHT_COLOR.dst)

        self.clear_moves()

        self._captured_image.update(
            captured_white=game_data.captured_white,
            captured_black=game_data.captured_black,
            leader=game_data.leader,
            lead=game_data.lead
        )

        self._update_captured_image_labels()

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
