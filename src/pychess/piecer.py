import collections
import math


from . import constant as c


class Piece:
    piece_attr = collections.namedtuple(
        'piece_attr',
        [
            'allowed_move_direction',
            'worth',
            'nb_pieces',
            'travel_distance',
        ]
    )

    piece_data = {
        c.PieceType.pawn: piece_attr(
            allowed_move_direction=[
                c.Direction.n,
                c.Direction.nw,
                c.Direction.ne,
            ],
            worth=1,
            nb_pieces=8,
            travel_distance=[1, math.sqrt(2)],
        ),
        c.PieceType.knight: piece_attr(
            allowed_move_direction=[
                c.Direction.nnw,
                c.Direction.nne,
                c.Direction.wnw,
                c.Direction.ene,
                c.Direction.wsw,
                c.Direction.ese,
                c.Direction.ssw,
                c.Direction.sse,
            ],
            worth=3,
            nb_pieces=2,
            travel_distance=[math.sqrt(5)],
        ),
        c.PieceType.bishop: piece_attr(
            allowed_move_direction=[
                c.Direction.nw,
                c.Direction.ne,
                c.Direction.sw,
                c.Direction.se
            ],
            worth=3,
            nb_pieces=2,
            travel_distance=[0],
        ),
        c.PieceType.rook: piece_attr(
            allowed_move_direction=[
                c.Direction.n,
                c.Direction.s,
                c.Direction.e,
                c.Direction.w
            ],
            worth=5,
            nb_pieces=2,
            travel_distance=[0],
        ),
        c.PieceType.queen: piece_attr(
            allowed_move_direction=[
                c.Direction.nw,
                c.Direction.ne,
                c.Direction.sw,
                c.Direction.se,
                c.Direction.n,
                c.Direction.e,
                c.Direction.w,
                c.Direction.s,
            ],
            worth=9,
            nb_pieces=1,
            travel_distance=[0],
        ),
        c.PieceType.king: piece_attr(
            allowed_move_direction=[
                c.Direction.nw,
                c.Direction.ne,
                c.Direction.sw,
                c.Direction.se,
                c.Direction.n,
                c.Direction.e,
                c.Direction.w,
                c.Direction.s,
            ],
            worth=10,
            nb_pieces=1,
            travel_distance=[1, math.sqrt(2)],
        ),
    }

    def __init__(self, piece_type, color, order=0):
        self._type = piece_type
        self._color = color
        self._color_code = self._color.name[:1]
        self._order = order

        self._attr = self.piece_data[self._type]
        self._name = piece_type.name
        self._code = (
            piece_type.name[:1]
            if piece_type != c.PieceType.knight
            else c.GAME.CODE_KNIGHT
        )
        self._worth = self._attr.worth
        self._allowed_move_direction = self._attr.allowed_move_direction
        self._travel_distance = self._attr.travel_distance
        self._nb_pieces = self._attr.nb_pieces
        self._uid = f'{self.order}{self.code}{self.color_code}'

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
    def color_code(self):
        return self._color_code

    @property
    def worth(self):
        return self._worth

    @property
    def type(self):
        return self._type

    @property
    def allowed_move_direction(self):
        return self._allowed_move_direction

    @property
    def nb_pieces(self):
        return self._nb_pieces

    @property
    def order(self):
        return self._order

    @property
    def uid(self):
        return self._uid

    @property
    def travel_distance(self):
        return self._travel_distance

    @property
    def pretty(self):
        return (
            f'{self}\n'
            f'name: {self.name}\n'
            f'code: {self.code}\n'
            f'order: {self.order}\n'
            f'color: {self.color}\n'
            f'color_code: {self.color_code}\n'
            f'worth: {self.worth}\n'
            f'type: {self.type}\n'
            f'allowed_move_direction: {self.allowed_move_direction}\n'
            f'nb_pieces: {self.nb_pieces}\n'
            f'uid: {self.uid}\n'
            f'travel_distance: {self.travel_distance}\n'
        )

    def __repr__(self):
        return (
            f'<{self.__class__.__name__}'
            f'({self.color.name} {self.name} {self.order})>'
        )

    def __hash__(self):
        return (self.type.value * 100) + (self.color.value * 10) + self.order

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __neq__(self, other):
        return hash(self) != hash(other)

    def __gt__(self, other):
        return hash(self) > hash(other)

    def __lt__(self, other):
        return hash(self) < hash(other)

    def __ge__(self, other):
        return self.__eq__ or self.__gt__

    def __le__(self, other):
        return self.__eq__ or self.__lt__


def generate_pieces():
    pieces = []
    for color in c.Color:
        pieces.extend(_generate_pieces(color=color))

    return pieces


def get_piece_row_place(piece):
    places = {
        (c.PieceType.rook, 0): 0,
        (c.PieceType.knight, 0): 1,
        (c.PieceType.bishop, 0): 2,
        (c.PieceType.queen, 0): 3,
        (c.PieceType.king, 0): 4,
        (c.PieceType.bishop, 1): 5,
        (c.PieceType.knight, 1): 6,
        (c.PieceType.rook, 1): 7,
    }

    if piece.type == c.PieceType.pawn:
        return piece.order

    return places[(piece.type, piece.order)]


def _generate_pieces(color):
    pieces = []
    for piece_type in c.PieceType:
        nb_pieces = getattr(c.GAME.NUM_PIECES, piece_type.name)
        for i in range(nb_pieces):
            piece = Piece(piece_type=piece_type, color=color, order=i)
            pieces.append(piece)

    return sorted(pieces)
