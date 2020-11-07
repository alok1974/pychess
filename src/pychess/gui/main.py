from PySide2 import QtWidgets, QtCore


from .widgets import BoardWidget, ButtonWidget, OptionWidget, MoveWidget


from .. import constant as c, engineer
from ..history import Player as HistoryPlayer
from ..pgn import MOVES2PGN


class MainWidget(QtWidgets.QDialog):
    MOVE_SIGNAL = QtCore.Signal(str)
    GAME_RESET_SIGNAL = QtCore.Signal()
    UPDATE_BOARD_SIGNAL = QtCore.Signal()
    GAME_OPTIONS_SET_SIGNAL = QtCore.Signal(tuple)
    GAME_OVER_SIGNAL = QtCore.Signal(bool)
    BULK_MOVE_SIGNAL = QtCore.Signal(tuple)

    def __init__(self, board, parent=None):
        super().__init__(parent=parent)
        self._board = board
        self._board_widget = BoardWidget(board=self._board)
        self._board_widget.init_board()
        self._button_widget = ButtonWidget()
        self._moves_widget = MoveWidget()
        self._option_widget = OptionWidget(parent=self)

        self._collapsed_width = None
        self._history_player = None
        self._engine_color = None
        self._engine = engineer.Engine()
        self._board = board

        self._game_loaded = False
        self._current_player = c.Color.white

        self._bonus_time = c.GAME.DEFAULT_BONUS_TIME
        self._timer_white = QtCore.QTimer()
        self._timer_white.setInterval(1000)  # timeout per 1 second
        self._remaining_time_white = c.GAME.DEFAULT_PLAY_TIME * 60

        self._timer_black = QtCore.QTimer()
        self._timer_black.setInterval(1000)  # timeout per 1 second
        self._remaining_time_black = c.GAME.DEFAULT_PLAY_TIME * 60

        self._is_paused = True
        self._is_game_over = False
        self._has_game_started = False

        self._game_data = None
        self._history_player = None
        self._show_threatened = False

        self._inspecting_history = False

        self._setup_ui()
        self._connect_signals()

    def _reset(self):
        self.GAME_RESET_SIGNAL.emit()

        self._board_widget.reset()
        self._moves_widget.reset()
        self._option_widget.reset()
        self._button_widget.reset()

        self._engine_color = None
        self._history_player = None

        self._game_loaded = False
        self._current_player = c.Color.white

        self._bonus_time = c.GAME.DEFAULT_BONUS_TIME
        self._timer_white.stop()
        self._remaining_time_white = c.GAME.DEFAULT_PLAY_TIME * 60

        self._timer_black.stop()
        self._remaining_time_black = c.GAME.DEFAULT_PLAY_TIME * 60

        self._is_paused = True
        self._is_game_over = False
        self._has_game_started = False

        self._game_data = None
        self._history_player = None
        self._show_threatened = False

        self._inspecting_history = False

        self._board_widget.display_time_white(self._remaining_time_white)
        self._board_widget.display_time_black(self._remaining_time_black)

    def update_move(self, game_data):
        self._game_data = game_data
        self._history_player = HistoryPlayer(self._game_data.move_history)
        moves = MOVES2PGN(self._game_data.move_history).moves
        self._moves_widget.display_moves(moves)

        self._board_widget.update_move(game_data=self._game_data)

    def update_invalid_move(self):
        self._board_widget.update_invalid_move()

    def set_current_player(self, color):
        self._add_bonus_time()
        self._stop_current_player_time()
        self._current_player = color
        self._board_widget.set_current_player(color)
        self._start_current_player_time()

    def update_board(self):
        self._board_widget.update_board()

    def game_over(self, winner):
        self._is_game_over = True
        self._board_widget.game_over(winner)
        self._button_widget.start_btn.setText('RESTART')
        self._stop_all_timers()

    def resizeEvent(self, event):
        self._handle_left_widget()

    def mouseDoubleClickEvent(self, event):
        if not self._left_widget.isVisible():
            self._toggle_left_widget()

    def _setup_ui(self):
        main_layout = QtWidgets.QHBoxLayout(self)

        self._right_widget = self._create_right_widget()
        self._left_widget = self._create_left_widget()

        main_layout.addWidget(self._right_widget, 1)
        main_layout.addWidget(self._left_widget, 2)

    def _create_right_widget(self):
        widget = QtWidgets.QWidget()
        widget.setStyleSheet('border: none;')
        layout = QtWidgets.QVBoxLayout(widget)
        layout.addWidget(self._board_widget)
        return widget

    def _create_left_widget(self):
        # Create a left widget
        widget = QtWidgets.QWidget()
        widget.setStyleSheet('border: none;')

        inner_layout = QtWidgets.QVBoxLayout()
        inner_layout.setContentsMargins(0, 0, 0, 0)
        inner_layout.addWidget(self._moves_widget, 1)
        inner_layout.addWidget(self._button_widget, 1)

        # Create left widget toggle btn
        self._collapse_btn = QtWidgets.QPushButton('<')
        self._collapse_btn.setStyleSheet('border: 1px solid rgb(90, 90, 90);')
        self._collapse_btn.setFixedWidth(c.APP.COLLAPSE_BTN_WIDTH)

        layout = QtWidgets.QHBoxLayout(widget)
        layout.addWidget(self._collapse_btn)
        layout.addLayout(inner_layout)

        return widget

    def _connect_signals(self):
        self._moves_widget.MOVE_SELECTED_SIGNAL.connect(self._move_selected)

        self._moves_widget.FIRST_BTN_CLICKED_SIGNAL.connect(
            self._first_btn_clicked
        )

        self._moves_widget.PREV_BTN_CLICKED_SIGNAL.connect(
            self._previous_btn_clicked
        )

        self._moves_widget.NEXT_BTN_CLICKED_SIGNAL.connect(
            self._next_btn_clicked
        )

        self._moves_widget.LAST_BTN_CLICKED_SIGNAL.connect(
            self._last_btn_clicked
        )

        self._button_widget.OPTION_BTN_CLICKED_SIGNAL.connect(
            self._option_btn_clicked
        )

        self._button_widget.AI_BTN_CLICKED_SIGNAL.connect(
            self._ai_btn_clicked
        )

        self._button_widget.RESET_BTN_CLICKED_SIGNAL.connect(
            self._reset_btn_clicked
        )

        self._button_widget.START_BTN_CLICKED_SIGNAL.connect(
            self._start_btn_clicked
        )

        self._board_widget.MOVE_SIGNAL.connect(self._recieved_move_string)

        self._board_widget.WHITE_RESIGN_BTN_CLICKED_SIGNAL.connect(
            self._white_resign_btn_clicked
        )

        self._board_widget.BLACK_RESIGN_BTN_CLICKED_SIGNAL.connect(
            self._black_resign_btn_clicked
        )

        self._timer_white.timeout.connect(self._timer_white_timeout)
        self._timer_black.timeout.connect(self._timer_black_timeout)

        self._option_widget.DONE_SIGNAL.connect(self._set_options)

        self._collapse_btn.clicked.connect(self._toggle_left_widget)

    def _handle_left_widget(self):
        if self._collapsed_width is None:
            return

        width_increased = self.width() > self._collapsed_width
        left_widget_is_hidden = not self._left_widget.isVisible()
        if width_increased and left_widget_is_hidden:
            self._left_widget.setVisible(True)
            self._collapse_btn.setVisible(True)
            self._collapse_btn.setText('<')

    def _toggle_left_widget(self):
        vis_to_set = not self._left_widget.isVisible()
        self._left_widget.setVisible(vis_to_set)
        self._collapse_btn.setVisible(vis_to_set)
        if not vis_to_set:
            self._collapse_btn.setText('>')
        else:
            self._collapse_btn.setText('<')
        self.adjustSize()
        if not vis_to_set:
            self._collapsed_width = self.width()

    def _recieved_move_string(self, move_string):
        self.MOVE_SIGNAL.emit(move_string)

    def _move_selected(self, move_index):
        self._inspect_history(index=move_index)

    def _option_btn_clicked(self):
        if self._has_game_started:
            return

        self._option_widget.show()

    def _ai_btn_clicked(self):
        print('ai btn clicked')

    def _reset_btn_clicked(self):
        self._reset()

    def _start_btn_clicked(self):
        self._has_game_started = True
        if self._is_game_over:
            self._reset()

        if self._is_paused:
            self._button_widget.update_btn_text(
                btn_type=self._button_widget.BUTTON_TYPE.start,
                text='PAUSE',
            )
            self._start_current_player_time()
            self._is_paused = False
            self._board_widget.is_paused = self._is_paused
        else:
            self._button_widget.update_btn_text(
                btn_type=self._button_widget.BUTTON_TYPE.start,
                text='START',
            )
            self._stop_all_timers()
            self._is_paused = True
            self._board_widget.is_paused = self._is_paused

    def _first_btn_clicked(self):
        self._inspect_history(start=True)

    def _previous_btn_clicked(self):
        self._inspect_history(cursor_step=-1)

    def _next_btn_clicked(self):
        self._inspect_history(cursor_step=1)

    def _last_btn_clicked(self):
        self._inspect_history(end=True)

    def _white_resign_btn_clicked(self):
        self._resign(winning_color=c.Color.black)

    def _black_resign_btn_clicked(self):
        self._resign(winning_color=c.Color.white)

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

    def _timer_white_timeout(self):
        self._remaining_time_white -= 1
        if self._remaining_time_white == 0:
            self.game_over(winner=c.Color.black)
            white_wins = False
            self.GAME_OVER_SIGNAL.emit(white_wins)
            self._moves_widget.display_win(c.Color.black)

        self._board_widget.display_time_white(self._remaining_time_white)

    def _timer_black_timeout(self):
        self._remaining_time_black -= 1
        if self._remaining_time_black == 0:
            self.game_over(winner=c.Color.white)
            white_wins = True
            self.GAME_OVER_SIGNAL.emit(white_wins)
            self._moves_widget.display_win(c.Color.white)

        self._board_widget.display_time_black(self._remaining_time_black)

    def _add_bonus_time(self):
        if self._current_player == c.Color.white:
            self._remaining_time_white += self._bonus_time
            self._board_widget.display_time_white(self._remaining_time_white)
        else:
            self._remaining_time_black += self._bonus_time
            self._board_widget.display_time_black(self._remaining_time_black)

    def _set_options(self):
        self._bonus_time = self._option_widget.bonus_time

        self._remaining_time_white = self._option_widget.play_time * 60
        self._board_widget.display_time_white(self._remaining_time_white)

        self._remaining_time_black = self._option_widget.play_time * 60
        self._board_widget.display_time_black(self._remaining_time_black)

        self.GAME_OPTIONS_SET_SIGNAL.emit(
            (
                self._option_widget.white_promotion,
                self._option_widget.black_promotion,
                self._option_widget.is_standard_type,
            )
        )

    def _resign(self, winning_color):
        if not self._has_game_started:
            return

        if self._is_game_over:
            return

        self.game_over(winning_color)
        white_wins = True
        if winning_color == c.Color.black:
            white_wins = False

        self.GAME_OVER_SIGNAL.emit(white_wins)
        self._moves_widget.display_win(winning_color)

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

        not_at_end = not(self._history_player.is_at_end)
        self._board_widget.inspecting_history = not_at_end
        self._board_widget.board.data = result.board.data
        self._board_widget.board.reverse = result.board.reverse
        self.update_board()

        if result.move is not None:
            self._board_widget.highlight_move(
                src=result.move.src,
                dst=result.move.dst,
            )

        index = self._history_player.current_index
        self._moves_widget.highlight_move(move_index=index)
