import unittest
import itertools
import copy


from pychess.element.boarder import Board
from pychess.element.piecer import Piece
from pychess.element.squarer import Square
from pychess import constant as c


class TestBoarder(unittest.TestCase):
    def setUp(self):
        self.data = {

            # Rooks
            Square('a1'): Piece(c.PieceType.rook, c.Color.white, order=0),
            Square('h1'): Piece(c.PieceType.rook, c.Color.white, order=1),
            Square('a8'): Piece(c.PieceType.rook, c.Color.black, order=0),
            Square('h8'): Piece(c.PieceType.rook, c.Color.black, order=1),

            # Kinghts
            Square('b1'): Piece(c.PieceType.knight, c.Color.white, order=0),
            Square('g1'): Piece(c.PieceType.knight, c.Color.white, order=1),
            Square('b8'): Piece(c.PieceType.knight, c.Color.black, order=0),
            Square('g8'): Piece(c.PieceType.knight, c.Color.black, order=1),

            # Bishops
            Square('c1'): Piece(c.PieceType.bishop, c.Color.white, order=0),
            Square('f1'): Piece(c.PieceType.bishop, c.Color.white, order=1),
            Square('c8'): Piece(c.PieceType.bishop, c.Color.black, order=0),
            Square('f8'): Piece(c.PieceType.bishop, c.Color.black, order=1),

            # Queens
            Square('d1'): Piece(c.PieceType.queen, c.Color.white),
            Square('d8'): Piece(c.PieceType.queen, c.Color.black),

            # Kings
            Square('e1'): Piece(c.PieceType.king, c.Color.white),
            Square('e8'): Piece(c.PieceType.king, c.Color.black),

            # White Pawns
            Square('a2'): Piece(c.PieceType.pawn, c.Color.white, order=0),
            Square('b2'): Piece(c.PieceType.pawn, c.Color.white, order=1),
            Square('c2'): Piece(c.PieceType.pawn, c.Color.white, order=2),
            Square('d2'): Piece(c.PieceType.pawn, c.Color.white, order=3),
            Square('e2'): Piece(c.PieceType.pawn, c.Color.white, order=4),
            Square('f2'): Piece(c.PieceType.pawn, c.Color.white, order=5),
            Square('g2'): Piece(c.PieceType.pawn, c.Color.white, order=6),
            Square('h2'): Piece(c.PieceType.pawn, c.Color.white, order=7),

            # Black Pawns
            Square('a7'): Piece(c.PieceType.pawn, c.Color.black, order=0),
            Square('b7'): Piece(c.PieceType.pawn, c.Color.black, order=1),
            Square('c7'): Piece(c.PieceType.pawn, c.Color.black, order=2),
            Square('d7'): Piece(c.PieceType.pawn, c.Color.black, order=3),
            Square('e7'): Piece(c.PieceType.pawn, c.Color.black, order=4),
            Square('f7'): Piece(c.PieceType.pawn, c.Color.black, order=5),
            Square('g7'): Piece(c.PieceType.pawn, c.Color.black, order=6),
            Square('h7'): Piece(c.PieceType.pawn, c.Color.black, order=7),
        }
        self.reverse = {v: k for k, v in self.data.items()}

    def test_data(self):
        b = Board()
        for square, piece in self.data.items():
            board_piece = b.data[square]
            self.assertEqual(board_piece, piece)

    def test_set_data(self):
        b = Board()
        data_copy = copy.deepcopy(b.data)
        b.move(Square('e2'), Square('e4'))
        self.assertNotEqual(b.data, data_copy)

        b.data = data_copy
        self.assertEqual(b.data, data_copy)

    def test_pieces(self):
        b = Board()
        board_pieces = sorted(list(b.pieces))
        expected_results = sorted(self.data.values())
        self.assertEqual(board_pieces, expected_results)

    def test_squares(self):
        b = Board()
        board_squares = sorted(b.squares)
        expected_results = sorted(
            [
                Square((x, y))
                for x, y in itertools.product(range(8), range(8))
            ]
        )
        self.assertEqual(board_squares, expected_results)

    def test_get_piece(self):
        b = Board()
        for square, piece in self.data.items():
            expected_result = b.get_piece(square)
            self.assertEqual(piece, expected_result)

    def test_add_piece_validation(self):
        b = Board()

        for square, piece in self.data.items():
            with self.assertRaises(Exception) as context:
                b.add_piece(piece, square)

            exc_str = (
                f'The piece {piece} already '
                f'exists on the board at {square} '
                'cannot add it again!'
            )
            self.assertTrue(exc_str in str(context.exception))

    def test_add_piece(self):
        b = Board()
        b.clear()

        for square, piece in self.data.items():
            b.add_piece(piece, square)

            # Validate added piece
            expected_result = b.get_piece(square)
            self.assertEqual(piece, expected_result)

            # Validate square for added piece
            expected_result = b.get_square(piece)
            self.assertEqual(square, expected_result)

    def test_get_square(self):
        b = Board()

        for square, piece in self.data.items():
            expected_result = b.get_square(piece)
            self.assertEqual(square, expected_result)

    def test_clear_square(self):
        b = Board()

        for square, piece in self.data.items():
            # Knock off a piece from the board
            board_piece = b.clear_square(square)
            self.assertEqual(board_piece, piece)

            # Check that the square is now cleared
            square_contents = b.get_piece(square)
            self.assertIsNone(square_contents)

    def test_is_empty(self):
        b = Board()
        b.clear()
        for square, _ in self.data.items():
            self.assertTrue(b.is_empty(square))

    def test_clear(self):
        b = Board()
        expected_result = dict(
            [
                (Square((x, y)), None)
                for x in range(8)
                for y in range(8)
            ]
        )
        b.clear()
        self.assertEqual(b.data, expected_result)

    def test_reset(self):
        b = Board()

        # First move some pieces around
        b.move(Square('e2'), Square('e4'))
        b.move(Square('e7'), Square('e5'))

        expected_piece = Piece(
            c.PieceType.pawn,
            c.Color.white,
            order=4,
        )
        self.assertEqual(
            b.get_piece(Square('e4')),
            expected_piece,
        )

        expected_piece = Piece(
            c.PieceType.pawn,
            c.Color.black,
            order=4,
        )
        self.assertEqual(
            b.get_piece(Square('e5')),
            expected_piece,
        )

        # Now let's reset the board
        b.reset()

        for square, piece in b.data.items():
            if b.is_empty(square):
                continue
            expected_piece = self.data[square]

            self.assertEqual(piece, expected_piece)

    def test_validate_piece(self):
        b = Board()
        b.clear()

        for square, piece in self.data.items():
            with self.assertRaises(Exception) as context:
                b._validate_piece(piece)

            exc_str = f'The piece {piece} is not found on board'
            self.assertTrue(exc_str in str(context.exception))

    def test_repr(self):
        b = Board()
        expected_result = (
            '    a b c d e f g h\n'
            ' 8 |r|n|b|q|k|b|n|r| 8\n'
            ' 7 |p|p|p|p|p|p|p|p| 7\n'
            ' 6 |_|#|_|#|_|#|_|#| 6\n'
            ' 5 |#|_|#|_|#|_|#|_| 5\n'
            ' 4 |_|#|_|#|_|#|_|#| 4\n'
            ' 3 |#|_|#|_|#|_|#|_| 3\n'
            ' 2 |P|P|P|P|P|P|P|P| 2\n'
            ' 1 |R|N|B|Q|K|B|N|R| 1\n'
            '    a b c d e f g h'
        )
        self.assertEqual(repr(b), expected_result)

    def test_reverse(self):
        b = Board()
        self.assertEqual(b.reverse, self.reverse)

    def test_set_reverse(self):
        b = Board()
        reverse_copy = copy.deepcopy(b.reverse)
        b.move(Square('e2'), Square('e4'))
        self.assertNotEqual(b.reverse, reverse_copy)

        b.reverse = reverse_copy
        self.assertEqual(b.reverse, reverse_copy)

    def test_move_hint_1(self):
        b = Board()
        expected_hints = {
            Square('e2'): [(Square('e3'), None), (Square('e4'), None)],
            Square('a7'): [(Square('a6'), None), (Square('a5'), None)],
            Square('e1'): [],
            Square('g1'): [(Square('h3'), None), (Square('f3'), None)],
        }

        for s, hints in expected_hints.items():
            self.assertEqual(b.move_hint(s), hints)

    def test_move_hint_2(self):
        b = Board()

        b.move(Square('e2'), Square('e4'))
        b.move(Square('d7'), Square('d5'))

        expected_hints = {
            Square('d1'): [
                (Square('e2'), None),
                (Square('f3'), None),
                (Square('g4'), None),
                (Square('h5'), None),
            ],
            Square('e4'): [
                (
                    Square('d5'),
                    Piece(c.PieceType.pawn, c.Color.black, 3),
                ),
                (Square('e5'), None),
            ],
            Square('c8'): [
                (Square('d7'), None),
                (Square('e6'), None),
                (Square('f5'), None),
                (Square('g4'), None),
                (Square('h3'), None),
            ],
        }

        for s, hints in expected_hints.items():
            self.assertEqual(b.move_hint(s), hints)


if __name__ == "__main__":
    unittest.main()
