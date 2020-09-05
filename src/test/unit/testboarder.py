import unittest
import itertools


from pychess.boarder import Board
from pychess.squarer import Square
from pychess.piecer import Piece
from pychess import constant as C


class TestBoarder(unittest.TestCase):
    def setUp(self):
        self.data = {

            # Rooks
            Square('a1'): Piece(C.PieceType.rook, C.Color.white, order=0),
            Square('h1'): Piece(C.PieceType.rook, C.Color.white, order=1),
            Square('a8'): Piece(C.PieceType.rook, C.Color.black, order=0),
            Square('h8'): Piece(C.PieceType.rook, C.Color.black, order=1),

            # Kinghts
            Square('b1'): Piece(C.PieceType.knight, C.Color.white, order=0),
            Square('g1'): Piece(C.PieceType.knight, C.Color.white, order=1),
            Square('b8'): Piece(C.PieceType.knight, C.Color.black, order=0),
            Square('g8'): Piece(C.PieceType.knight, C.Color.black, order=1),

            # Bishops
            Square('c1'): Piece(C.PieceType.bishop, C.Color.white, order=0),
            Square('f1'): Piece(C.PieceType.bishop, C.Color.white, order=1),
            Square('c8'): Piece(C.PieceType.bishop, C.Color.black, order=0),
            Square('f8'): Piece(C.PieceType.bishop, C.Color.black, order=1),

            # Queens
            Square('d1'): Piece(C.PieceType.queen, C.Color.white),
            Square('d8'): Piece(C.PieceType.queen, C.Color.black),

            # Kings
            Square('e1'): Piece(C.PieceType.king, C.Color.white),
            Square('e8'): Piece(C.PieceType.king, C.Color.black),

            # White Pawns
            Square('a2'): Piece(C.PieceType.pawn, C.Color.white, order=0),
            Square('b2'): Piece(C.PieceType.pawn, C.Color.white, order=1),
            Square('c2'): Piece(C.PieceType.pawn, C.Color.white, order=2),
            Square('d2'): Piece(C.PieceType.pawn, C.Color.white, order=3),
            Square('e2'): Piece(C.PieceType.pawn, C.Color.white, order=4),
            Square('f2'): Piece(C.PieceType.pawn, C.Color.white, order=5),
            Square('g2'): Piece(C.PieceType.pawn, C.Color.white, order=6),
            Square('h2'): Piece(C.PieceType.pawn, C.Color.white, order=7),

            # Black Pawns
            Square('a7'): Piece(C.PieceType.pawn, C.Color.black, order=0),
            Square('b7'): Piece(C.PieceType.pawn, C.Color.black, order=1),
            Square('c7'): Piece(C.PieceType.pawn, C.Color.black, order=2),
            Square('d7'): Piece(C.PieceType.pawn, C.Color.black, order=3),
            Square('e7'): Piece(C.PieceType.pawn, C.Color.black, order=4),
            Square('f7'): Piece(C.PieceType.pawn, C.Color.black, order=5),
            Square('g7'): Piece(C.PieceType.pawn, C.Color.black, order=6),
            Square('h7'): Piece(C.PieceType.pawn, C.Color.black, order=7),
        }

    def test_data(self):
        b = Board()
        for square, piece in self.data.items():
            board_piece = b.data[square]
            self.assertEqual(board_piece, piece)

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


if __name__ == "__main__":
    unittest.main()
