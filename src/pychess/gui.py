from PySide2 import QtWidgets, QtCore, QtGui


from . import constant as c, imager
from .squarer import Square


class MainWindow(QtWidgets.QDialog):
    MOVE_SIGNAL = QtCore.Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent=parent)

    def init_board(self, board):
        self._board = board
        self._board_image = imager.BoardImage(self._board, size=600)

        self._first_square = None
        self._second_square = None

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
        x, y = event.x(), event.y()
        square = self._pixel_to_square(x, y)
        if square is None:
            return

        if self._first_square is None:
            self._first_square = square
        elif self._second_square is None:
            self._second_square = square
        else:
            pass
            # Both squares are filled and we are ready to move

        both_cell_selected = all([self._first_square, self._second_square])

        button = event.button()
        signal = None
        if button == QtCore.Qt.MouseButton.RightButton:
            pass
        else:
            signal = self.MOVE_SIGNAL

        if signal is not None and both_cell_selected:
            move = f'{self._first_square.address}{self._second_square.address}'
            signal.emit(move)
            self.clear_moves()

    def clear_moves(self):
        self._first_square = None
        self._second_square = None

    def update(self):
        self._board_image.update()
        self._pixmap = QtGui.QPixmap.fromImage(self._board_image.qt_image)
        self._image_label.setPixmap(self._pixmap)

    def _pixel_to_square(self, x, y):
        resize_factor = float(
            self._board_image.height / c.IMAGE.BASE_IMAGE_SIZE
        )

        square_size = int(c.IMAGE.SQUARE_SIZE * resize_factor)
        border_size = int(c.IMAGE.BORDER_SIZE * resize_factor)

        pixel_on_border = self._pixel_on_border(
            square_size=square_size,
            nb_squares=c.IMAGE.NB_SQUARES,
            border_size=border_size,
            x=x,
            y=y,
        )

        if pixel_on_border:
            self._first_square = None
            self._second_square = None
            return

        square_x = int((x - border_size) / square_size)
        square_y = c.IMAGE.NB_SQUARES - 1 - int(
            (y - border_size) / square_size
        )
        return Square((square_x, square_y))

    def _pixel_on_border(self, square_size, nb_squares, border_size, x, y):
        return (
            (x - border_size) < 0 or
            (y - border_size) < 0 or
            (x > (border_size + (nb_squares * square_size))) or
            (y > (border_size + (nb_squares * square_size)))
        )

    def mousePressEvent(self, event):
        # NOTE: This event will be fired only when
        # the user has clicke somewhere in the gui
        # OUTSIDE of the chess board image. We can
        # easily clear the first and the second square
        # selections
        self._first_square = None
        self._second_square = None
