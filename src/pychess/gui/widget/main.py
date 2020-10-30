from PySide2 import QtWidgets, QtCore


from .board import BoardWidget
from .buttons import ButtonWidget
from .moves import MoveWidget
from ...engineer import Engine
from ... import constant as c


class MainWidget(QtWidgets.QDialog):
    MOVE_SIGNAL = QtCore.Signal(str)
    GAME_RESET_SIGNAL = QtCore.Signal()
    UPDATE_BOARD_SIGNAL = QtCore.Signal()
    GAME_OPTIONS_SET_SIGNAL = QtCore.Signal(tuple)
    GAME_OVER_SIGNAL = QtCore.Signal(bool)
    BULK_MOVE_SIGNAL = QtCore.Signal(tuple)

    def __init__(self, board, parent=None):
        super().__init__(parent=parent)
        self._board_widget = BoardWidget(board=board)
        self._board_widget.init_board()
        self._button_widget = ButtonWidget()
        self._moves_widget = MoveWidget()
        self._moves_widget.display_moves(moves=[])
        self._setup_ui()
        self._connect_signals()

    def init_board(self, board):
        self._engine_color = None
        self._engine = Engine()
        self._board = board

        self._game_loaded = False
        self._current_player = c.Color.white
        self._winner = None

        self._bonus_time = 0  # self._option_widget.bonus_time

        self._timer_white = QtCore.QTimer()
        self._timer_white.setInterval(1000)  # timeout per 1 second
        self._remaining_time_white = 0  # self._option_widget.play_time * 60

        self._timer_black = QtCore.QTimer()
        self._timer_black.setInterval(1000)  # timeout per 1 second
        self._remaining_time_black = 0  # self._option_widget.play_time * 60

        self._is_paused = True
        self._is_game_over = False
        self._has_game_started = False

        self._game_data = None
        self._history_player = None
        self._show_threatened = False

        self._inspecting_history = False

        self._setup_ui()
        self._connect_signals()

    def update_move(self, game_data):
        self._board_widget.update_move(game_data=game_data)

    def update_invalid_move(self):
        self._board_widget.update_invalid_move()

    def set_current_player(self, color):
        self._current_player = color
        self._board_widget.set_current_player(color)

    def _setup_ui(self):
        self._main_layout = QtWidgets.QHBoxLayout(self)
        self._left_layout = QtWidgets.QVBoxLayout()
        self._left_layout.addWidget(self._moves_widget, 2)
        # self._left_layout.addStretch(1)
        self._left_layout.addWidget(self._button_widget, 1)

        self._main_layout.addWidget(self._board_widget, 1)
        self._main_layout.addLayout(self._left_layout, 2)

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

    def _recieved_move_string(self, move_string):
        print(f'recieved move {move_string}')
        self.MOVE_SIGNAL.emit(move_string)

    def _move_selected(self, move_index):
        print(f'Selected move index: {move_index}')

    def _option_btn_clicked(self):
        print('option btn clicked')

    def _ai_btn_clicked(self):
        print('ai btn clicked')

    def _start_btn_clicked(self):
        print('start btn clicked')

    def _first_btn_clicked(self):
        print('first btn clicked')

    def _previous_btn_clicked(self):
        print('previous btn clicked')

    def _next_btn_clicked(self):
        print('next btn clicked')

    def _last_btn_clicked(self):
        print('last btn clicked')

    def _white_resign_btn_clicked(self):
        print('white resign btn clicked')

    def _black_resign_btn_clicked(self):
        print('black resign btn clicked')
