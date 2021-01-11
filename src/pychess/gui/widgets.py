import os
import shutil
import contextlib
import collections
import functools
import re
import itertools
import random


from PySide2 import QtWidgets, QtCore, QtGui
from PIL import Image


from .. import constant as c
from ..core.pgn import REGEX, NAMEDTUPLES
from . import imager


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


RECT_DATA = collections.namedtuple(
    'RECT_DATA',
    ['width', 'height', 'extra_width', 'extra_height'],
)


class BoardImageLabel(QtWidgets.QLabel):
    NB_RANDOMS = 12

    def __init__(self, pixmap, parent=None):
        super().__init__(parent=parent)
        self._pychess_pixmap = QtGui.QPixmap(
            c.IMAGE.PYCHESS_IMAGE_FILE_PATH,
        )
        self.setPixmap(pixmap)
        self.setSizePolicy(
            QtWidgets.QSizePolicy.MinimumExpanding,
            QtWidgets.QSizePolicy.MinimumExpanding,
        )

        self._draw_splash = True
        self._grid_iter = list(
            itertools.product(
                range(c.IMAGE.NB_SQUARES),
                range(c.IMAGE.NB_SQUARES),
            ),
        )

        self._grid_colors = self._get_grid_color_map()
        self._grid_max = c.IMAGE.NB_SQUARES - 1

        randoms = self._grid_iter[:]
        random.shuffle(randoms)
        self._randoms = randoms[:self.NB_RANDOMS]

        self._border_size = 2

        self._hue = 0
        self._hue_timer = QtCore.QTimer()
        self._hue_timer.timeout.connect(self._hue_change)
        self._hue_timer.start()

        self._color_timer = QtCore.QTimer()
        self._color_timer.setInterval(500)
        self._color_timer.timeout.connect(self._randomize_colors)
        self._color_timer.start()

        self._random_timer = QtCore.QTimer()
        self._random_timer.setInterval(500)
        self._random_timer.timeout.connect(self._randomize_squares)
        self._random_timer.start()

        self._current_band_no = 2
        self._current_band = self._get_band(self._current_band_no)
        self._band_timer = QtCore.QTimer()
        self._band_timer.setInterval(500)
        self._band_timer.timeout.connect(self._change_band)
        self._band_timer.start()

    @property
    def draw_splash(self):
        return self._draw_splash

    @draw_splash.setter
    def draw_splash(self, val):
        self._draw_splash = val

    def setPixmap(self, pixmap):
        self.pixmap = pixmap
        super().setPixmap(self.pixmap)

    def paintEvent(self, event):
        size = self.size()
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.TextAntialiasing)
        painter.setRenderHint(QtGui.QPainter.SmoothPixmapTransform)
        painter.setRenderHint(QtGui.QPainter.HighQualityAntialiasing)

        if self._draw_splash:
            self._draw_grid(size=size, painter=painter)
            self._draw_rays(size=size, painter=painter)
            self._draw_overlay(size=size, painter=painter)
        else:
            self._draw_pixmap(size=size, painter=painter)

        painter.end()
        painter = None

    def _draw_pixmap(self, size, painter):
        point = QtCore.QPoint(0, 0)
        scaled_pixmap = self.pixmap.scaled(
            size,
            QtCore.Qt.KeepAspectRatio,
            transformMode=QtCore.Qt.SmoothTransformation,
        )

        point.setX((size.width() - scaled_pixmap.width()) / 2)
        point.setY((size.height() - scaled_pixmap.height()) / 2)

        painter.setRenderHint(QtGui.QPainter.TextAntialiasing)
        painter.setRenderHint(QtGui.QPainter.SmoothPixmapTransform)
        painter.setRenderHint(QtGui.QPainter.HighQualityAntialiasing)
        painter.drawPixmap(point, scaled_pixmap)

    def _draw_rays(self, size, painter):
        lcolor = QtGui.QColor()
        lcolor.setHsv(self._hue, 100, 255, 60)
        painter.setBrush(lcolor)
        painter.setPen(lcolor)

        center_x = (
                int((size.width() - self._pychess_pixmap.width()) / 2) +
                c.IMAGE.PYCHESS_FOCUS[0]
        )
        center_y = (
                int((size.height() - self._pychess_pixmap.height()) / 2) +
                c.IMAGE.PYCHESS_FOCUS[1]
        )

        sign_x = random.choice([-1, 1])
        x_mult = random.randint(0, 100)
        x = sign_x * size.width() * x_mult / 100

        sign_y = random.choice([-1, 1])
        y_mult = random.randint(0, 100)
        y = sign_y * size.height() * y_mult / 100

        painter.drawLine(
            center_x,
            center_y,
            center_x + x,
            center_y + y,
        )

    def _draw_grid(self, size, painter):
        rect_data = self._get_rect_data(
            size=size,
            nb_squares=c.IMAGE.NB_SQUARES,
            border=self._border_size,
        )

        last_row, last_column = max(self._grid_iter)
        for row, column in self._grid_iter:
            is_random = (row, column) in self._randoms
            is_band = (row, column) in self._current_band
            to_color = is_random or is_band

            if to_color:
                qcolor = QtGui.QColor()
                qcolor.setHsv(self._hue, 100, 120)
            else:
                color = self._grid_colors[(row, column)]
                qcolor = QtGui.QColor(*color)

            painter.setBrush(qcolor)
            painter.setPen(qcolor)

            draw_width = rect_data.width
            if row == last_row:
                draw_width = rect_data.width + rect_data.extra_width

            draw_height = rect_data.height
            if column == last_column:
                draw_height = rect_data.height + rect_data.extra_height

            x, y = self._get_rect_position(
                row=row,
                column=column,
                width=rect_data.width,
                height=rect_data.height,
                border=self._border_size
            )
            painter.drawRect(x, y, draw_width, draw_height)

    @staticmethod
    def _get_band(band_no):
        box_1 = list(itertools.product(range(3, 5), range(3, 5)))
        box_2 = list(itertools.product(range(2, 6), range(2, 6)))
        box_3 = list(itertools.product(range(1, 7), range(1, 7)))
        box_4 = list(itertools.product(range(8), range(8)))
        if band_no == 0:
            return box_1
        elif band_no == 1:
            return list(set(box_2) - set(box_1))
        elif band_no == 2:
            return list(set(box_3) - set(box_2))
        elif band_no == 3:
            return list(set(box_4) - set(box_3))
        else:
            raise ValueError(f'Band No.{band_no} is defined!')

    @staticmethod
    def _get_rect_data(size, nb_squares, border):
        """
        Given a width, height, number of sqaures and border size between
        the squares, returns the size of the rectangles and the extra width
        and height left after all borders and rectangle sizes are considered
        """
        w, h = size.width(), size.height()
        n = nb_squares
        b = border
        width = int((w - ((n + 1) * b)) / n)
        height = int((h - ((n + 1) * b)) / n)
        extra_width = w - (((n + 1)) * b + (n * width))
        extra_height = h - (((n + 1)) * b + (n * height))

        return RECT_DATA(
            width=width,
            height=height,
            extra_width=extra_width,
            extra_height=extra_height
        )

    @staticmethod
    def _get_rect_position(row, column, width, height, border):
        x = ((row + 1) * border) + (row * width)
        y = ((column + 1) * border) + (column * height)
        return x, y

    def _hue_change(self):
        self._hue += 0.7
        if self._hue > 359:
            self._hue = 0

        self.setStyleSheet(f'background-color:hsv({self._hue}, 255, 60);')

    @staticmethod
    def _get_grid_color_map():
        n = c.IMAGE.NB_SQUARES
        image = Image.open(c.IMAGE.GRID_IMAGE_FILE_PATH)
        square_size = int(c.IMAGE.BASE_IMAGE_SIZE / n)
        coords = imager.Coordinates(
            border_size=0,
            square_size=square_size,
        )
        colors = {}
        for row, column in itertools.product(range(n), range(n)):
            pixel_pos = coords.square_to_pixel(row, column)
            colors[(row, column)] = image.getpixel(pixel_pos)

        return colors

    def _randomize_colors(self):
        values = list(self._grid_colors.values())[:]
        random.shuffle(values)
        keys = list(self._grid_colors.keys())[:]
        self._grid_colors.clear()
        self._grid_colors = dict([(k, v) for k, v in zip(keys, values)])

    def _randomize_squares(self):
        randoms = self._grid_iter[:]
        random.shuffle(randoms)
        self._randoms = self._prune_neighbors(randoms[:self.NB_RANDOMS])

    def _prune_neighbors(self, squares):
        first_random = random.randint(0, len(squares) - 1)
        pruned = [squares.pop(first_random)]
        for row, column in squares:
            if self._is_neigbour((row, column), pruned):
                continue
            else:
                pruned.append((row, column))
        return pruned

    @staticmethod
    def _is_neigbour(square, squares):
        if square[0] in [s[0] for s in squares]:
            for y in [s[1] for s in squares]:
                if square[1] in (y - 1, y + 1):
                    return True
        if square[1] in [s[1] for s in squares]:
            for x in [s[0] for s in squares]:
                if square[0] in (x - 1, x + 1):
                    return True
        return False

    def _change_band(self):
        self._current_band_no -= 1
        if self._current_band_no < 0:
            self._current_band_no = 2

        self._current_band = self._get_band(band_no=self._current_band_no)

    def _draw_overlay(self, size, painter):
        center = QtCore.QPoint(0, 0)
        center.setX((size.width() - self._pychess_pixmap.width()) / 2)
        center.setY((size.height() - self._pychess_pixmap.height()) / 2)
        painter.drawPixmap(center, self._pychess_pixmap)


class SmoothImageLabel(QtWidgets.QLabel):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

    def setPixmap(self, pixmap):
        self.pixmap = pixmap
        super().setPixmap(pixmap)

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.HighQualityAntialiasing)
        painter.drawPixmap(0, 0, self.pixmap)
        painter.end()
        painter = None


class ButtonLabel(QtWidgets.QLabel):
    def __init__(self, default_pixmap, active_pixmap, parent=None):
        super().__init__(parent=parent)
        self._default_pixmap = default_pixmap
        self._active_pixmap = active_pixmap

        self._set_default()

        self.setSizePolicy(
            QtWidgets.QSizePolicy.MinimumExpanding,
            QtWidgets.QSizePolicy.MinimumExpanding,
        )
        self.setStyleSheet('QToolTip {font-size: 14px;}')

    def set_active(self, pixmap):
        self._active_pixmap = pixmap
        self._set_active()

    def set_default(self, pixmap):
        self._default_pixmap = pixmap
        self._set_default()

    def enterEvent(self, event):
        self._set_active()

    def leaveEvent(self, event):
        self._set_default()

    def _set_active(self):
        self.pixmap = self._active_pixmap
        self.setPixmap(self._active_pixmap)

    def _set_default(self):
        self.pixmap = self._default_pixmap
        self.setPixmap(self._default_pixmap)

    def paintEvent(self, event):
        size = self.size()
        painter = QtGui.QPainter(self)

        point = QtCore.QPoint(0, 0)
        scaled_pixmap = self.pixmap.scaled(
            size,
            QtCore.Qt.KeepAspectRatio,
            transformMode=QtCore.Qt.SmoothTransformation,
        )

        point.setX((size.width() - scaled_pixmap.width()) / 2)
        point.setY((size.height() - scaled_pixmap.height()) / 2)

        painter.setRenderHint(QtGui.QPainter.TextAntialiasing)
        painter.setRenderHint(QtGui.QPainter.SmoothPixmapTransform)
        painter.setRenderHint(QtGui.QPainter.HighQualityAntialiasing)
        painter.drawPixmap(point, scaled_pixmap)

        painter.end()
        painter = None


class ToolBar(QtWidgets.QWidget):
    BTN_CLICKED_SIGNAL = QtCore.Signal(c.ToolCommand)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self._setup_ui()

    def _setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        self._buttons = {}
        for image_data in c.IMAGE.BTN_IMAGE:
            if image_data.cmd == c.ToolCommand.play:
                continue
            default_pixmap = QtGui.QPixmap(
                os.path.join(c.IMAGE.IMAGE_DIR, image_data.default)
            )
            active_pixmap = QtGui.QPixmap(
                os.path.join(c.IMAGE.IMAGE_DIR, image_data.active)
            )
            btn = ButtonLabel(
                default_pixmap=default_pixmap,
                active_pixmap=active_pixmap,
            )
            btn.setToolTip(image_data.tooltip)
            btn.setSizePolicy(
                QtWidgets.QSizePolicy.Expanding,
                QtWidgets.QSizePolicy.Expanding,
            )
            btn.mousePressEvent = functools.partial(
                self._btn_label_clicked,
                cmd=image_data.cmd,
            )

            self._buttons[image_data.cmd] = btn
            layout.addWidget(btn)

    def _btn_label_clicked(self, event, cmd):
        self.BTN_CLICKED_SIGNAL.emit(cmd)

    def toogle_pause_icon(self, is_paused):
        if is_paused:
            default_icon = c.IMAGE.BTN_IMAGE.play.default
            active_icon = c.IMAGE.BTN_IMAGE.play.active
        else:
            default_icon = c.IMAGE.BTN_IMAGE.pause.default
            active_icon = c.IMAGE.BTN_IMAGE.pause.active

        default_pixmap = QtGui.QPixmap(
            os.path.join(
                c.IMAGE.IMAGE_DIR,
                default_icon,
            )
        )
        active_pixmap = QtGui.QPixmap(
            os.path.join(
                c.IMAGE.IMAGE_DIR,
                active_icon,
            )
        )

        btn = self._buttons[c.ToolCommand.pause]
        btn.set_active(active_pixmap)
        btn.set_default(default_pixmap)


class ChoosePlayerWidget(QtWidgets.QDialog):
    CHOSEN_COLOR_SIGNAL = QtCore.Signal(c.Color)
    HUMAN_VS_HUMAN_SIGNAL = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self._parent = parent
        self._engine_exists = self._check_engine_exists()
        self._setup_ui()
        self._connect_signals()

    def _check_engine_exists(self):
        exe = shutil.which(c.APP.STOCKFISH_EXE_NAME)
        if exe is not None:
            return os.path.exists(exe)
        return False

    def _setup_ui(self):
        self.setStyleSheet(c.APP.STYLESHEET)
        self.setWindowTitle('Choose Players')
        self.setMaximumSize(c.APP.MOVE_WIDGET_WIDTH, c.APP.MOVE_WIDGET_WIDTH)
        self.setModal(True)

        self._main_layout = QtWidgets.QVBoxLayout(self)

        self._human_vs_human_btn = self._create_btn()
        self._main_layout.addWidget(self._human_vs_human_btn)

        if not self._engine_exists:
            return

        self._human_vs_computer_btn = self._create_btn(c.Color.black)
        self._main_layout.addWidget(self._human_vs_computer_btn)

        self._computer_vs_human_btn = self._create_btn(c.Color.white)
        self._main_layout.addWidget(self._computer_vs_human_btn)

    def _connect_signals(self):
        self._human_vs_human_btn.clicked.connect(
            lambda: self._set_player()
        )

        if not self._engine_exists:
            return

        self._computer_vs_human_btn.clicked.connect(
            lambda: self._set_player(c.Color.white)
        )

        self._human_vs_computer_btn.clicked.connect(
            lambda: self._set_player(c.Color.black)
        )

    def _set_player(self, color=None):
        if color is None:
            self.HUMAN_VS_HUMAN_SIGNAL.emit()
        else:
            self.CHOSEN_COLOR_SIGNAL.emit(color)

        self.close()

    @staticmethod
    def _create_btn(color=None):
        if color is None:
            btn_text = 'Human vs. Human'
        else:
            if color == c.Color.white:
                btn_text = 'Computer vs. Human'
            else:
                btn_text = 'Human vs. Computer'

        btn = QtWidgets.QPushButton(btn_text)
        btn.setMinimumWidth(c.APP.AI_BTN_WIDTH)
        btn.setMinimumHeight(c.APP.AI_BTN_HEIGHT)
        btn.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Expanding,
        )
        return btn


class BoardWidget(QtWidgets.QDialog):
    MOVE_SIGNAL = QtCore.Signal(str)
    RESIGN_BTN_CLICKED_SIGNAL = QtCore.Signal(c.Color)
    ANIM_IN_PROGRESS_SIGNAL = QtCore.Signal()
    ANIM_FINISHED_SIGNAL = QtCore.Signal()

    def __init__(self, board, parent=None):
        super().__init__(parent=parent)
        self._board = board
        self._board_image = imager.BoardImage(self._board)
        self._board_image.FRAME_UPDATED_SIGNAL.connect(self._animate_move)
        self._board_image.ANIM_FINISHED_SIGNAL.connect(self._animation_done)
        self._captured_image = imager.CapturedImage()
        self._splash_pixmap = QtGui.QPixmap(c.IMAGE.SPLASH_IMAGE_FILE_PATH)
        self._pychess_pixmap = QtGui.QPixmap(c.IMAGE.PYCHESS_IMAGE_FILE_PATH)

        self._setup_ui()
        self._connect_signals()

        self.reset()

    @property
    def board(self):
        return self._board

    @property
    def image_height(self):
        return self._board_image.image.height

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
        self._handle_pause()

    @property
    def is_flipped(self):
        return self._is_flipped

    @is_flipped.setter
    def is_flipped(self, val):
        self._is_flipped = val
        self._handle_flip()

    @property
    def game_loaded(self):
        return self._game_loaded

    @game_loaded.setter
    def game_loaded(self, val):
        self._game_loaded = val

    @property
    def engine_color(self):
        return self._engine_color

    @engine_color.setter
    def engine_color(self, val):
        self._engine_color = val

    def update_board(self):
        self._update()

    def reset(self):
        self._board_image = imager.BoardImage(self._board)
        self._board_image.FRAME_UPDATED_SIGNAL.connect(self._animate_move)
        self._board_image.ANIM_FINISHED_SIGNAL.connect(self._animation_done)
        self._captured_image = imager.CapturedImage()

        self._board_image.update()
        self._update_captured_image_labels()

        self._first_square = None
        self._second_square = None

        self._current_player = c.Color.white

        self._game_data = None
        self._game_loaded = False
        self._is_paused = True
        self._is_game_over = False
        self._engine_color = None

        self._show_threatened = False
        self._inspecting_history = False

        self._is_flipped = False

        self._white_timer_lcd.display(
            self._format_time(c.GAME.DEFAULT_PLAY_TIME * 60)
        )
        self._black_timer_lcd.display(
            self._format_time(c.GAME.DEFAULT_PLAY_TIME * 60)
        )

        self.set_panel_visibility(False)
        self._update_splash()
        self.adjustSize()

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

    def update_move(self, game_data):
        self._game_data = game_data

        if self.game_loaded:
            self.update_board()
        else:
            self.ANIM_IN_PROGRESS_SIGNAL.emit()
            self._board_image.animate_move(
                self._game_data.src,
                self._game_data.dst
            )

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

    def mousePressEvent(self, event):
        # NOTE: This event will be fired only when
        # the user has clicke somewhere in the gui
        # OUTSIDE of the chess board image. We can
        # safely clear the first and the second square
        # selections
        self._first_square = None
        self._second_square = None

    def game_over(self, winner):
        self._set_game_over(winner=winner)

    def stalemate(self):
        self._set_game_over(is_stalemate=True)

    def _set_game_over(self, winner=None, is_stalemate=False):
        self._winner = winner
        self._is_game_over = True

        if is_stalemate:
            self._captured_image.draw_stalemate()
        else:
            self._captured_image.draw_winner(winner)

        self._update_captured_image_labels()

        self.ANIM_FINISHED_SIGNAL.emit()

    def display_time_white(self, seconds=None):
        self._white_timer_lcd.display(
            self._format_time(total_seconds=seconds)
        )

    def display_time_black(self, seconds=None):
        self._black_timer_lcd.display(
            self._format_time(total_seconds=seconds)
        )

    def toggle_show_threatened(self):
        self._show_threatened = not self._show_threatened

        if not self._show_threatened:
            self._hide_threatened()
        else:
            self._display_threatened()

    def set_panel_visibility(self, visibility):
        self._white_panel_widget.setVisible(visibility)
        self._black_panel_widget.setVisible(visibility)
        self._captured_label_white.setVisible(visibility)
        self._captured_label_black.setVisible(visibility)

    def ready_to_start(self):
        self._update_image_label()
        self.set_panel_visibility(True)
        self.adjustSize()

    def _setup_ui(self):
        self.setStyleSheet('border: none;')
        self._main_layout = QtWidgets.QVBoxLayout(self)

        # Add black panel widget
        (
            self._black_panel_widget,
            self._black_timer_lcd,
            self._black_resign_btn
        ) = self._create_panel_widget(color=c.Color.black)
        self._main_layout.addWidget(self._black_panel_widget)

        # Add white capture image
        self._captured_pixmap_white = QtGui.QPixmap.fromImage(
            self._captured_image.qt_image_white)
        self._captured_label_white = SmoothImageLabel()
        self._captured_label_white.setPixmap(self._captured_pixmap_white)

        self._main_layout.addWidget(self._captured_label_white)

        # Add main board image
        self._image_widget = self._create_image_widget()
        self._main_layout.addWidget(self._image_widget)

        # Add black capture image
        self._captured_pixmap_black = QtGui.QPixmap.fromImage(
            self._captured_image.qt_image_black
        )
        self._captured_label_black = SmoothImageLabel()
        self._captured_label_black.setPixmap(self._captured_pixmap_black)
        self._main_layout.addWidget(self._captured_label_black)

        # Add white panel widget
        (
            self._white_panel_widget,
            self._white_timer_lcd,
            self._white_resign_btn,
        ) = self._create_panel_widget(color=c.Color.white)
        self._main_layout.addWidget(self._white_panel_widget)

    def _create_image_widget(self):
        widget = QtWidgets.QWidget()
        # Create Pixmap
        self._pixmap = QtGui.QPixmap.fromImage(self._board_image.qt_image)

        # Create Label and add the pixmap
        self._image_label = BoardImageLabel(pixmap=self._pixmap)
        self._image_label.setCursor(
            QtGui.QCursor(QtCore.Qt.PointingHandCursor)
        )

        layout = QtWidgets.QVBoxLayout(widget)
        layout.addWidget(self._image_label)

        return widget

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

        return widget, lcd, btn

    @staticmethod
    def _create_lcd(color, min_height=None):
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

    @staticmethod
    def _create_btn(text, min_height=None):
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
        self._image_label.mousePressEvent = self._image_clicked
        self._white_resign_btn.clicked.connect(self._white_resign_btn_clicked)
        self._black_resign_btn.clicked.connect(self._black_resign_btn_clicked)

    def _animate_move(self):
        self._update_image_label()

    def _animation_done(self):
        if self._show_threatened:
            self._display_threatened()
        else:
            self._hide_threatened()

        self.highlight_move(src=self._game_data.src, dst=self._game_data.dst)
        self._board_image.clear_selection()
        self.ANIM_FINISHED_SIGNAL.emit()

    def toggle_address(self):
        self._board_image.toggle_address()
        self._update_image_label()
        return

    def _image_clicked(self, event):
        if not self._is_image_clickable():
            return

        if self._board_image.is_border_clicked(event.x(), event.y()):
            self.toggle_address()
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

    def _white_resign_btn_clicked(self):
        self.RESIGN_BTN_CLICKED_SIGNAL.emit(c.Color.black)

    def _black_resign_btn_clicked(self):
        self.RESIGN_BTN_CLICKED_SIGNAL.emit(c.Color.white)

    def _is_image_clickable(self):
        is_engine_move = False
        if self._engine_color is not None:
            is_engine_move = self._current_player == self._engine_color
        return not any(
            [
                is_engine_move,
                self._game_loaded,
                self._is_paused,
                self._is_game_over,
                self._inspecting_history,
            ]
        )

    def _is_selection_valid(self, square):
        if square is None:
            return False

        if self._board_image.board.is_empty(square):
            return False

        selected_color = self._board_image.board.get_piece(square).color
        if selected_color != self._current_player:
            return False

        return True

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

        all_threatened = []
        capturables = self._game_data.capturables[color]
        for _, threatened in capturables.items():
            all_threatened.extend(threatened)

        all_threatened = list(set(all_threatened))

        return all_threatened

    def _update_image_label(self):
        self._image_label.draw_splash = False
        self._pixmap = QtGui.QPixmap.fromImage(self._board_image.qt_image)
        self._image_label.setPixmap(self._pixmap)

    def _update_splash(self):
        self._image_label.draw_splash = True

    def _update_captured_image_labels(self):
        self._captured_pixmap_white = QtGui.QPixmap.fromImage(
            self._captured_image.qt_image_white)
        self._captured_label_white.setPixmap(self._captured_pixmap_white)

        self._captured_pixmap_black = QtGui.QPixmap.fromImage(
            self._captured_image.qt_image_black)
        self._captured_label_black.setPixmap(self._captured_pixmap_black)

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

    def _handle_pause(self):
        self._board_image.is_paused = self._is_paused
        if not self._is_paused and self._game_data is not None:
            self.highlight_move(
                src=self._game_data.src,
                dst=self._game_data.dst,
            )

        self._update_image_label()

        self.set_panel_visibility(not self._is_paused)
        self.adjustSize()

    def _handle_flip(self):
        self._handle_ui_flip()
        self._handle_board_image_flip()

    def _handle_board_image_flip(self):
        self._board_image.is_flipped = self._is_flipped
        if self._game_data is not None:
            self.highlight_move(
                src=self._game_data.src,
                dst=self._game_data.dst,
            )

        self._update_image_label()

    def _handle_ui_flip(self):
        if self._is_flipped:
            widgets = [
                self._white_panel_widget,
                self._captured_label_black,
                self._image_widget,
                self._captured_label_white,
                self._black_panel_widget,

            ]
        else:
            widgets = [
                self._black_panel_widget,
                self._captured_label_white,
                self._image_widget,
                self._captured_label_black,
                self._white_panel_widget,
            ]

        for index, w in enumerate(widgets):
            self._main_layout.removeWidget(w)
            self._main_layout.insertWidget(index, w)


class LoadGameWidget(QtWidgets.QDialog):
    SELECTED_GAME_SIGNAL = QtCore.Signal(int)

    def __init__(self, game_info, parent=None):
        super().__init__(parent=parent)
        self._game_info = game_info
        self._title = (
            'Click on game to load '
            f'({len(self._game_info)} games found in the file)'
        )
        self._selected_index = -1
        self._setup_ui()

    def _setup_ui(self):
        self.setWindowTitle(self._title)
        self.setModal(True)

        self._main_layout = QtWidgets.QVBoxLayout(self)

        self._scroll_area = QtWidgets.QScrollArea()
        self._scroll_area.setSizePolicy(
            QtWidgets.QSizePolicy.Fixed,
            QtWidgets.QSizePolicy.Expanding,
        )

        self._scroll_widget = QtWidgets.QWidget()
        self._scroll_widget.setSizePolicy(
            QtWidgets.QSizePolicy.Fixed,
            QtWidgets.QSizePolicy.Expanding,
        )

        self._scroll_area.setVerticalScrollBarPolicy(
            QtCore.Qt.ScrollBarAsNeeded
        )
        self._scroll_area.setHorizontalScrollBarPolicy(
            QtCore.Qt.ScrollBarAlwaysOff
        )

        h_scroll_bar = self._scroll_area.horizontalScrollBar()
        h_scroll_bar.setStyleSheet(
            """
            QWidget {
                border: 1px solid  rgb(90, 90, 90);
                color: rgb(100, 18, 20);
            }
            """
        )

        self._game_data_layout = QtWidgets.QVBoxLayout()
        self._game_data_layout.setContentsMargins(0, 0, 0, 0)
        for index, game_data in enumerate(self._game_info):
            btn_text = f'\n{game_data}\n'
            btn = QtWidgets.QPushButton(btn_text)
            btn.setMinimumWidth(c.APP.MOVE_WIDGET_WIDTH)
            btn.setSizePolicy(
                QtWidgets.QSizePolicy.Fixed,
                QtWidgets.QSizePolicy.Expanding,
            )
            func = functools.partial(
                self._btn_clicked,
                index=index
            )
            btn.clicked.connect(func)
            self._game_data_layout.addWidget(btn)

        self._scroll_widget.setLayout(self._game_data_layout)
        self._scroll_area.setWidget(self._scroll_widget)
        self._main_layout.addWidget(self._scroll_area)

    def _add_btn(self, add_to_layout, index, game_data):
        serial_text = str(index + 1).zfill(len(str(len(self._game_info))))
        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        s_no_label = QtWidgets.QLabel(serial_text)
        s_no_label.setStyleSheet('border: 1px solid rgb(90, 90, 90);')
        s_no_label.setMinimumWidth(int(c.APP.MOVE_WIDGET_WIDTH / 4))

        layout.addWidget(s_no_label)
        btn_text = f'\n{game_data}\n'
        btn = QtWidgets.QPushButton(btn_text)
        btn.setStyleSheet('border: 1px solid rgb(90, 90, 90);')
        btn.setMinimumWidth(c.APP.MOVE_WIDGET_WIDTH)
        btn.setSizePolicy(
            QtWidgets.QSizePolicy.Fixed,
            QtWidgets.QSizePolicy.Expanding,
        )
        func = functools.partial(
            self._btn_clicked,
            index=index
        )
        btn.clicked.connect(func)
        layout.addWidget(btn)
        spacer_label = QtWidgets.QLabel(' ')
        layout.addWidget(spacer_label)
        add_to_layout.addLayout(layout)

    def _btn_clicked(self, index):
        self._selected_index = index
        self.close()

    def showEvent(self, event):
        self._scroll_area.adjustSize()
        self._scroll_widget.adjustSize()
        self.adjustSize()
        self.setFixedWidth(self.sizeHint().width())

    def closeEvent(self, event):
        self.SELECTED_GAME_SIGNAL.emit(self._selected_index)


class MoveWidget(QtWidgets.QDialog):
    MOVE_SELECTED_SIGNAL = QtCore.Signal(int)
    FIRST_BTN_CLICKED_SIGNAL = QtCore.Signal()
    PREV_BTN_CLICKED_SIGNAL = QtCore.Signal()
    NEXT_BTN_CLICKED_SIGNAL = QtCore.Signal()
    LAST_BTN_CLICKED_SIGNAL = QtCore.Signal()
    KEYPRESS_SIGNAL = QtCore.Signal(QtCore.QEvent)

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

    def keyPressEvent(self, event):
        # Relay back the keypress events
        # NOTE: This fixed the problem when the move widget
        # was being closed when the escape key was pressed
        self.KEYPRESS_SIGNAL.emit(event)

    def reset(self):
        self._cursor_pos_map = {}
        self._move_index_word_data = {}
        self._last_highlighted = None
        self._textedit.clear()

    def display_win(self, winning_text=None, winner=None):
        winning_text = winning_text or self._get_winning_text(winner=winner)
        self._add_winning_text_at_end(winning_text)

    @staticmethod
    def _get_winning_text(winner=None):
        winning_text = None
        if winner is None:
            winning_text = '1/2-1/2'
        elif winner == c.Color.black:
            winning_text = '0-1'
        else:
            winning_text = '1-0'
        return winning_text

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

            winning_text, move_string = self._extract_winning_text(move_string)
            cur_pos += len(move_string)

            self._textedit.insertPlainText(move_string)
            if winning_text is not None:
                self._add_winning_text_at_end(winning_text)

    @staticmethod
    def _extract_winning_text(move_string):
        if move_string.strip().endswith('1-0'):
            move_string = move_string.replace('1-0', '')
            winning_text = '1-0'
        elif move_string.strip().endswith('0-1'):
            move_string = move_string.replace('0-1', '')
            winning_text = '0-1'
        elif move_string.strip().endswith('1/2-1/2'):
            move_string = move_string.replace('1/2-1/2', '')
            winning_text = '1/2-1/2'
        else:
            winning_text = None

        return winning_text, move_string

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
                else:
                    unicode_symbol = ''
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

    def set_game_info(self, white, black, date, result=None):
        white = self._format_player_name(white)
        black = self._format_player_name(black)

        text = f' White: {white}\n Black: {black}\n Date: {date}'
        if result is not None:
            text = f'{text}, Result: {result}'
        self._game_info_label.setText(text)

    @staticmethod
    def _format_player_name(name):
        return ' '.join([n.strip() for n in name.split(',')])

    def _setup_ui(self):
        self.setStyleSheet('border: none;')
        self.setMinimumWidth(c.APP.MOVE_WIDGET_WIDTH)
        self.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Expanding,
        )

        self._main_layout = QtWidgets.QVBoxLayout(self)

        self._game_info_label = QtWidgets.QLabel('GAME INFO')
        self._game_info_label.setStyleSheet(
            'border: 1px solid rgb(90, 90, 90);'
            'font-size: 14px;'
        )
        self._game_info_label.setMinimumHeight(70)
        self._main_layout.addWidget(self._game_info_label)

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

    def showEvent(self, event):
        # Force loading of fonts at init time
        self._textedit.insertPlainText('Initializing ...')
        self._textedit.clear()

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
        self._textedit.mousePressEvent = self._mouse_press_event

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

    def _mouse_press_event(self, event):
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
        char_format.setForeground(QtGui.QBrush(QtGui.QColor(221, 221, 221)))
        char_format.setBackground(QtGui.QBrush(QtGui.QColor(255, 0, 0)))
        char_format.setFontWeight(QtGui.QFont.Bold)
        return char_format

    @staticmethod
    def _plain_format():
        char_format = QtGui.QTextCharFormat()
        char_format.setForeground(QtGui.QBrush(QtGui.QColor(221, 221, 221)))
        char_format.setBackground(QtGui.QBrush(QtGui.QColor(25, 25, 25)))
        char_format.setFontWeight(QtGui.QFont.Normal)
        return char_format

    @staticmethod
    def _winning_format():
        char_format = QtGui.QTextCharFormat()
        char_format.setForeground(QtGui.QBrush(QtGui.QColor(255, 20, 10)))
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

        self._format(
            start=word_data.start,
            length=word_data.length,
            char_format=char_format,
        )

    def _format(self, start, length, char_format):
        cursor = self._textedit.textCursor()
        cursor.setPosition(start)
        cursor.movePosition(
            QtGui.QTextCursor.NextCharacter,
            QtGui.QTextCursor.KeepAnchor,
            length,
        )
        cursor.mergeCharFormat(char_format)

        self._reset_format()

    def _add_winning_text_at_end(self, winning_text):
        start = self._textedit.document().characterCount() - 1
        length = len(winning_text)
        char_format = self._winning_format()
        self._textedit.insertPlainText(winning_text)
        self._format(
            start=start,
            length=length,
            char_format=char_format,
        )

    def _reset_format(self):
        self._textedit.setTextColor(QtGui.QColor(221, 221, 221))
        self._textedit.setTextBackgroundColor(QtGui.QColor(25, 25, 25))


class OptionWidget(QtWidgets.QDialog):
    PROMOTION_PIECES = [
        None,
        c.PieceType.queen,
        c.PieceType.rook,
        c.PieceType.bishop,
        c.PieceType.knight,
    ]

    OPTIONS_SET_SIGNAL = QtCore.Signal(tuple)

    OPTIONS = collections.namedtuple(
        'OPTIONS',
        [
            'play_time',
            'bonus_time',
            'is_standard_type',
            'white_promotion',
            'black_promotion',
        ]
    )

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self._default_play_time = c.GAME.DEFAULT_PLAY_TIME
        self._default_bonus_time = c.GAME.DEFAULT_BONUS_TIME

        self._play_time = self._default_play_time
        self._bonus_time = self._default_bonus_time

        self._default_white_promotion = None
        self._default_black_promotion = None

        self._is_standard_type = True
        self._white_promotion = self._default_white_promotion
        self._black_promotion = self._default_black_promotion

        self._image_store = {}
        self._setup_ui()
        self._connect_signals()

    def reset(self):
        self._play_time = self._default_play_time
        self._bonus_time = self._default_bonus_time
        self._is_standard_type = True
        self._white_promotion = self._default_white_promotion
        self._black_promotion = self._default_black_promotion

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

            self._white_promotion_combobox.setCurrentIndex(0)
            self._black_promotion_combobox.setCurrentIndex(0)

    def _setup_ui(self):
        self.setModal(True)
        self._main_layout = QtWidgets.QVBoxLayout(self)

        time_widget = self._create_time_widget()
        self._main_layout.addWidget(time_widget)

        self._main_layout.addSpacerItem(
            QtWidgets.QSpacerItem(1, 20),
        )

        game_widget = self._create_game_widget()
        self._main_layout.addWidget(game_widget)

        self._main_layout.addSpacerItem(
            QtWidgets.QSpacerItem(1, 20),
        )

        promotion_widget = self._create_promotion_widget()
        self._main_layout.addWidget(promotion_widget)

    def _create_time_widget(self):
        widget = QtWidgets.QWidget()
        widget.setMaximumHeight(220)
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
            QtWidgets.QSpacerItem(1, 20)
        )
        layout.addLayout(bonus_time_layout)

        return widget

    def _create_game_widget(self):
        widget = QtWidgets.QWidget()
        widget.setMaximumHeight(100)
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
        widget.setMaximumHeight(150)
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
        combobox.setMinimumWidth(200)
        combobox.setMinimumHeight(30)

        for item in self.PROMOTION_PIECES:
            if item is None:
                combobox.addItem('CHOOSE DURING GAME', '')
            else:
                combobox.addItem(
                    self._create_icon(f'{item.name}_small', color),
                    '',
                )

        layout.addWidget(label)
        layout.addWidget(combobox)
        layout.addStretch(1)

        return layout, combobox

    @staticmethod
    def _create_icon(piece_name, color):
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

    @staticmethod
    def _create_slider(min_val, max_val, default_val, step=1):
        slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        slider.setMinimum(min_val)
        slider.setMaximum(max_val)
        slider.setSingleStep(step)
        slider.setMinimumWidth(300)
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
            self._play_time_slider_changed
        )

        self._bonus_time_slider.valueChanged.connect(
            self._bonus_time_slider_changed
        )

        self._chess960_button.toggled.connect(
            lambda: self._game_type_btn_toggled(self._chess960_button)
        )

        self._standard_button.toggled.connect(
            lambda: self._game_type_btn_toggled(self._standard_button)
        )

        self._black_promotion_combobox.currentIndexChanged.connect(
            self._black_combo_index_changed,
        )

        self._white_promotion_combobox.currentIndexChanged.connect(
            self._white_combo_index_changed,
        )

    def _play_time_slider_changed(self, val):
        self._play_time = val
        self._play_time_slider_value_label.setText(f'{str(val).zfill(2)} min')

    def _bonus_time_slider_changed(self, val):
        self._bonus_time = val
        self._bonus_time_slider_value_label.setText(f'{str(val).zfill(2)} sec')

    def _game_type_btn_toggled(self, btn):
        if btn.text() == c.GAME.TYPE.std:
            self._is_standard_type = btn.isChecked()

        if btn.text() == c.GAME.TYPE.c9lx:
            self._is_standard_type = not btn.isChecked()

    def _white_combo_index_changed(self, index):
        self._white_promotion = self.PROMOTION_PIECES[index]

    def _black_combo_index_changed(self, index):
        self._black_promotion = self.PROMOTION_PIECES[index]

    def closeEvent(self, event):
        options = self.OPTIONS(
            play_time=self._play_time,
            bonus_time=self._bonus_time,
            is_standard_type=self._is_standard_type,
            white_promotion=self._white_promotion,
            black_promotion=self._black_promotion,
        )
        self.OPTIONS_SET_SIGNAL.emit(options)


class SaveGameDataWidget(QtWidgets.QDialog):
    DONE_SIGNAL = QtCore.Signal(tuple)

    PGN_GAME_INFO = collections.namedtuple(
        'GAME_DATA',
        [
            'event', 'site', 'date', 'round', 'black', 'white'
        ]
    )

    def __init__(self, parent=None, white=None, black=None, date=None):
        super().__init__(parent=parent)
        self._event = ''
        self._site = ''
        self._date = date or ''
        self._round = ''
        self._white = white or ''
        self._black = black or ''

        self._force_quit = False

        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        self.setStyleSheet(c.APP.STYLESHEET)
        self.windowTitle = 'Enter game details'
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

        empty_label = QtWidgets.QLabel('  ')
        empty_label.setMinimumHeight(c.APP.MEDIUM_HEIGHT)
        self._main_layout.addWidget(empty_label)

        self._save_btn = self._create_btn('Save Game')
        self._main_layout.addWidget(self._save_btn)

    @staticmethod
    def _create_btn(text):
        btn = QtWidgets.QPushButton(text)
        btn.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Fixed,
        )
        btn.setMinimumHeight(c.APP.MEDIUM_HEIGHT)
        return btn

    def _connect_signals(self):
        self._save_btn.clicked.connect(self._save_btn_clicked)

    def _save_btn_clicked(self):
        data = [
            self._event_text.text(), self._site_text.text(),
            self._date_text.text(), self._round_text.text(),
            self._white_text.text(), self._black_text.text(),
        ]

        if not all(data):
            msg_box = QtWidgets.QMessageBox()
            msg_box.setText("Missing details! Please fill all fields.")
            msg_box.exec_()
            return

        game_data = self.PGN_GAME_INFO(
            event=self._event_text.text(),
            site=self._site_text.text(),
            date=self._date_text.text(),
            round=self._round_text.text(),
            white=self._white_text.text(),
            black=self._black_text.text(),
        )
        self.DONE_SIGNAL.emit(game_data)
        self.close()

    @staticmethod
    def _get_current_date():
        from datetime import datetime
        n = datetime.now()
        return f'{n.year}.{n.month}.{n.day}'

    @staticmethod
    def _create_field(name, default_val=''):
        layout = QtWidgets.QHBoxLayout()
        label = QtWidgets.QLabel(name)
        label.setMinimumSize(
            c.APP.MEDIUM_HEIGHT * 4,
            c.APP.MEDIUM_HEIGHT,
        )
        line_edit = QtWidgets.QLineEdit(default_val)
        line_edit.setMinimumSize(
            c.APP.MEDIUM_HEIGHT * 4,
            c.APP.MEDIUM_HEIGHT,
        )
        line_edit.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Fixed,
        )
        layout.addWidget(label)
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
            self._date_text.setText(self._date)
            self._round_text.setText('1')
            self._white_text.setText(self._white)
            self._black_text.setText(self._black)

        self.setFixedHeight(self.sizeHint().height())


class SelectPromotionWidget(QtWidgets.QDialog):
    PROMOTION_PIECES = [
        c.PieceType.queen,
        c.PieceType.rook,
        c.PieceType.bishop,
        c.PieceType.knight,
    ]

    SELECTED_PROMOTION_SIGNAL = QtCore.Signal(c.PieceType)

    def __init__(self, color, parent=None):
        super().__init__(parent=parent)
        self._color = color
        self._promotion = None
        self.setModal(True)
        self._setup_ui()

    def _setup_ui(self):
        self.setWindowTitle('SELECT A PROMOTION TYPE')
        self.setStyleSheet('border: none;')

        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        for piece_type in self.PROMOTION_PIECES:
            piece_image = self._get_piece_image_path(
                piece_type=piece_type,
                color=self._color,
            )
            default_pixmap = QtGui.QPixmap(piece_image)

            piece_image_active = self._get_piece_image_path(
                piece_type=piece_type,
                color=self._color,
                active=True,
            )
            active_pixmap = QtGui.QPixmap(piece_image_active)
            btn = ButtonLabel(
                default_pixmap=default_pixmap,
                active_pixmap=active_pixmap,
            )

            btn.setToolTip(f'Promote to {piece_type.name}')
            btn.setSizePolicy(
                QtWidgets.QSizePolicy.Expanding,
                QtWidgets.QSizePolicy.Expanding,
            )
            btn.setStyleSheet('border: none;')
            btn.mousePressEvent = functools.partial(
                self._btn_label_clicked,
                piece_type=piece_type,
            )

            layout.addWidget(btn)
            layout.addStretch(1)

    @staticmethod
    def _get_piece_image_path(piece_type, color, active=False):
        piece_name = piece_type.name
        color_name = color.name
        piece_images = getattr(c.IMAGE.PROMOTION_IMAGE, piece_name)
        image_data = getattr(piece_images, color_name)
        if active:
            image_name = getattr(image_data, 'active')
        else:
            image_name = getattr(image_data, 'default')
        return os.path.join(c.IMAGE.IMAGE_DIR, image_name)

    def _btn_label_clicked(self, event, piece_type):
        self._promotion = piece_type
        self.close()

    def showEvent(self, event):
        self.adjustSize()
        self.setFixedWidth(self.sizeHint().width())

    def closeEvent(self, event):
        if self._promotion is None:
            msg_box = QtWidgets.QMessageBox()
            msg_box.setText("Please select a promotion type")
            msg_box.exec_()
            event.ignore()
            return

        self.SELECTED_PROMOTION_SIGNAL.emit(self._promotion)
