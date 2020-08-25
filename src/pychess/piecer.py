class Piece:
    def __init__(self, name, color, code, worth, piece_type, move_type):
        self._piece_type = piece_type
        self._name = name
        self._code = code
        self._color = color
        self._worth = worth
        self._move_type = move_type

    @property
    def name(self):
        return self._name

    @property
    def code(self):
        return self._code

    @property
    def color(self):
        return self._color

    @property
    def worth(self):
        return self._worth

    @property
    def piece_type(self):
        return self._piece_type

    @property
    def move_type(self):
        return self._move_type
