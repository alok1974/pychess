import getpass
from datetime import datetime
import collections

from PySide2 import QtWidgets, QtCore


from .. import constant as c
from ..core.history import Player as HistoryPlayer
from ..core.pgn import MOVES2PGN, PGN2MOVES
from ..core.engineer import Engine


from .widgets import (
    BoardWidget,
    OptionWidget,
    MoveWidget,
    LoadGameWidget,
    SaveGameDataWidget,
    ChoosePlayerWidget,
    ToolBar,
    SelectPromotionWidget,
)


GAME_OPTIONS = collections.namedtuple(
    'GAME_OPTIONS',
    [
        'white_promotion',
        'black_promotion',
        'is_standard'
    ]
)


class MainWidget(QtWidgets.QDialog):
    MOVE_SIGNAL = QtCore.Signal(tuple)
    GAME_RESET_SIGNAL = QtCore.Signal()
    UPDATE_BOARD_SIGNAL = QtCore.Signal()
    GAME_OPTIONS_SET_SIGNAL = QtCore.Signal(tuple)
    GAME_OVER_SIGNAL = QtCore.Signal(bool)
    BULK_MOVE_SIGNAL = QtCore.Signal(tuple)

    def __init__(self, board, parent=None):
        super().__init__(parent=parent)
        self._board = board
        self._board_widget = BoardWidget(board=self._board)
        self._moves_widget = MoveWidget()
        self._tool_bar = ToolBar()

        self._collapsed_width = None
        self._history_player = None
        self._engine_color = None
        self._engine = Engine()
        self._board = board

        self._current_player = c.Color.white
        self._winner = None
        self._bonus_time = c.GAME.DEFAULT_BONUS_TIME
        self._timer_white = QtCore.QTimer()
        self._timer_white.setInterval(1000)  # timeout per 1 second
        self._remaining_time_white = c.GAME.DEFAULT_PLAY_TIME * 60

        self._timer_black = QtCore.QTimer()
        self._timer_black.setInterval(1000)  # timeout per 1 second
        self._remaining_time_black = c.GAME.DEFAULT_PLAY_TIME * 60

        self._is_paused = False
        self._is_game_over = False
        self._has_game_started = False
        self._game_loaded = False

        self._game_data = None
        self._history_player = None
        self._inspecting_history = False
        self._move_index = None

        self._white_player_name = getpass.getuser().capitalize()
        self._black_player_name = 'Opponent'
        self._game_date = None

        self._is_flipped = False

        # Custom Options
        self._custom_options_set = False
        self._custom_bonus_time = None
        self._custom_play_time = None
        self._custom_white_promotion = None
        self._custom_black_promotion = None
        self._custom_is_standard_type = None

        self._setup_ui()
        self._connect_signals()

        self._reset()

    def _reset(self):
        self.GAME_RESET_SIGNAL.emit()

        self._board_widget.reset()
        self._moves_widget.reset()

        self._engine_color = None
        self._history_player = None

        self._current_player = c.Color.white
        self._winner = None
        self._bonus_time = c.GAME.DEFAULT_BONUS_TIME
        self._timer_white.stop()
        self._remaining_time_white = c.GAME.DEFAULT_PLAY_TIME * 60

        self._timer_black.stop()
        self._remaining_time_black = c.GAME.DEFAULT_PLAY_TIME * 60

        self._is_paused = False
        self._is_game_over = False
        self._has_game_started = False
        self._game_loaded = False

        self._game_data = None
        self._history_player = None
        self._inspecting_history = False
        self._move_index = None

        self._white_player_name = getpass.getuser().capitalize()
        self._black_player_name = 'Opponent'
        self._game_date = None

        self._is_flipped = False

        self._board_widget.display_time_white(self._remaining_time_white)
        self._board_widget.display_time_black(self._remaining_time_black)

        self._toggle_left_widget(visibility=False)
        self._tool_bar.toogle_pause_icon(is_paused=self._is_paused)
        self._tool_bar.setVisible(True)
        self._adjust_size()

    def _reset_custom_options(self):
        self._custom_options_set = False
        self._custom_bonus_time = None
        self._custom_play_time = None
        self._custom_white_promotion = None
        self._custom_black_promotion = None
        self._custom_is_standard_type = None

    def update_move(self, game_data):
        self._game_data = game_data
        self._display_pgn_moves()
        self._board_widget.update_move(game_data=self._game_data)

    def update_invalid_move(self):
        self._board_widget.update_invalid_move()

    def set_current_player(self, color):
        self._add_bonus_time()
        self._stop_current_player_time()
        self._current_player = color
        self._board_widget.set_current_player(color)
        self._start_current_player_time()
        self._handle_engine_move()

    def _handle_engine_move(self):
        if self._engine_color is None:
            return

        if self._current_player != self._engine_color:
            return

        moves = [(m.src, m.dst) for m in self._game_data.move_history]
        best_move = self._engine.get_best_move(moves)
        if best_move is None:
            return

        self.MOVE_SIGNAL.emit((best_move, None))

    def update_board(self):
        self._board_widget.update_board()

    def game_over(self, winner):
        self._set_game_over()
        self._board_widget.game_over(winner)

    def stalemate(self):
        self._set_game_over()
        self._board_widget.stalemate()
        self._moves_widget.display_win(winning_text='1/2-1/2')

    def promotion_required(self, move_spec):
        w = SelectPromotionWidget(color=self._current_player)
        w.SELECTED_PROMOTION_SIGNAL.connect(
            lambda piece_type: self._recieved_move_string(
                move_string=move_spec,
                promotion=piece_type,
            ),
        )
        w.show()

    def resizeEvent(self, event):
        if self._is_paused:
            return

        if self._game_loaded or self._has_game_started:
            self._handle_left_widget()

    def mouseDoubleClickEvent(self, event):
        if self._is_paused:
            return

        if not self._has_game_started:
            return

        self._tool_bar.setVisible(True)
        self._toggle_left_widget()

    def keyPressEvent(self, event):
        self._handle_keypress(event=event)

    @staticmethod
    def _is_key_pressed(event, key, modifier=None):
        result = event.key() == key
        if modifier is not None:
            result = result and event.modifiers() == modifier
        return result

    def _setup_ui(self):
        self.setStyleSheet('border: none;')
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self._right_widget = self._create_right_widget()
        self._left_widget = self._create_left_widget()

        layout.addWidget(self._right_widget, 1)
        layout.addWidget(self._left_widget, 2)

    def _create_right_widget(self):
        widget = QtWidgets.QWidget()
        widget.setStyleSheet('border: none;')
        layout = QtWidgets.QHBoxLayout(widget)
        layout.addWidget(self._tool_bar)
        layout.addWidget(self._board_widget, 1)
        return widget

    def _create_left_widget(self):
        # Create a left widget
        widget = QtWidgets.QWidget()
        widget.setStyleSheet('border: none;')

        # Create left widget toggle btn
        self._collapse_btn = QtWidgets.QPushButton('<')
        self._collapse_btn.setStyleSheet('border: 1px solid rgb(90, 90, 90);')
        self._collapse_btn.setFixedWidth(c.APP.COLLAPSE_BTN_WIDTH)

        layout = QtWidgets.QHBoxLayout(widget)
        layout.addWidget(self._collapse_btn)
        layout.addWidget(self._moves_widget, 1)

        return widget

    def _connect_signals(self):
        # Board Widget signals
        bw = self._board_widget
        bw.MOVE_SIGNAL.connect(self._recieved_move_string)
        bw.RESIGN_BTN_CLICKED_SIGNAL.connect(self._resign)
        bw.ANIM_IN_PROGRESS_SIGNAL.connect(self._anim_in_progress)
        bw.ANIM_FINISHED_SIGNAL.connect(self._anim_finished)

        # Move Widget Signals
        mw = self._moves_widget
        mw.KEYPRESS_SIGNAL.connect(self._handle_keypress)
        mw.MOVE_SELECTED_SIGNAL.connect(self._move_selected)
        mw.FIRST_BTN_CLICKED_SIGNAL.connect(self._first_btn_clicked)
        mw.PREV_BTN_CLICKED_SIGNAL.connect(self._previous_btn_clicked)
        mw.NEXT_BTN_CLICKED_SIGNAL.connect(self._next_btn_clicked)
        mw.LAST_BTN_CLICKED_SIGNAL.connect(self._last_btn_clicked)

        # Toolbar Signals
        self._tool_bar.BTN_CLICKED_SIGNAL.connect(self._handle_command)

        # Internal Signals
        self._timer_white.timeout.connect(self._timer_white_timeout)
        self._timer_black.timeout.connect(self._timer_black_timeout)
        self._collapse_btn.clicked.connect(self._collapse_btn_clicked)

    def _handle_left_widget(self):
        if self._collapsed_width is None:
            return

        width_increased = self.width() > self._collapsed_width
        left_widget_is_hidden = not self._left_widget.isVisible()
        if width_increased and left_widget_is_hidden:
            self._tool_bar.setVisible(True)
            self._left_widget.setVisible(True)
            self._display_pgn_moves()
            self._collapse_btn.setVisible(True)
            self._collapse_btn.setText('<')

    def _toggle_left_widget(self, visibility=None):
        if visibility is not None:
            vis_to_set = visibility
        else:
            vis_to_set = not self._left_widget.isVisible()

        self._left_widget.setVisible(vis_to_set)
        self._collapse_btn.setVisible(vis_to_set)

        if vis_to_set:
            self._collapse_btn.setVisible(vis_to_set)
            self._collapse_btn.setText('<')
            self._display_pgn_moves()

    def _recieved_move_string(self, move_string, promotion=None):
        self.MOVE_SIGNAL.emit((move_string, promotion))

    def _move_selected(self, move_index):
        self._inspect_history(index=move_index)

    def _toggle_pause(self):
        if not self._has_game_started:
            return

        if self._is_game_over:
            return

        if self._is_paused:
            self._resume_game()
        else:
            self._pause_game()

        self._tool_bar.toogle_pause_icon(is_paused=self._is_paused)

    def _first_btn_clicked(self):
        self._inspect_history(start=True)

    def _previous_btn_clicked(self):
        self._inspect_history(cursor_step=-1)

    def _next_btn_clicked(self):
        self._inspect_history(cursor_step=1)

    def _last_btn_clicked(self):
        self._inspect_history(end=True)

    def _collapse_btn_clicked(self):
        if not self._has_game_started:
            return

        self._tool_bar.setVisible(False)
        self._toggle_left_widget()
        self._adjust_size()
        self._collapsed_width = self.width()

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
            self._moves_widget.display_win(winner=c.Color.black)

        self._board_widget.display_time_white(self._remaining_time_white)

    def _timer_black_timeout(self):
        self._remaining_time_black -= 1
        if self._remaining_time_black == 0:
            self.game_over(winner=c.Color.white)
            white_wins = True
            self.GAME_OVER_SIGNAL.emit(white_wins)
            self._moves_widget.display_win(winner=c.Color.white)

        self._board_widget.display_time_black(self._remaining_time_black)

    def _add_bonus_time(self):
        if self._current_player == c.Color.white:
            self._remaining_time_white += self._bonus_time
            self._board_widget.display_time_white(self._remaining_time_white)
        else:
            self._remaining_time_black += self._bonus_time
            self._board_widget.display_time_black(self._remaining_time_black)

    def _set_options(self, options):
        self._custom_options_set = True
        self._custom_bonus_time = options.bonus_time
        self._custom_play_time = options.play_time
        self._custom_white_promotion = options.white_promotion
        self._custom_black_promotion = options.black_promotion
        self._custom_is_standard_type = options.is_standard_type

    def _resign(self, winning_color):
        if self._is_paused:
            return

        if self._is_game_over:
            return

        self.game_over(winning_color)
        white_wins = True
        if winning_color == c.Color.black:
            white_wins = False

        self.GAME_OVER_SIGNAL.emit(white_wins)
        self._moves_widget.display_win(winner=winning_color)

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

        self._move_index = self._history_player.current_index
        self._moves_widget.highlight_move(move_index=self._move_index)

    def _toggle_show_threatened(self):
        self._board_widget.toggle_show_threatened()

    @staticmethod
    def _get_pgn2moves():
        msg_box = QtWidgets.QMessageBox()
        msg_box.setText("Please select a PGN game file")
        msg_box.exec_()

        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            parent=None,
            caption='Load game (.pgn)',
            filter='*.pgn'

        )
        if not file_path:
            return

        return PGN2MOVES(pgn_file_path=file_path)

    def _handle_load_game(self):
        if self._has_game_started:
            return

        pgn2moves = self._get_pgn2moves()
        if pgn2moves is None:
            return

        self._pgn2moves = pgn2moves

        if self._pgn2moves.nb_games == 1:
            self._load_game()
        else:
            game_info = self._pgn2moves.short_info
            w = LoadGameWidget(game_info=game_info, parent=self)
            w.SELECTED_GAME_SIGNAL.connect(self._load_game)
            w.show()

    def _handle_make_movie(self):
        if self._has_game_started:
            return

        pgn2moves = self._get_pgn2moves()
        if pgn2moves is None:
            return

        self._pgn2moves = pgn2moves
        if self._pgn2moves.nb_games == 1:
            self._make_movie()
        else:
            game_info = self._pgn2moves.short_info
            w = LoadGameWidget(game_info=game_info, parent=self)
            w.SELECTED_GAME_SIGNAL.connect(self._make_movie)
            w.show()

    def _load_game(self, game_index=0):
        if game_index == -1:  # No game was selected
            return

        self._reset()
        self._game_loaded = True
        self._board_widget.game_loaded = True
        moves = self._pgn2moves.get_moves(game_index=game_index)
        bulk_moves = [
            (f'{src.address}{dst.address}', promotion)
            for src, dst, promotion in moves
        ]
        self.BULK_MOVE_SIGNAL.emit(bulk_moves)
        self._stop_all_timers()

        header = self._pgn2moves.header_info[game_index]
        result = header.result
        self._moves_widget.display_win(winning_text=result)
        self._white_player_name = header.white
        self._black_player_name = header.black
        self._game_date = header.date
        self._moves_widget.set_game_info(
            white=self._white_player_name,
            black=self._black_player_name,
            date=self._game_date,
            result=result,
        )

        self._board_widget.set_panel_visibility(False)
        self._toggle_left_widget(visibility=True)
        self._collapse_btn.setVisible(False)
        self._adjust_size()

        self._inspect_history(start=True)

    def _make_movie(self, game_index=0):
        if game_index == -1:  # No game was selected
            return

        msg_box = QtWidgets.QMessageBox()
        msg_box.setText("Please select the save location for the movie file")
        msg_box.exec_()

        movie_file_path, _ = QtWidgets.QFileDialog.getSaveFileName(
            parent=None,
            caption='Create movie (.mp4)',
            filter='*.mp4'

        )
        if not movie_file_path:
            return

        self._pgn2moves.create_movie(
            game_index=game_index,
            movie_file_path=movie_file_path,
        )

    def _handle_save_game(self):
        if self._game_loaded:
            return
        if self._game_data is None:
            return
        elif not self._game_data.move_history:
            return

        w = SaveGameDataWidget(
            parent=self,
            white=self._white_player_name,
            black=self._black_player_name,
            date=self._game_date,
        )
        w.DONE_SIGNAL.connect(self._save_game)
        w.show()

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
        if not file_path:
            return

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

    def _choose_player(self):
        if self._has_game_started:
            return

        w = ChoosePlayerWidget(parent=self)
        w.CHOSEN_COLOR_SIGNAL.connect(
            lambda color: self._start_new_game(engine_color=color)
        )
        w.HUMAN_VS_HUMAN_SIGNAL.connect(self._start_new_game)
        w.show()

    def _open_options(self):
        if self._has_game_started or self._board_widget.game_loaded:
            return

        self._reset_custom_options()
        w = OptionWidget(parent=self)
        w.OPTIONS_SET_SIGNAL.connect(self._set_options)
        w.show()

    def _update_ui_for_start(self):
        # NOTE: The order of widget initialization below
        # is important otherwise the move widget does not fill
        # the whole space
        self._toggle_left_widget(visibility=True)
        self._set_game_info()
        self._left_widget.adjustSize()
        self._moves_widget.adjustSize()
        self._board_widget.ready_to_start()
        self.adjustSize()
        self.adjustPosition(self)

    def _update_data_for_start(self, engine_color=None):
        self._reset()
        result = self._set_custom_options(engine_color=engine_color)
        if not result:
            return False

        self._update_game_info(engine_color=engine_color)
        self._resume_game()
        self._has_game_started = True

        return True

    def _set_custom_options(self, engine_color=None):
        if not self._custom_options_set:
            return True

        valid_engine_game = self._check_valid_engine_game(engine_color)
        if not valid_engine_game:
            return False

        self._bonus_time = self._custom_bonus_time
        self._remaining_time_white = self._custom_play_time * 60
        self._remaining_time_black = self._custom_play_time * 60

        game_options = GAME_OPTIONS(
            white_promotion=self._custom_white_promotion,
            black_promotion=self._custom_black_promotion,
            is_standard=self._custom_is_standard_type,
        )
        self.GAME_OPTIONS_SET_SIGNAL.emit(game_options)
        return True

    def _check_valid_engine_game(self, engine_color=None):
        engine_set = engine_color is not None
        chess960 = not self._custom_is_standard_type
        if engine_set and chess960:
            msg_box = QtWidgets.QMessageBox()
            msg_box.setText(
                'Currently, Chess 960 format is not available '
                'while playing against computer. It might be implemented '
                'in future. For now, please select the standard format '
                'for playing against computer.'
            )
            msg_box.exec_()
            return False
        return True

    def _update_game_info(self, engine_color=None):
        self._game_date = datetime.now().strftime('%Y.%m.%d')

        if engine_color is None:
            return

        if engine_color == c.Color.white:
            self._white_player_name = 'Computer'
            self._black_player_name = getpass.getuser().capitalize()
        else:
            self._White_player_name = getpass.getuser().capitalize()
            self._black_player_name = 'Computer'

    def _update_engine_for_start(self, engine_color):
        if engine_color is None:
            return

        self._engine_color = engine_color
        self._board_widget.engine_color = engine_color
        if self._engine_color == c.Color.white:
            best_move = self._engine.get_best_move()
            if best_move is not None:
                self.MOVE_SIGNAL.emit((best_move, None))

    def _start_new_game(self, engine_color=None):
        result = self._update_data_for_start(engine_color=engine_color)
        if not result:
            # Something went wrong while updating the start data
            return

        self._update_ui_for_start()
        self._update_engine_for_start(engine_color=engine_color)

    def _set_game_info(self):
        self._moves_widget.set_game_info(
            white=self._white_player_name,
            black=self._black_player_name,
            date=self._game_date,
        )

    def _resume_game(self):
        self._start_current_player_time()
        self._is_paused = False
        self._board_widget.is_paused = self._is_paused
        self._toggle_left_widget(visibility=True)
        self._adjust_size()

    def _pause_game(self):
        self._stop_all_timers()
        self._is_paused = True
        self._board_widget.is_paused = self._is_paused
        self._toggle_left_widget(visibility=False)
        self._adjust_size()

    def _display_pgn_moves(self):
        if self._game_data is None:
            return

        self._history_player = HistoryPlayer(self._game_data.move_history)
        moves = MOVES2PGN(self._game_data.move_history).moves
        self._moves_widget.display_moves(moves)

    def _handle_reset(self):
        if self._has_game_started:
            msg_box = QtWidgets.QMessageBox()
            result = msg_box.question(
                self,
                'Reset Game?',
                'There is a game in progress, '
                'do you really want to reset?',
                QtWidgets.QMessageBox.Yes,
                QtWidgets.QMessageBox.Cancel,
            )
            if result != QtWidgets.QMessageBox.Yes:
                return
        self._reset()

    def _handle_keypress(self, event):
        keys = QtCore.Qt
        if self._is_key_pressed(event, keys.Key_C):
            self._toggle_show_threatened()

        if self._is_key_pressed(event, keys.Key_S, keys.ControlModifier):
            self._handle_save_game()

        if self._is_key_pressed(event, keys.Key_O, keys.ControlModifier):
            self._handle_load_game()

        if self._is_key_pressed(event, keys.Key_R, keys.ControlModifier):
            self._handle_reset()

        if self._is_key_pressed(event, keys.Key_T, keys.ControlModifier):
            self._open_options()

        if self._is_key_pressed(event, keys.Key_N, keys.ControlModifier):
            self._choose_player()

        if self._is_key_pressed(event, keys.Key_P, keys.ControlModifier):
            self._toggle_pause()

        if self._is_key_pressed(event, keys.Key_B, keys.ControlModifier):
            self._toggle_adress()

    def _adjust_size(self):
        self._left_widget.adjustSize()
        self._moves_widget.adjustSize()
        self._board_widget.adjustSize()
        self._right_widget.adjustSize()
        self.adjustSize()
        self.adjustPosition(self)

    def _toggle_adress(self):
        if self._is_paused:
            return

        if self._has_game_started or self._game_loaded:
            self._board_widget.toggle_address()

    def _anim_in_progress(self):
        self._stop_current_player_time()

    def _anim_finished(self):
        if self._move_index is not None and self._move_index == -1:
            self.update_board()

        if self._is_game_over or self._is_paused:
            return

        self._start_current_player_time()

    def _handle_command(self, cmd):
        if cmd == c.ToolCommand.reset:
            self._handle_reset()
        elif cmd == c.ToolCommand.new:
            self._choose_player()
        elif cmd == c.ToolCommand.load:
            self._handle_load_game()
        elif cmd == c.ToolCommand.option:
            self._open_options()
        elif cmd == c.ToolCommand.border:
            self._toggle_adress()
        elif cmd == c.ToolCommand.pause:
            self._toggle_pause()
        elif cmd == c.ToolCommand.save:
            self._handle_save_game()
        elif cmd == c.ToolCommand.threat:
            self._toggle_show_threatened()
        elif cmd == c.ToolCommand.zen:
            self._collapse_btn_clicked()
        elif cmd == c.ToolCommand.movie:
            self._handle_make_movie()
        elif cmd == c.ToolCommand.flip:
            self._handle_flip()

    def _set_game_over(self, winner=None):
        self._winner = winner
        self._is_game_over = True
        self._has_game_started = False
        self._stop_all_timers()
        self._toggle_left_widget(visibility=True)
        self._tool_bar.setVisible(True)

    def _handle_flip(self):
        if not self._has_game_started:
            return

        self._is_flipped = not self._is_flipped
        self._board_widget.is_flipped = self._is_flipped
