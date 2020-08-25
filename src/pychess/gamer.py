class Piece:
    type = None

    def __init__(self, name, color, short_name, worth):
        pass

    @property
    def name(self):
        return self._name

    @property
    def short_name(self):
        return self._shot_name

    @property
    def color(self):
        return self._color

    @property
    def worth(self):
        return self._worth


class Game:
    def __init__(self):
        pass

    def initialize(self):
        pass

    def is_game_over(self):
        pass

    def is_move_legal(self, piece, src, dst):
        pass

    def move(self):
        pass
