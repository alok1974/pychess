import unittest


from pychess import piecer, constant as c


class TestPiecer(unittest.TestCase):
    def test_generate_pieces(self):
        pieces = piecer.generate_pieces()

        w_pieces = [p for p in pieces if p.color == c.Color.white]
        b_pieces = [p for p in pieces if p.color == c.Color.black]
        self.assertTrue(len(w_pieces) == len(b_pieces) == 16)

        w_pawns = [p for p in w_pieces if p.type == c.PieceType.pawn]
        b_pawns = [p for p in b_pieces if p.type == c.PieceType.pawn]
        self.assertTrue(len(w_pawns) == len(b_pawns) == 8)

        w_knights = [p for p in w_pieces if p.type == c.PieceType.knight]
        b_knights = [p for p in b_pieces if p.type == c.PieceType.knight]
        self.assertTrue(len(w_knights) == len(b_knights) == 2)

        w_bishops = [p for p in w_pieces if p.type == c.PieceType.bishop]
        b_bishops = [p for p in b_pieces if p.type == c.PieceType.bishop]
        self.assertTrue(len(w_bishops) == len(b_bishops) == 2)

        w_bishops = [p for p in w_pieces if p.type == c.PieceType.bishop]
        b_bishops = [p for p in b_pieces if p.type == c.PieceType.bishop]
        self.assertTrue(len(w_bishops) == len(b_bishops) == 2)

        w_rooks = [p for p in w_pieces if p.type == c.PieceType.rook]
        b_rooks = [p for p in b_pieces if p.type == c.PieceType.rook]
        self.assertTrue(len(w_rooks) == len(b_rooks) == 2)

        w_queens = [p for p in w_pieces if p.type == c.PieceType.queen]
        b_queens = [p for p in b_pieces if p.type == c.PieceType.queen]
        self.assertTrue(len(w_queens) == len(b_queens) == 1)

        w_kings = [p for p in w_pieces if p.type == c.PieceType.king]
        b_kings = [p for p in b_pieces if p.type == c.PieceType.king]
        self.assertTrue(len(w_kings) == len(b_kings) == 1)

    def test_uid(self):
        expected_result = [
            '0bb', '0bw', '0kb', '0kw', '0nb', '0nw', '0pb', '0pw', '0qb',
            '0qw', '0rb', '0rw', '1bb', '1bw', '1nb', '1nw', '1pb', '1pw',
            '1rb', '1rw', '2pb', '2pw', '3pb', '3pw', '4pb', '4pw', '5pb',
            '5pw', '6pb', '6pw', '7pb', '7pw'
        ]
        pieces = piecer.generate_pieces()
        uids = sorted([p.uid for p in pieces])
        self.assertEqual(uids, expected_result)


if __name__ == "__main__":
    unittest.main()
