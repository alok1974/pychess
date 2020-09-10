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
        self._board_image = imager.BoardImage(self._board, size=600)

        self._first_square = None
        self._second_square = None

        self._current_player = c.Color.white

        self._setup_ui()
        self._timer = QtCore.QTimer()
        self._time = 0
        self._connect_signals()

    def _setup_ui(self):
        self.setWindowTitle(c.APP.NAME)
        self.setStyleSheet(c.APP.STYLESHEET)
        self.setFixedSize(
            self._board_image.qt_image.width() + 40,
            self._board_image.qt_image.height() + 140
        )

        self._main_layout = QtWidgets.QVBoxLayout(self)

        # Add top layout
        self._top_layout = self._create_top_layout()
        self._main_layout.addLayout(self._top_layout)

        # Add image layout
        self._image_layout_outer = self._create_image_layout()
        self._main_layout.addLayout(self._image_layout_outer)

        # Add bottom layout
        self._bottom_layout = self._create_bottom_layout()
        self._main_layout.addLayout(self._bottom_layout)

        # Move focus away from the line edits
        # self._restart_image_label.setFocus()

    def _create_top_layout(self):
        self._top_layout = QtWidgets.QHBoxLayout()
        return self._top_layout

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

    def _create_bottom_layout(self):
        self._bottom_layout = QtWidgets.QHBoxLayout()
        return self._bottom_layout

    def _connect_signals(self):
        self._image_label.mousePressEvent = self._on_image_clicked

    def _on_image_clicked(self, event):
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

    def update_move(self, move):
        src, dst = move
        self._update()
        self._highlight(src, highlight_color=c.APP.HIGHLIGHT_COLOR.src)
        self._highlight(dst, highlight_color=c.APP.HIGHLIGHT_COLOR.dst)
        self.clear_moves()

    def set_current_player(self, color):
        self._current_player = color

    def _update_image_label(self):
        self._pixmap = QtGui.QPixmap.fromImage(self._board_image.qt_image)
        self._image_label.setPixmap(self._pixmap)

    def mousePressEvent(self, event):
        # NOTE: This event will be fired only when
        # the user has clicke somewhere in the gui
        # OUTSIDE of the chess board image. We can
        # easily clear the first and the second square
        # selections
        self._first_square = None
        self._second_square = None
