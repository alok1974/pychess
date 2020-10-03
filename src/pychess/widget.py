import os
import contextlib


from PySide2 import QtWidgets, QtCore, QtGui


from . import constant as c


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
        # self.setStyleSheet(c.APP.STYLESHEET)
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


class MovesWidget(QtWidgets.QWidget):
    def __init__(self, resize_factor, parent=None):
        super().__init__(parent=parent)
        self._resize_factor = resize_factor
        self._init_scroll_height = 20
        self._scroll_bar_height = 10
        self._scroll_bar_active = False
        self._labels = []
        self._labels_scroll_pos = {}
        self._move_num_labels = []
        self._setup_ui()
        self._connect_signals()

    def reset(self):
        self._clear_labels()
        self._init_scroll_height = 20
        self._scroll_bar_height = 10
        self._scroll_bar_active = False
        self._labels = []
        self._labels_scroll_pos = {}
        self._move_num_labels = []

    def paintEvent(self, event):
        max_val = self._horizontal_scroll_bar.maximum()
        if self._labels and max_val:
            self._labels_scroll_pos[len(self._labels) - 1] = (
                max_val + self._labels[-1].width()
            )

    def _clear_labels(self):
        print('clearing widget')
        nb_move_num_labels = len(self._move_num_labels)
        for i in range(nb_move_num_labels):
            move_label = self._move_num_labels.pop()
            move_label.deleteLater()

        nb_labels = len(self._labels)
        for i in range(nb_labels):
            label = self._labels.pop()
            label.deleteLater()

        self.repaint()

    def display_moves(self, moves):
        label_order = 0
        move_num_label_order = 0
        for move in moves:
            move_num, m1, m2 = move
            move_num_label_order += 1
            if len(self._move_num_labels) < move_num_label_order:
                move_label = self._create_label(f'   {str(move_num)}.')
                self._move_num_labels.append(move_label)
                self._labels_layout.insertWidget(
                    self._labels_layout.count() - 1,
                    move_label,
                )

            label_order += 1
            if len(self._labels) < label_order:
                m1_label = self._create_label(m1)
                self._labels.append(m1_label)
                self._labels_layout.insertWidget(
                    self._labels_layout.count() - 1,
                    m1_label,
                )
                self.set_active_label(len(self._labels) - 1)

            if m2:
                label_order += 1
                if len(self._labels) < label_order:
                    m2_label = self._create_label(m2)
                    self._labels.append(m2_label)
                    self._labels_layout.insertWidget(
                        self._labels_layout.count() - 1,
                        m2_label,
                    )
                    self.set_active_label(len(self._labels) - 1)

    def _setup_ui(self):
        self._main_layout = QtWidgets.QVBoxLayout(self)
        self._main_layout.setContentsMargins(0, 0, 0, 0)

        self._labels_widget = QtWidgets.QWidget()
        self._labels_widget.setStyleSheet(
            'QWidget { border: none }'
        )
        self._labels_layout = QtWidgets.QHBoxLayout(self._labels_widget)
        self._labels_layout.setContentsMargins(0, 0, 0, 0)
        self._labels_layout.addStretch(1)
        self._scroll_area = QtWidgets.QScrollArea()
        new_height = self._init_scroll_height + self._scroll_bar_height + 20
        self._scroll_area.setMinimumHeight(
            self._resize_factor * new_height
        )

        self._scroll_area.setVerticalScrollBarPolicy(
            QtCore.Qt.ScrollBarAlwaysOff
        )
        self._scroll_area.setHorizontalScrollBarPolicy(
            QtCore.Qt.ScrollBarAsNeeded
        )

        self._scroll_area.setWidget(self._labels_widget)
        self._scroll_area.setWidgetResizable(True)
        self._scroll_area.setStyleSheet(
            'QScrollArea { border: none }'
        )

        self._horizontal_scroll_bar = self._create_horizontal_scroll_bar(
            self._scroll_area
        )

        self._main_layout.addWidget(self._scroll_area)

    def _connect_signals(self):
        self._horizontal_scroll_bar.rangeChanged.connect(
            self._horizontal_range_changed
        )

    def _horizontal_range_changed(self):
        self._scroll_bar_active = True
        self._horizontal_scroll_bar.setValue(
            self._horizontal_scroll_bar.maximum()
        )

    def _create_horizontal_scroll_bar(self, scroll_area):
        hbar = scroll_area.horizontalScrollBar()
        hbar.setMinimumHeight(self._resize_factor * self._scroll_bar_height)
        hbar.setStyleSheet(
            """
            QScrollBar::add-line:horizontal {
                border: none;
                background: none;
                width: 0px;
                height: 0px;
            }
            QScrollBar::sub-line:horizontal {
                border: none;
                background: none;
                width: 0px;
                height: 0px;
            }
            QScrollBar::right-arrow:horizontal
            {
                border: none;
                background: none;
                color: none;
                width: 0px;
                height: 0px;
            }
            QScrollBar::left-arrow:horizontal
            {
                border: none;
                background: none;
                color: none;
                width: 0px;
                height: 0px;
            }
            """
        )
        # hbar.rangeChanged.connect(lambda: hbar.setValue(hbar.maximum()))

        return hbar

    def _create_label(self, text):
        label = QtWidgets.QLabel(text)
        label.setFixedHeight(self._init_scroll_height)
        # label.setSizePolicy(
        #     QtWidgets.QSizePolicy.Preferred,
        #     QtWidgets.QSizePolicy.Preferred,
        # )
        return label

    def set_active_label(self, index, set_scroll=False):
        if index < 0:
            self._horizontal_scroll_bar.setValue(0)
            first_label = self._labels[0]
            self._set_label_style(label=first_label, active=False)
            return

        for i, label in enumerate(self._labels):
            active = True if i == index else False
            self._set_label_style(label=label, active=active)

        self._scroll_to_label(index, set_scroll=set_scroll)

    def _scroll_to_label(self, index, set_scroll):
        if not set_scroll:
            return

        if not self._scroll_bar_active:
            return

        if self._is_label_fully_visible(self._labels[index]):
            return

        if index in self._labels_scroll_pos:
            self._horizontal_scroll_bar.setValue(
                self._labels_scroll_pos[index]
            )
        else:
            self._horizontal_scroll_bar.setValue(0)

    def _set_label_style(self, label, active):
        if active:
            label.setStyleSheet(
                """
                QLabel {
                    color: black;
                    background: yellow;
                    border: 1px solid red;
                }
                """
            )
        else:
            label.setStyleSheet(
                """
                QLabel {
                    color: white;
                    background: #191919;
                    border: none;
                }
                """
            )

    def _is_label_fully_visible(self, label):
        visible_region = label.visibleRegion()
        if not visible_region.isEmpty():
            visible_region_width = visible_region.rects()[0].width()
            return visible_region_width >= label.width()

        return False
