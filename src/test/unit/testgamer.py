import unittest


from pychess.gamer import Game
from pychess.squarer import Square
from pychess.piecer import Piece
from pychess.constant import PieceType, Color
from pychess.mover import Move


class TestGamer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # A simple gameplay (even a noob would not play so bad ;)
        cls.game = Game()

        # Illegal Move - White rook trying to move diagonally
        cls.game.move(Square('a1'), Square('h8'))

        # Move 1 - White opening with d4
        cls.game.move(Square('d2'), Square('d4'))

        # Move 2 - Black opening with c6
        cls.game.move(Square('c7'), Square('c6'))

        # Illegal Move - Trying to capture white pawn at d4 by white queen
        cls.game.move(Square('d1'), Square('d4'))

        # Move 3 - White Queen to d3
        cls.game.move(Square('d1'), Square('d3'))

        # Illegal Move - Queen trying to jump over white pawn at d4
        # nothing will happen
        cls.game.move(Square('d3'), Square('d5'))

        # Move 4 - Black moves pawn a6
        cls.game.move(Square('a7'), Square('a6'))

        # Move 5- Black pawn at h7 captured by the white queen
        cls.game.move(Square('d3'), Square('h7'))

        # Move 6 - Black pawn to a5
        cls.game.move(Square('a6'), Square('a5'))

        # Move 7 - White queen to f5
        cls.game.move(Square('h7'), Square('f5'))

        # Move 8 - Black rook to h6, where it comes under attack
        # by the black bishop at c1
        cls.game.move(Square('h8'), Square('h6'))

        # Move 9 - White pawn to e4
        cls.game.move(Square('e2'), Square('e4'))

        # Move 10 - Black pawn to a4
        cls.game.move(Square('a5'), Square('a4'))

        # Move 11 - White rook to c4
        cls.game.move(Square('f1'), Square('c4'))

        # Move 12 - White rook to h5 attacking the queen
        cls.game.move(Square('h6'), Square('h5'))

        # Move 13 - White queen to f7, it's a mate!
        cls.game.move(Square('f5'), Square('f7'))

    def test_board(self):
        expected_result = (
            '    a b c d e f g h\n'
            ' 8 |r|n|b|q|k|b|n|#| 8\n'
            ' 7 |#|p|#|p|p|Q|p|_| 7\n'
            ' 6 |_|#|p|#|_|#|_|#| 6\n'
            ' 5 |#|_|#|_|#|_|#|r| 5\n'
            ' 4 |p|#|B|P|P|#|_|#| 4\n'
            ' 3 |#|_|#|_|#|_|#|_| 3\n'
            ' 2 |P|P|P|#|_|P|P|P| 2\n'
            ' 1 |R|N|B|_|K|_|N|R| 1\n'
            '    a b c d e f g h'
        )
        self.assertEqual(repr(self.game.board), expected_result)

    def test_captured_black(self):
        expected_result = [
            Piece(PieceType.pawn, Color.black, order=7),
            Piece(PieceType.pawn, Color.black, order=5),
        ]

        self.assertEqual(self.game.captured_black, expected_result)

    def test_captured_white(self):
        expected_result = []
        self.assertEqual(self.game.captured_white, expected_result)

    def test_white_points(self):
        expected_result = 2
        self.assertEqual(self.game.white_points, expected_result)

    def test_black_points(self):
        expected_result = 0
        self.assertEqual(self.game.black_points, expected_result)

    def test_leader(self):
        expected_result = Color.white
        self.assertEqual(self.game.leader, expected_result)

    def test_lead(self):
        expected_result = 2
        self.assertEqual(self.game.lead, expected_result)

    def test_pieces_checking_black(self):
        expected_result = [Piece(PieceType.queen, Color.white)]
        self.assertEqual(self.game.pieces_checking_black, expected_result)

    def test_pieces_checking_white(self):
        expected_result = []
        self.assertEqual(self.game.pieces_checking_white, expected_result)

    def test_move_history(self):
        # Some short hands for fitting one move in one line
        p = PieceType.pawn
        b = PieceType.bishop
        r = PieceType.rook
        q = PieceType.queen

        wt = Color.white
        bl = Color.black
        s = Square

        expected_result = [
            Move(Piece(p, wt, 3), s('d2'), s('d4')),
            Move(Piece(p, bl, 2), s('c7'), s('c6')),
            Move(Piece(q, wt, 0), s('d1'), s('d3')),
            Move(Piece(p, bl, 0), s('a7'), s('a6')),
            Move(Piece(q, wt, 0), s('d3'), s('h7')),
            Move(Piece(p, bl, 0), s('a6'), s('a5')),
            Move(Piece(q, wt, 0), s('h7'), s('f5')),
            Move(Piece(r, bl, 1), s('h8'), s('h6')),
            Move(Piece(p, wt, 4), s('e2'), s('e4')),
            Move(Piece(p, bl, 0), s('a5'), s('a4')),
            Move(Piece(b, wt, 1), s('f1'), s('c4')),
            Move(Piece(r, bl, 1), s('h6'), s('h5')),
            Move(Piece(q, wt, 0), s('f5'), s('f7')),
        ]

        self.assertEqual(self.game.move_history, expected_result)

    def test_capturables(self):
        expected_result = {
            Color.white: {
                Piece(PieceType.king, Color.black): [
                    Piece(PieceType.queen, Color.white)
                ],
                Piece(PieceType.rook, Color.black, 1): [
                    Piece(PieceType.pawn, Color.white, 7)
                ]
            },
            Color.black: {
                Piece(PieceType.queen, Color.white): [
                    Piece(PieceType.pawn, Color.black, 4),
                    Piece(PieceType.king, Color.black),
                    Piece(PieceType.bishop, Color.black, 1),
                    Piece(PieceType.pawn, Color.black, 6),
                    Piece(PieceType.knight, Color.black, 1),
                    Piece(PieceType.rook, Color.black, 1),

                ]
            }
        }
        self.assertEqual(self.game.capturables, expected_result)


if __name__ == '__main__':
    unittest.main()
