import unittest


from pychess.piecer import generate_pieces, Piece, get_piece_row_place
from pychess.constant import PieceType, Color, Direction as D


class TestPiecer(unittest.TestCase):
    def test_sort_pieces(self):
        import itertools

        pieces = sorted([
            Piece(pd[0], pd[1])
            for pd in itertools.product(PieceType, Color)
        ])

        expected_result = [
            '<Piece(black pawn 0)>', '<Piece(white pawn 0)>',
            '<Piece(black knight 0)>', '<Piece(white knight 0)>',
            '<Piece(black bishop 0)>', '<Piece(white bishop 0)>',
            '<Piece(black rook 0)>', '<Piece(white rook 0)>',
            '<Piece(black queen 0)>', '<Piece(white queen 0)>',
            '<Piece(black king 0)>', '<Piece(white king 0)>',
        ]

        self.assertEqual([repr(p) for p in pieces], expected_result)

    def test_generate_pieces(self):
        pieces = generate_pieces()

        w_pieces = [p for p in pieces if p.color == Color.white]
        b_pieces = [p for p in pieces if p.color == Color.black]
        self.assertTrue(len(w_pieces) == len(b_pieces) == 16)

        w_pawns = [p for p in w_pieces if p.type == PieceType.pawn]
        b_pawns = [p for p in b_pieces if p.type == PieceType.pawn]
        self.assertTrue(len(w_pawns) == len(b_pawns) == 8)

        w_knights = [p for p in w_pieces if p.type == PieceType.knight]
        b_knights = [p for p in b_pieces if p.type == PieceType.knight]
        self.assertTrue(len(w_knights) == len(b_knights) == 2)

        w_bishops = [p for p in w_pieces if p.type == PieceType.bishop]
        b_bishops = [p for p in b_pieces if p.type == PieceType.bishop]
        self.assertTrue(len(w_bishops) == len(b_bishops) == 2)

        w_bishops = [p for p in w_pieces if p.type == PieceType.bishop]
        b_bishops = [p for p in b_pieces if p.type == PieceType.bishop]
        self.assertTrue(len(w_bishops) == len(b_bishops) == 2)

        w_rooks = [p for p in w_pieces if p.type == PieceType.rook]
        b_rooks = [p for p in b_pieces if p.type == PieceType.rook]
        self.assertTrue(len(w_rooks) == len(b_rooks) == 2)

        w_queens = [p for p in w_pieces if p.type == PieceType.queen]
        b_queens = [p for p in b_pieces if p.type == PieceType.queen]
        self.assertTrue(len(w_queens) == len(b_queens) == 1)

        w_kings = [p for p in w_pieces if p.type == PieceType.king]
        b_kings = [p for p in b_pieces if p.type == PieceType.king]
        self.assertTrue(len(w_kings) == len(b_kings) == 1)

    def test_name(self):
        expected_result = ['pawn', 'knight', 'bishop', 'rook', 'queen', 'king']

        pieces = [Piece(p, Color.black) for p in PieceType]
        names = [p.name for p in pieces]

        self.assertEqual(names, expected_result)

    def test_code(self):
        expected_result = ['p', 'n', 'b', 'r', 'q', 'k']

        pieces = [Piece(p, Color.black) for p in PieceType]
        codes = [p.code for p in pieces]

        self.assertEqual(codes, expected_result)

    def test_color(self):
        p = Piece(PieceType.pawn, color=Color.black)
        self.assertEqual(p.color, Color.black)

        p = Piece(PieceType.pawn, color=Color.white)
        self.assertEqual(p.color, Color.white)

    def test_color_code(self):
        p = Piece(PieceType.pawn, color=Color.black)
        self.assertEqual(p.color_code, 'b')

        p = Piece(PieceType.pawn, color=Color.white)
        self.assertEqual(p.color_code, 'w')

    def test_worth(self):
        expected_result = [1, 3, 3, 5, 9, 10]

        pieces = [Piece(p, Color.black) for p in PieceType]
        worths = [p.worth for p in pieces]

        self.assertEqual(worths, expected_result)

    def test_type(self):
        pieces = [Piece(p, Color.black) for p in PieceType]
        types = [p.type for p in pieces]

        self.assertEqual(types, [t for t in PieceType])

    def test_allowed_move_directions(self):
        moves = {
            PieceType.pawn: [D.n, D.nw, D.ne],
            PieceType.knight: [
                D.nnw, D.nne, D.wnw, D.ene, D.wsw, D.ese, D.ssw, D.sse],
            PieceType.bishop: [D.nw, D.ne, D.sw, D.se],
            PieceType.rook: [D.n, D.s, D.e, D.w],
            PieceType.queen: [
                D.nw, D.ne, D.sw, D.se, D.n, D.e, D.w, D.s],
            PieceType.king: [
                D.nw, D.ne, D.sw, D.se, D.n, D.e, D.w, D.s
            ],
        }

        pieces = [Piece(p, Color.black) for p in moves.keys()]

        for p in pieces:
            expected_result = moves.get(p.type)
            self.assertEqual(p.allowed_move_direction, expected_result)

    def test_nb_pieces(self):
        expected_result = [8, 2, 2, 2, 1, 1]

        pieces = [Piece(p, Color.black) for p in PieceType]
        nb_pieces = [p.nb_pieces for p in pieces]

        self.assertEqual(nb_pieces, expected_result)

    def test_order(self):
        nb_pieces = {
            PieceType.pawn: 8,
            PieceType.knight: 2,
            PieceType.bishop: 2,
            PieceType.rook: 2,
            PieceType.queen: 1,
            PieceType.king: 1,
        }

        for piece_type in nb_pieces.keys():
            pieces = []
            orders = []
            for i in range(nb_pieces[piece_type]):
                pieces.append(Piece(piece_type, Color.black, order=i))
                orders = [p.order for p in pieces]
            expected_result = list(range(nb_pieces[piece_type]))
            self.assertEqual(orders, expected_result)

    def test_uid(self):
        expected_result = [
            '0bb', '0bw', '0kb', '0kw', '0nb', '0nw', '0pb', '0pw', '0qb',
            '0qw', '0rb', '0rw', '1bb', '1bw', '1nb', '1nw', '1pb', '1pw',
            '1rb', '1rw', '2pb', '2pw', '3pb', '3pw', '4pb', '4pw', '5pb',
            '5pw', '6pb', '6pw', '7pb', '7pw'
        ]
        pieces = generate_pieces()
        uids = sorted([p.uid for p in pieces])
        self.assertEqual(uids, expected_result)

    def test_travel_distance(self):
        import math

        travel_distance = {
            PieceType.pawn: [1, math.sqrt(2)],
            PieceType.knight: [math.sqrt(5)],
            PieceType.bishop: [0],
            PieceType.rook: [0],
            PieceType.queen: [0],
            PieceType.king: [1, math.sqrt(2)],
        }

        pieces = [Piece(p, Color.black) for p in travel_distance.keys()]

        for p in pieces:
            expected_result = travel_distance.get(p.type)
            self.assertEqual(p.travel_distance, expected_result)

    def test_hash(self):
        import itertools

        piece_data = [d for d in itertools.product(PieceType, Color)]

        expected_results = [
            (d[0].value * 100) + (d[1].value * 10) + (0)  # default order
            for d in piece_data
        ]

        pieces = [Piece(piece_type=d[0], color=d[1]) for d in piece_data]

        for piece, expected_result in zip(pieces, expected_results):
            try:
                self.assertEqual(hash(piece), expected_result)
            except AssertionError:
                print(f'{piece} != {expected_result}')
                raise

    def test_equals(self):
        p1 = Piece(PieceType.pawn, Color.black)
        p2 = Piece(PieceType.pawn, Color.black)

        self.assertTrue(p1 is not p2)
        self.assertEqual(p1, p2)

    def test_not_equals(self):
        p1 = Piece(PieceType.rook, Color.black)
        p2 = Piece(PieceType.rook, Color.black, order=1)
        self.assertNotEqual(p1, p2)

    def test_greater(self):
        p1 = Piece(PieceType.king, Color.black)
        p2 = Piece(PieceType.queen, Color.white)

        self.assertGreater(p1, p2)

        p1 = Piece(PieceType.king, Color.white)
        p2 = Piece(PieceType.king, Color.black)

        self.assertGreater(p1, p2)

    def test_less(self):
        p1 = Piece(PieceType.queen, Color.black)
        p2 = Piece(PieceType.king, Color.white)

        self.assertLess(p1, p2)

        p1 = Piece(PieceType.queen, Color.black)
        p2 = Piece(PieceType.queen, Color.white)

        self.assertLess(p1, p2)

    def test_greater_equals(self):
        p1 = Piece(PieceType.king, Color.black)
        p2 = Piece(PieceType.queen, Color.white)
        self.assertGreaterEqual(p1, p2)

        p1 = Piece(PieceType.king, Color.white)
        p2 = Piece(PieceType.king, Color.white)
        self.assertGreaterEqual(p1, p2)

    def test_less_equals(self):
        p1 = Piece(PieceType.queen, Color.black)
        p2 = Piece(PieceType.king, Color.white)
        self.assertLessEqual(p1, p2)

        p1 = Piece(PieceType.king, Color.white)
        p2 = Piece(PieceType.king, Color.white)
        self.assertLessEqual(p1, p2)

    def test_get_pieces_row_place(self):
        places = {
            (PieceType.rook, 0): 0,
            (PieceType.knight, 0): 1,
            (PieceType.bishop, 0): 2,
            (PieceType.queen, 0): 3,
            (PieceType.king, 0): 4,
            (PieceType.bishop, 1): 5,
            (PieceType.knight, 1): 6,
            (PieceType.rook, 1): 7,
        }

        for piece in generate_pieces():
            if piece.type == PieceType.pawn:
                expected_result = piece.order
            else:
                expected_result = places[(piece.type, piece.order)]
            row_place = get_piece_row_place(piece)
            self.assertEqual(row_place, expected_result)


if __name__ == "__main__":
    unittest.main()
