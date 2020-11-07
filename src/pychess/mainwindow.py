from PySide2 import QtWidgets, QtCore, QtGui


from . import constant as c, imager
from .pgn import MOVES2PGN, PGN2MOVES
from .engineer import Engine
from .widget import (
    OptionWidget,
    MovesWidget,
    SaveGameDataWidget,
    LoadGameWidget,
    PlayAgainstComputerWidget,
)
from .history import Player


class MainWidget(QtWidgets.QDialog):
    MOVE_SIGNAL = QtCore.Signal(str)
    GAME_RESET_SIGNAL = QtCore.Signal()
    GAME_OPTIONS_SET_SIGNAL = QtCore.Signal(tuple)
    GAME_OVER_SIGNAL = QtCore.Signal(bool)
    BULK_MOVE_SIGNAL = QtCore.Signal(tuple)

    def __init__(self, parent=None):
        super().__init__(parent=parent)

    def init_board(self, board):
        self._engine_color = None
        self._engine = Engine()
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
            parent=self,
        )

        self._save_game_data_widget = SaveGameDataWidget(
            size=c.IMAGE.DEFAULT_SIZE,
            parent=None,
        )

        self._game_loaded = False
        self._first_square = None
        self._second_square = None
        self._current_player = c.Color.white
        self._winner = None

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

        self._game_data = None
        self._history_player = None
        self._show_threatened = False

        self._inspecting_history = False

        self._resize_factor = (
            self._board_image.width / c.IMAGE.BASE_IMAGE_SIZE
        )

        self._setup_ui()
        self._connect_signals()

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_C:
            self._toggle_show_threatened()

        ctrl_s = (
            event.key() == QtCore.Qt.Key_S and
            event.modifiers() == QtCore.Qt.ControlModifier
        )

        if ctrl_s:
            self._handle_save_game()

        ctrl_o = (
            event.key() == QtCore.Qt.Key_O and
            event.modifiers() == QtCore.Qt.ControlModifier
        )

        if ctrl_o:
            self._handle_load_game()

    def board_updated(self):
        self._update()

    def _handle_load_game(self):
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            parent=None,
            caption='Load game (.pgn)',
            filter='*.pgn'

        )
        if not file_path:
            return

        self._pgn2moves = PGN2MOVES(pgn_file_path=file_path)
        if self._pgn2moves.nb_games == 1:
            self._load_game()
        else:
            game_info = self._pgn2moves.game_info
            w = LoadGameWidget(game_info=game_info)
            w.SELECTED_GAME_SIGNAL.connect(self._load_game)
            w.show()

    def _load_game(self, game_index=0):
        self._reset()

        moves = self._pgn2moves.get_moves(game_index=game_index)
        bulk_moves = [
            (f'{src.address}{dst.address}', promotion)
            for src, dst, promotion in moves
        ]
        self.BULK_MOVE_SIGNAL.emit(bulk_moves)

        self._game_loaded = True
        self._white_resign_btn.setVisible(False)
        self._black_resign_btn.setVisible(False)
        self._white_timer_lcd.setVisible(False)
        self._black_timer_lcd.setVisible(False)
        self._options_btn.setVisible(False)
        self._start_btn.setVisible(False)
        self._captured_label_white.setVisible(False)
        self._captured_label_black.setVisible(False)
        self._stop_all_timers()

    def _handle_save_game(self):
        if not self._has_game_started:
            return
        elif self._game_data is None:
            return
        elif not self._game_data.move_history:
            return

        self._save_game_data_widget.show()

    def _save_game(self, game_data):
        result = self._get_result()
        game_data = (
            f'[Event "{game_data.event}"]\n'
            f'[Site "{game_data.site}"]\n'
            f'[Date "{game_data.date}"]\n'
            f'[Round "{game_data.round}"]\n'
            f'[White "{game_data.white}"]\n'
            f'[Black "{game_data.black}"]\n'
            f'[Result "{result}"]\n'
        )

        move_history = self._game_data.move_history
        game_moves = MOVES2PGN(move_history).text
        if not game_moves.endswith(result):
            game_moves = f'{game_moves} {result}'

        game = f'{game_data}\n{game_moves}'

        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(
            parent=None,
            caption='Save game (.pgn)',
            filter='*.pgn'

        )
        with open(file_path, 'w') as fp:
            fp.write(game)

    def _get_result(self):
        if self._winner is None:
            return '1/2-1/2'
        elif self._winner == c.Color.white:
            return '1-0'
        elif self._winner == c.Color.black:
            return '0-1'
        else:
            error_msg = 'Unknown winner type!'
            raise RuntimeError(error_msg)

    def _reset(self):
        self._engine_color = None
        self._option_widget.reset()
        self._moves_widget.reset()
        self.GAME_RESET_SIGNAL.emit()
        self._start_btn.setText('START')
        self._board_image = imager.BoardImage(
            self._board,
            size=c.IMAGE.DEFAULT_SIZE,
        )
        self._captured_image = imager.CapturedImage(
            size=c.IMAGE.DEFAULT_SIZE,
        )

        self._game_loaded = False
        self._first_square = None
        self._second_square = None

        self._current_player = c.Color.white
        self._winner = None

        self._bonus_time = self._option_widget.bonus_time

        self._time_white = 0
        self._remaining_time_white = self._option_widget.play_time * 60

        self._time_black = 0
        self._remaining_time_black = self._option_widget.play_time * 60

        self._is_paused = True
        self._is_game_over = False
        self._has_game_started = False

        self._game_data = None
        self._history_player = None
        self._show_threatened = False

        self._inspecting_history = False

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

        self._white_resign_btn.setVisible(True)
        self._black_resign_btn.setVisible(True)
        self._white_timer_lcd.setVisible(True)
        self._black_timer_lcd.setVisible(True)
        self._options_btn.setVisible(True)
        self._start_btn.setVisible(True)
        self._captured_label_white.setVisible(True)
        self._captured_label_black.setVisible(True)

    def _setup_ui(self):
        self.setWindowTitle(c.APP.NAME)
        self.setStyleSheet(c.APP.STYLESHEET)
        # self.setFixedWidth(self._board_image.width + 40)

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
        self._black_timer_lcd.setSegmentStyle(QtWidgets.QLCDNumber.Flat)
        self._black_timer_lcd.setStyleSheet(
            'color: rgb(255, 255, 255);'
            'background-color: rgb(0, 0, 0);'
            'border: none;'
        )

        self._black_resign_btn = QtWidgets.QPushButton("  RESIGN  ")
        self._black_panel_layout.addWidget(self._captured_label_white, 4)
        self._black_panel_layout.addWidget(self._black_resign_btn, 1)
        self._black_panel_layout.addWidget(self._black_timer_lcd, 2)

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
        self._white_timer_lcd.setSegmentStyle(QtWidgets.QLCDNumber.Flat)
        self._white_timer_lcd.setStyleSheet(
            'color: rgb(0, 0, 0);'
            'background-color: rgb(230, 230, 230);'
            'border: none;'
        )

        self._white_resign_btn = QtWidgets.QPushButton("  RESIGN  ")
        self._white_resign_layout = QtWidgets.QVBoxLayout()
        self._white_resign_layout.addWidget(self._white_timer_lcd)
        self._white_resign_layout.addWidget(self._white_resign_btn)

        self._white_panel_layout.addWidget(self._captured_label_black, 2)
        self._white_panel_layout.addLayout(self._white_resign_layout, 1)
        return self._white_panel_layout

    def _create_bottom_layout(self):
        self._bottom_layout = QtWidgets.QVBoxLayout()

        self._moves_widget = MovesWidget(
            resize_factor=self._resize_factor,
            parent=self,
        )
        self._bottom_layout.addWidget(self._moves_widget)

        self._btn_layout = QtWidgets.QHBoxLayout()

        self._options_btn = self._create_btn(' OPTIONS ')
        self._btn_layout.addWidget(self._options_btn, 1)

        self._engine_btn = self._create_btn(' AI ')
        self._btn_layout.addWidget(self._engine_btn, 1)

        self._reset_btn = self._create_btn(' RESET ')
        self._btn_layout.addWidget(self._reset_btn, 1)

        self._start_btn = self._create_btn(' START ')
        self._btn_layout.addWidget(self._start_btn, 1)

        self._go_to_start_btn = self._create_btn('|<')
        self._btn_layout.addWidget(self._go_to_start_btn, 1)

        self._back_btn = self._create_btn('<')
        self._btn_layout.addWidget(self._back_btn, 1)

        self._forward_btn = self._create_btn('>')
        self._btn_layout.addWidget(self._forward_btn, 1)

        self._go_to_end_btn = self._create_btn('>|')
        self._btn_layout.addWidget(self._go_to_end_btn, 1)

        self._bottom_layout.addLayout(self._btn_layout)

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
        self._engine_btn.clicked.connect(self._on_engine_btn_clicked)
        self._reset_btn.clicked.connect(self._on_reset_btn_clicked)
        self._start_btn.clicked.connect(self._on_start_btn_clicked)
        self._go_to_end_btn.clicked.connect(self._on_go_to_end_btn_clicked)
        self._go_to_start_btn.clicked.connect(self._on_go_to_start_btn_clicked)
        self._forward_btn.clicked.connect(self._on_forward_btn_clicked)
        self._back_btn.clicked.connect(self._on_back_btn_clicked)
        self._option_widget.DONE_SIGNAL.connect(self._on_options_selected)
        self._timer_white.timeout.connect(self._timer_white_timeout)
        self._timer_black.timeout.connect(self._timer_black_timeout)
        self._moves_widget.LABEL_CLICKED_SIGNAL.connect(
            self._on_move_widget_label_clicked
        )

        self._white_resign_btn.clicked.connect(
            lambda: self._resign_btn_clicked(c.Color.black)
        )

        self._black_resign_btn.clicked.connect(
            lambda: self._resign_btn_clicked(c.Color.white)
        )

        self._save_game_data_widget.DONE_SIGNAL.connect(self._save_game)

    def _on_engine_btn_clicked(self):
        w = PlayAgainstComputerWidget(parent=self)
        w.CHOSEN_COLOR_SIGNAL.connect(self._set_engine_color)
        w.show()

    def _set_engine_color(self, color):
        self._engine_color = color
        if self._engine_color == c.Color.white:
            best_move = self._engine.get_best_move()
            if best_move is not None:
                self.MOVE_SIGNAL.emit(best_move)

        self._on_start_btn_clicked()

    def _resign_btn_clicked(self, winning_color):
        if not self._has_game_started:
            return

        self.game_over(winning_color)
        white_wins = True
        if winning_color == c.Color.black:
            white_wins = False

        self.GAME_OVER_SIGNAL.emit(white_wins)
        self._moves_widget.display_win(winning_color)

    def _on_move_widget_label_clicked(self, index):
        self._inspect_history(index=index)

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

    def _on_forward_btn_clicked(self):
        self._inspect_history(cursor_step=1)

    def _on_back_btn_clicked(self):
        self._inspect_history(cursor_step=-1)

    def _on_go_to_start_btn_clicked(self):
        self._inspect_history(start=True)

    def _on_go_to_end_btn_clicked(self):
        self._inspect_history(end=True)

    def _inspect_history(
            self, cursor_step=None,
            start=False, end=False, index=None
    ):
        if self._history_player is None:
            return

        if index is not None:
            result = self._history_player.move_to(index=index)
        elif start:
            result = self._history_player.move_to_start()
        elif end:
            result = self._history_player.move_to_end()
        elif cursor_step == 1:
            result = self._history_player.move_forward()
        elif cursor_step == -1:
            result = self._history_player.move_backward()
        else:
            error_msg = f'Unknown cursor step: {cursor_step}'
            raise RuntimeError(error_msg)

        if result is None or result.board is None:
            return

        self._inspecting_history = not self._history_player.is_at_end
        self._board.data = result.board.data
        self._board.reverse = result.board.reverse

        self._update()

        if result.move is not None:
            self._highlight(
                result.move.src,
                highlight_color=c.APP.HIGHLIGHT_COLOR.src,
            )

            self._highlight(
                result.move.dst,
                highlight_color=c.APP.HIGHLIGHT_COLOR.dst,
            )

        index = self._history_player.current_index
        self._moves_widget.set_active_label(index, set_scroll=True)

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
        self._winner = winner
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
            white_wins = False
            self.GAME_OVER_SIGNAL.emit(white_wins)
            self._moves_widget.display_win(c.Color.black)

        time_str = self._format_time(self._remaining_time_white)
        self._white_timer_lcd.display(time_str)

    def _timer_black_timeout(self):
        self._time_black += 1
        self._remaining_time_black -= 1
        if self._remaining_time_black == 0:
            self.game_over(winner=c.Color.white)
            white_wins = True
            self.GAME_OVER_SIGNAL.emit(white_wins)
            self._moves_widget.display_win(c.Color.white)

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
        self._game_data = game_data
        self._history_player = Player(self._game_data.move_history)

        moves = MOVES2PGN(self._game_data.move_history).moves
        self._moves_widget.setVisible(True)
        self._moves_widget.display_moves(moves)

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

        if self._engine_color is not None:
            if self._current_player == self._engine_color:
                moves = [(m.src, m.dst) for m in self._game_data.move_history]
                best_move = self._engine.get_best_move(moves)
                if best_move is not None:
                    self.MOVE_SIGNAL.emit(best_move)

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


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.main_widget = MainWidget()
        self._frame = QtWidgets.QFrame()
        self._layout = QtWidgets.QVBoxLayout()
        self._layout.addWidget(self.main_widget)
        self._frame.setLayout(self._layout)
        self._status_bar = self.statusBar()
        self._menu_bar = self.menuBar()
        self.setCentralWidget(self._frame)
        self.setWindowTitle('Pychess')
        self.setStyleSheet(c.APP.STYLESHEET)
