import os
import contextlib


from PySide2 import QtWidgets, QtCore, QtGui


from . import constant as c, imager


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
        self._size = size

        self._default_play_time = 10
        self._default_bonus_time = 0

        self._play_time = self._default_play_time
        self._bonus_time = self._default_bonus_time

        self._default_white_promotion = c.PieceType.queen
        self._default_black_promotion = c.PieceType.queen

        self._is_standard_type = True
        self._white_promotion = self._default_white_promotion
        self._black_promotion = self._default_black_promotion

        self._resize_factor = float(size / c.IMAGE.DEFAULT_SIZE)
        self._image_store = {}

        self._font_id = QtGui.QFontDatabase().addApplicationFont(
            c.APP.FONT_FILE_PATH
        )
        if self._font_id == -1:
            error_msg = f'Could not load font from {c.APP.FONT_FILE_PATH}'
            raise RuntimeError(error_msg)
        self._font = QtGui.QFont(c.APP.FONT_FAMILY)

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
        self.setStyleSheet(c.APP.STYLESHEET)
        self.setFixedSize(self._size, self._size)
        self.setModal(True)

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
        layout_label = self._create_label('GAME TIME', 300, 24)
        layout.addWidget(layout_label)

        self._play_time_slider_value_label = self._create_label(
            f'{str(self._default_play_time).zfill(2)} min',
            50,
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
            50,
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
        layout_label = self._create_label('GAME TYPE', 200, 24)
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
        layout_label = self._create_label('PAWN PROMOTIONS', 200, 24)
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
            int(self._resize_factor * 100),
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

    def _create_label(self, name, width=150, font_size=14):
        label = QtWidgets.QLabel(name)
        label.setFixedWidth(int(self._resize_factor * width))
        label.setStyleSheet('QWidget { border: none }')
        self._font.setPointSize(int(self._resize_factor * font_size))
        label.setFont(self._font)

        return label

    def _create_slider(self, min_val, max_val, default_val, step=1):
        slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        slider.setMinimum(min_val)
        slider.setMaximum(max_val)
        slider.setSingleStep(step)
        slider.setMinimumWidth(int(self._resize_factor * 300))
        slider.setValue(default_val)
        return slider

    def _create_radio_button(self, name, check_state):
        btn = QtWidgets.QRadioButton(name)
        btn.setChecked(check_state)
        # btn.setMinimumHeight(self._resize_factor * 50)
        btn.setStyleSheet('QWidget { border: none }')
        self._font.setPointSize(int(self._resize_factor * 14))
        btn.setFont(self._font)
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


class MainWindow(QtWidgets.QDialog):
    MOVE_SIGNAL = QtCore.Signal(str)
    GAME_RESET_SIGNAL = QtCore.Signal()
    GAME_OPTIONS_SET_SIGNAL = QtCore.Signal(tuple)

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

        self._option_widget = OptionWidget(
            size=c.IMAGE.DEFAULT_SIZE,
        )

        self._first_square = None
        self._second_square = None
        self._current_player = c.Color.white

        self._bonus_time = self._option_widget.bonus_time

        self._timer_white = QtCore.QTimer()
        self._timer_white.setInterval(1000)  # timeout per 1 second
        self._time_white = 0
        self._remaining_time_white = self._option_widget.play_time * 60

        self._timer_black = QtCore.QTimer()
        self._timer_black.setInterval(1000)  # timeout per 1 second
        self._time_black = 0
        self._remaining_time_black = self._option_widget.play_time * 60

        self._is_paused = True
        self._is_game_over = False
        self._has_game_started = False

        self._gamedata = None
        self._show_threatened = False

        self._resize_factor = (
            self._board_image.width / c.IMAGE.BASE_IMAGE_SIZE
        )

        self._setup_ui()
        self._connect_signals()

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_C:
            self._toggle_show_threatened()

    def board_updated(self):
        self._update()

    def _reset(self):
        self._option_widget.reset()
        self.GAME_RESET_SIGNAL.emit()
        self._start_btn.setText('START')
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

        self._bonus_time = self._option_widget.bonus_time

        self._time_white = 0
        self._remaining_time_white = self._option_widget.play_time * 60

        self._time_black = 0
        self._remaining_time_black = self._option_widget.play_time * 60

        self._is_paused = True
        self._is_game_over = False
        self._has_game_started = False

        self._gamedata = None
        self._show_threatened = False

        self._timer_white.stop()
        self._timer_black.stop()

        self._board_image.update()
        self._update_image_label()

        self._update_captured_image_labels()

        self._white_timer_lcd.display(
            self._format_time(self._remaining_time_white)
        )
        self._black_timer_lcd.display(
            self._format_time(self._remaining_time_black)
        )

    def _setup_ui(self):
        self.setWindowTitle(c.APP.NAME)
        self.setStyleSheet(c.APP.STYLESHEET)
        self.setFixedWidth(self._board_image.width + 40)

        self._main_layout = QtWidgets.QVBoxLayout(self)

        # Add black panel layout
        self._black_panel_layout = self._create_black_panel_layout()
        self._main_layout.addLayout(self._black_panel_layout)

        # Add image layout
        self._image_layout_outer = self._create_image_layout()
        self._main_layout.addLayout(self._image_layout_outer)

        # Add white panel layout
        self._white_panel_layout = self._create_white_panel_layout()
        self._main_layout.addLayout(self._white_panel_layout)

        # Add bottom layout
        self._bottom_layout = self._create_bottom_layout()
        self._main_layout.addLayout(self._bottom_layout, 3)

    def _create_black_panel_layout(self):
        self._black_panel_layout = QtWidgets.QHBoxLayout()

        self._captured_pixmap_white = QtGui.QPixmap.fromImage(
            self._captured_image.qt_image_white)
        self._captured_label_white = QtWidgets.QLabel()
        self._captured_label_white.setPixmap(self._captured_pixmap_white)

        self._black_timer_lcd = QtWidgets.QLCDNumber()
        self._black_timer_lcd.setDigitCount(8)
        self._black_timer_lcd.display(
            self._format_time(self._remaining_time_black)
        )
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
        self._white_timer_lcd.display(
            self._format_time(self._remaining_time_white)
        )
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

        self._options_btn = self._create_btn('OPTIONS')
        self._bottom_layout.addWidget(self._options_btn, 1)

        self._reset_btn = self._create_btn('RESET')
        self._bottom_layout.addWidget(self._reset_btn, 1)

        self._start_btn = self._create_btn('START')
        self._bottom_layout.addWidget(self._start_btn, 1)

        return self._bottom_layout

    def _create_btn(self, text):
        btn = QtWidgets.QPushButton(str(text).upper())
        btn.setMinimumHeight(
            int(c.APP.BUTTON_HEIGHT * self._resize_factor)
        )
        btn.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Expanding
        )

        return btn

    def _connect_signals(self):
        self._image_label.mousePressEvent = self._on_image_clicked
        self._options_btn.clicked.connect(self._on_options_btn_clicked)
        self._reset_btn.clicked.connect(self._on_reset_btn_clicked)
        self._start_btn.clicked.connect(self._on_start_btn_clicked)
        self._option_widget.DONE_SIGNAL.connect(self._on_options_selected)
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
                highlight_color=c.APP.HIGHLIGHT_COLOR.selected,
                is_first_selected=True,
            )
        else:
            self._second_square = square

        both_cell_selected = all([self._first_square, self._second_square])
        if both_cell_selected:
            move = f'{self._first_square.address}{self._second_square.address}'
            self.MOVE_SIGNAL.emit(move)

    def _on_options_btn_clicked(self):
        if self._has_game_started:
            return

        self._option_widget.show()

    def _on_reset_btn_clicked(self):
        self._reset()

    def _on_options_selected(self):
        self._bonus_time = self._option_widget.bonus_time
        self._remaining_time_white = self._option_widget.play_time * 60
        self._white_timer_lcd.display(
            self._format_time(self._remaining_time_white)
        )

        self._remaining_time_black = self._option_widget.play_time * 60
        self._black_timer_lcd.display(
            self._format_time(self._remaining_time_black)
        )

        self.GAME_OPTIONS_SET_SIGNAL.emit(
            (
                self._option_widget.white_promotion,
                self._option_widget.black_promotion,
                self._option_widget.is_standard_type,
            )
        )

    def game_over(self, winner):
        self._is_game_over = True
        self._captured_image.draw_winner(winner)
        self._update_captured_image_labels()
        self._start_btn.setText('RESTART')
        self._stop_all_timers()

    def _timer_white_timeout(self):
        self._time_white += 1
        self._remaining_time_white -= 1
        if self._remaining_time_white == 0:
            self.game_over(winner=c.Color.black)

        time_str = self._format_time(self._remaining_time_white)
        self._white_timer_lcd.display(time_str)

    def _timer_black_timeout(self):
        self._time_black += 1
        self._remaining_time_black -= 1
        if self._remaining_time_black == 0:
            self.game_over(winner=c.Color.white)

        time_str = self._format_time(self._remaining_time_black)
        self._black_timer_lcd.display(time_str)

    def _on_start_btn_clicked(self):
        self._has_game_started = True
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
        self._gamedata = game_data

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

    def toggle_player(self, color):
        # It has been a successful move
        # Before changing the current player, let us add bonus
        # time to the player who made the move
        self._add_bonus_time()

        self._stop_current_player_time()
        self._current_player = color
        self._start_current_player_time()

        if self._show_threatened:
            self._display_threatened()

    def _add_bonus_time(self):
        if self._current_player == c.Color.white:
            self._remaining_time_white += self._bonus_time
            self._white_timer_lcd.display(
                self._format_time(self._remaining_time_white)
            )
        else:
            self._remaining_time_black += self._bonus_time
            self._black_timer_lcd.display(
                self._format_time(self._remaining_time_white)
            )

    def _display_threatened(self):
        threatened = self._get_threatened(self._current_player)
        self._board_image.draw_threatened(threatened)
        self._update_image_label()

    def _hide_threatened(self):
        self._board_image.clear_threatened_squares()
        self._update_image_label()

    def _get_threatened(self, color):
        if self._gamedata is None:
            return []

        total_threatened = []
        capturables = self._gamedata.capturables[color]
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

    def _toggle_show_threatened(self):
        self._show_threatened = not self._show_threatened

        if not self._show_threatened:
            self._hide_threatened()
        else:
            self._display_threatened()
