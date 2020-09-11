from PySide2 import QtWidgets, QtCore, QtGui


from . import constant as c, imager
from .squarer import Square


class MainWindow(QtWidgets.QDialog):
    MOVE_SIGNAL = QtCore.Signal(str)
    SQUARE_SELECTED = QtCore.Signal(Square)

    def __init__(self, parent=None):
        super().__init__(parent=parent)

    def init_board(self, board):
        self._board = board
        self._board_image = imager.BoardImage(
            self._board,
            size=c.IMAGE.DEFAULT_SIZE,
        )
        self._captured_image = imager.CapturedImage(
            size=c.IMAGE.DEFAULT_SIZE,
        )

        self._first_square = None
        self._second_square = None
        self._current_player = c.Color.white

        self._timer_white = QtCore.QTimer()
        self._timer_white.setInterval(1000)  # timeout per 1 second
        self._time_white = 0

        self._timer_black = QtCore.QTimer()
        self._timer_black.setInterval(1000)  # timeout per 1 second
        self._time_black = 0

        self._is_paused = True
        self._is_game_over = False

        self._resize_factor = (
            self._board_image.width / c.IMAGE.BASE_IMAGE_SIZE
        )

        self._setup_ui()
        self._connect_signals()

    def _reset(self):
        self._board_image = imager.BoardImage(
            self._board,
            size=c.IMAGE.DEFAULT_SIZE,
        )
        self._captured_image = imager.CapturedImage(
            size=c.IMAGE.DEFAULT_SIZE,
        )

        self._first_square = None
        self._second_square = None

        self._current_player = c.Color.white

        self._time_white = 0
        self._time_black = 0

        self._is_paused = True
        self._is_game_over = False

        self._timer_white.stop()
        self._timer_black.stop()

        self._board_image.update()
        self._update_image_label()

        self._update_caputred_image_labels()

        self._white_timer_lcd.display('00:00:00')
        self._black_timer_lcd.display('00:00:00')

    def _setup_ui(self):
        self.setWindowTitle(c.APP.NAME)
        self.setStyleSheet(c.APP.STYLESHEET)

        self.setFixedSize(
            self._board_image.width + 40,
            self._board_image.height +
            (2 * c.APP.LCD_HEIGHT * self._resize_factor) +
            (c.APP.BUTTON_HEIGHT * self._resize_factor) +
            80,
        )

        self._main_layout = QtWidgets.QVBoxLayout(self)

        # Add top layout
        self._top_layout = self._create_top_layout()
        self._main_layout.addLayout(self._top_layout)

        # Add black panel layout
        self._black_panel_layout = self._create_black_panel_layout()
        self._main_layout.addLayout(self._black_panel_layout, 1)

        # Add image layout
        self._image_layout_outer = self._create_image_layout()
        self._main_layout.addLayout(self._image_layout_outer, 1)

        # Add white panel layout
        self._white_panel_layout = self._create_white_panel_layout()
        self._main_layout.addLayout(self._white_panel_layout, 1)

        # Add bottom layout
        self._bottom_layout = self._create_bottom_layout()
        self._main_layout.addLayout(self._bottom_layout, 10)

    def _create_top_layout(self):
        self._top_layout = QtWidgets.QHBoxLayout()
        return self._top_layout

    def _create_black_panel_layout(self):
        self._black_panel_layout = QtWidgets.QHBoxLayout()

        self._captured_pixmap_white = QtGui.QPixmap.fromImage(
            self._captured_image.qt_image_white)
        self._captured_label_white = QtWidgets.QLabel()
        self._captured_label_white.setPixmap(self._captured_pixmap_white)

        self._black_timer_lcd = QtWidgets.QLCDNumber()
        self._black_timer_lcd.setDigitCount(8)
        self._black_timer_lcd.display('00:00:00')
        self._black_timer_lcd.setFixedHeight(
            int(c.APP.LCD_HEIGHT * self._resize_factor)
        )
        self._black_timer_lcd.setSegmentStyle(QtWidgets.QLCDNumber.Flat)
        self._black_timer_lcd.setStyleSheet(
            'color: rgb(255, 255, 255);'
            'background-color: rgb(0, 0, 0);'
            'border: none;'
        )

        self._black_panel_layout.addWidget(self._captured_label_white, 3)
        self._black_panel_layout.addWidget(self._black_timer_lcd, 1)

        return self._black_panel_layout

    def _create_image_layout(self):
        self._image_layout_inner = QtWidgets.QHBoxLayout()

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
        self._image_layout_inner.addWidget(self._image_label)

        # Adding a spacer to the right of the label to make sure that the
        # image label does not stretch otherwise we cannot get the right
        # mouse position to pick the pixel
        self._image_layout_inner.addStretch(1)

        # Create an outer layout to prohibit the vertical stretching
        # of the image label
        self._image_layout_outer = QtWidgets.QVBoxLayout()
        self._image_layout_outer.addLayout(self._image_layout_inner)

        # Adding a spacer to the bottom of the label to make sure that the
        # image label does not stretch otherwise we cannot get the right
        # mouse position to pick the pixel
        self._image_layout_outer.addStretch(1)
        return self._image_layout_outer

    def _create_white_panel_layout(self):
        self._white_panel_layout = QtWidgets.QHBoxLayout()

        self._captured_pixmap_black = QtGui.QPixmap.fromImage(
            self._captured_image.qt_image_black
        )
        self._captured_label_black = QtWidgets.QLabel()
        self._captured_label_black.setPixmap(self._captured_pixmap_black)

        self._white_timer_lcd = QtWidgets.QLCDNumber()
        self._white_timer_lcd.setDigitCount(8)
        self._white_timer_lcd.display('00:00:00')
        self._white_timer_lcd.setFixedHeight(
            int(c.APP.LCD_HEIGHT * self._resize_factor)
        )
        self._white_timer_lcd.setSegmentStyle(QtWidgets.QLCDNumber.Flat)
        self._white_timer_lcd.setStyleSheet(
            'color: rgb(0, 0, 0);'
            'background-color: rgb(230, 230, 230);'
            'border: none;'
        )

        self._white_panel_layout.addWidget(self._captured_label_black, 3)
        self._white_panel_layout.addWidget(self._white_timer_lcd, 1)

        return self._white_panel_layout

    def _create_bottom_layout(self):
        self._bottom_layout = QtWidgets.QHBoxLayout()

        self._start_btn = QtWidgets.QPushButton('START')
        self._start_btn.setMinimumHeight(
            int(c.APP.BUTTON_HEIGHT * self._resize_factor)
        )
        self._bottom_layout.addWidget(self._start_btn)

        return self._bottom_layout

    def _connect_signals(self):
        self._image_label.mousePressEvent = self._on_image_clicked
        self._start_btn.clicked.connect(self._on_start_btn_clicked)
        self._timer_white.timeout.connect(self._timer_white_timeout)
        self._timer_black.timeout.connect(self._timer_black_timeout)

    def _on_image_clicked(self, event):
        if self._is_paused or self._is_game_over:
            return

        button = event.button()
        if button != QtCore.Qt.MouseButton.LeftButton:
            return

        x, y = event.x(), event.y()
        square = self._board_image.pixel_to_square(x, y)
        if self._first_square is None:
            if not self._is_selection_valid(square):
                return

            self._first_square = square
            self._highlight(
                square,
                highlight_color=c.APP.HIGHLIGHT_COLOR.selected
            )
        else:
            self._second_square = square

        both_cell_selected = all([self._first_square, self._second_square])
        if both_cell_selected:
            move = f'{self._first_square.address}{self._second_square.address}'
            self.MOVE_SIGNAL.emit(move)

    def game_over(self, winner):
        self._is_game_over = True
        self._captured_image.draw_winner(winner)
        self._update_caputred_image_labels()
        self._start_btn.setText('RESTART')
        self._stop_all_timers()

    def _timer_white_timeout(self):
        self._time_white += 1
        time_str = self._format_time(self._time_white)
        self._white_timer_lcd.display(time_str)

    def _timer_black_timeout(self):
        self._time_black += 1
        time_str = self._format_time(self._time_black)
        self._black_timer_lcd.display(time_str)

    def _on_start_btn_clicked(self):
        if self._is_game_over:
            self._reset()

        if self._is_paused:
            self._start_btn.setText('PAUSE')
            self._start_current_player_time()
            self._is_paused = False
        else:
            self._start_btn.setText('START')
            self._stop_all_timers()
            self._is_paused = True

    def _start_current_player_time(self):
        if self._current_player == c.Color.white:
            self._timer_white.start()
        else:
            self._timer_black.start()

    def _stop_current_player_time(self):
        if self._current_player == c.Color.white:
            self._timer_white.stop()
        else:
            self._timer_black.stop()

    def _stop_all_timers(self):
        self._timer_white.stop()
        self._timer_black.stop()

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
            highlight_color=c.APP.HIGHLIGHT_COLOR.selected
        )

    def _highlight(self, square, highlight_color):
        self._board_image.highlight(square, highlight_color=highlight_color)
        self._update_image_label()

    def _remove_highlight(self, square):
        self._board_image.remove_highlight(square)
        self._update_image_label()

    def _update(self):
        self._board_image.update()
        self._update_image_label()

    def update_move(self, game_data):
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

        self._update_caputred_image_labels()

    def toggle_player(self, color):
        self._stop_current_player_time()
        self._current_player = color
        self._start_current_player_time()

    def _update_image_label(self):
        self._pixmap = QtGui.QPixmap.fromImage(self._board_image.qt_image)
        self._image_label.setPixmap(self._pixmap)

    def _update_caputred_image_labels(self):
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

    def _format_time(self, total_seconds):
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
