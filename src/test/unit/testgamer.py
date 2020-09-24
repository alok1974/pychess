import unittest
import copy


from pychess.gamer import Game
from pychess.squarer import Square
from pychess.piecer import Piece
from pychess import constant as c
from pychess.mover import Move


def _check_win(game):
    if game.is_game_over:
        winner = str(game.winner.name).capitalize()
        print(f'{winner} wins!')


class TestGamer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Some short hands for fitting one move in one line
        p = c.PieceType.pawn
        b = c.PieceType.bishop
        r = c.PieceType.rook
        q = c.PieceType.queen

        wt = c.Color.white
        bl = c.Color.black
        s = Square

        cls.expected_move_history = []
        # A simple gameplay (even a noob would not play so bad ;)
        cls.game = Game()

        # Illegal Move - White rook trying to move diagonally
        cls.game.move(('a1h8'))
        _check_win(cls.game)

        # Move 1 - White opening with d4
        cls.game.move(('d2d4'))
        _check_win(cls.game)
        cls.expected_move_history.append(
            (
                Move(Piece(p, wt, 3), s('d2'), s('d4')),
                copy.deepcopy(cls.game.board.data),
                copy.deepcopy(cls.game.board.reverse),
            )

        )

        # Move 2 - Black opening with c6
        cls.game.move(('c7c6'))
        _check_win(cls.game)
        cls.expected_move_history.append(
            (
                Move(Piece(p, bl, 2), s('c7'), s('c6')),
                copy.deepcopy(cls.game.board.data),
                copy.deepcopy(cls.game.board.reverse),
            )

        )

        # Illegal Move - Trying to capture white pawn at d4 by white queen
        cls.game.move(('d1d4'))
        _check_win(cls.game)

        # Move 3 - White Queen to d3
        cls.game.move(('d1d3'))
        _check_win(cls.game)
        cls.expected_move_history.append(
            (
                Move(Piece(q, wt, 0), s('d1'), s('d3')),
                copy.deepcopy(cls.game.board.data),
                copy.deepcopy(cls.game.board.reverse),
            )

        )

        # Illegal Move - Queen trying to jump over white pawn at d4
        # nothing will happen
        cls.game.move(('d3d5'))
        _check_win(cls.game)

        # Move 4 - Black moves pawn a6
        cls.game.move(('a7a6'))
        _check_win(cls.game)
        cls.expected_move_history.append(
            (
                Move(Piece(p, bl, 0), s('a7'), s('a6')),
                copy.deepcopy(cls.game.board.data),
                copy.deepcopy(cls.game.board.reverse),
            )

        )

        # Move 5 - Black pawn at h7 captured by the white queen
        cls.game.move(('d3h7'))
        _check_win(cls.game)
        cls.expected_move_history.append(
            (
                Move(Piece(q, wt, 0), s('d3'), s('h7')),
                copy.deepcopy(cls.game.board.data),
                copy.deepcopy(cls.game.board.reverse),
            )

        )

        # Move 6 - Black pawn to a5
        cls.game.move(('a6a5'))
        _check_win(cls.game)
        cls.expected_move_history.append(
            (
                Move(Piece(p, bl, 0), s('a6'), s('a5')),
                copy.deepcopy(cls.game.board.data),
                copy.deepcopy(cls.game.board.reverse),
            )

        )

        # Move 7 - White queen to f5
        cls.game.move(('h7f5'))
        _check_win(cls.game)
        cls.expected_move_history.append(
            (
                Move(Piece(q, wt, 0), s('h7'), s('f5')),
                copy.deepcopy(cls.game.board.data),
                copy.deepcopy(cls.game.board.reverse),
            )

        )

        # Move 8 - Black rook to h6, where it comes under attack
        # by the black bishop at c1
        cls.game.move(('h8h6'))
        _check_win(cls.game)
        cls.expected_move_history.append(
            (
                Move(Piece(r, bl, 1), s('h8'), s('h6')),
                copy.deepcopy(cls.game.board.data),
                copy.deepcopy(cls.game.board.reverse),
            )

        )

        # Move 9 - White pawn to e4
        cls.game.move(('e2e4'))
        _check_win(cls.game)
        cls.expected_move_history.append(
            (
                Move(Piece(p, wt, 4), s('e2'), s('e4')),
                copy.deepcopy(cls.game.board.data),
                copy.deepcopy(cls.game.board.reverse),
            )

        )

        # Move 10 - Black pawn to a4
        cls.game.move(('a5a4'))
        _check_win(cls.game)
        cls.expected_move_history.append(
            (
                Move(Piece(p, bl, 0), s('a5'), s('a4')),
                copy.deepcopy(cls.game.board.data),
                copy.deepcopy(cls.game.board.reverse),
            )

        )

        # Move 11 - White rook to c4
        cls.game.move(('f1c4'))
        _check_win(cls.game)
        cls.expected_move_history.append(
            (
                Move(Piece(b, wt, 1), s('f1'), s('c4')),
                copy.deepcopy(cls.game.board.data),
                copy.deepcopy(cls.game.board.reverse),
            )

        )

        # Move 12 - White rook to h5 attacking the queen
        cls.game.move(('h6h5'))
        _check_win(cls.game)
        cls.expected_move_history.append(
            (
                Move(Piece(r, bl, 1), s('h6'), s('h5')),
                copy.deepcopy(cls.game.board.data),
                copy.deepcopy(cls.game.board.reverse),
            )

        )

        # Move 13 - White queen to f7, it's a mate!
        cls.game.move(('f5f7'))
        _check_win(cls.game)
        cls.expected_move_history.append(
            (
                Move(Piece(q, wt, 0), s('f5'), s('f7')),
                copy.deepcopy(cls.game.board.data),
                copy.deepcopy(cls.game.board.reverse),
            )

        )

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
            Piece(c.PieceType.pawn, c.Color.black, order=7),
            Piece(c.PieceType.pawn, c.Color.black, order=5),
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
        expected_result = c.Color.white
        self.assertEqual(self.game.leader, expected_result)

    def test_lead(self):
        expected_result = 2
        self.assertEqual(self.game.lead, expected_result)

    def test_pieces_checking_black(self):
        expected_result = [Piece(c.PieceType.queen, c.Color.white)]
        self.assertEqual(self.game.pieces_checking_black, expected_result)

    def test_pieces_checking_white(self):
        expected_result = []
        self.assertEqual(self.game.pieces_checking_white, expected_result)

    def test_move_history(self):
        self.assertEqual(self.game.move_history, self.expected_move_history)

    def test_capturables(self):
        expected_result = {
            c.Color.white: {
                Piece(c.PieceType.king, c.Color.black): [
                    Piece(c.PieceType.queen, c.Color.white)
                ],
                Piece(c.PieceType.rook, c.Color.black, 1): [
                    Piece(c.PieceType.pawn, c.Color.white, 7)
                ]
            },
            c.Color.black: {
                Piece(c.PieceType.queen, c.Color.white): [
                    Piece(c.PieceType.pawn, c.Color.black, 4),
                    Piece(c.PieceType.king, c.Color.black),
                    Piece(c.PieceType.bishop, c.Color.black, 1),
                    Piece(c.PieceType.pawn, c.Color.black, 6),
                    Piece(c.PieceType.knight, c.Color.black, 1),
                    Piece(c.PieceType.rook, c.Color.black, 1),

                ]
            }
        }
        self.assertEqual(self.game.capturables, expected_result)

    def test_winner(self):
        expected_result = c.Color.white
        self.assertEqual(self.game.winner, expected_result)

    def test_parse_move_spec_1(self):
        move_spec = 'a1h8'
        expected_result = (Square('a1'), Square('h8'))
        self.assertEqual(Game.parse_move_spec(move_spec), expected_result)

    def test_parse_move_spec_2(self):
        move_spec = ('a1', 'h8')
        expected_result = (Square('a1'), Square('h8'))
        self.assertEqual(Game.parse_move_spec(move_spec), expected_result)

    def test_parse_move_spec_3(self):
        move_spec = ((0, 0), (0, 7))
        expected_result = (Square((0, 0)), Square((0, 7)))
        self.assertEqual(Game.parse_move_spec(move_spec), expected_result)

    def test_parse_move_spec_4(self):
        move_spec = [1, 2, 3, 4]
        exc_str = (
            f'`move_spec={move_spec}` should either be a tuple or a string'
        )
        with self.assertRaises(Exception) as context:
            Game.parse_move_spec(move_spec)

        self.assertTrue(exc_str in str(context.exception))

    def test_parse_move_spec_5(self):
        move_spec = (1, 2, 3)
        exc_str = (
            f'{move_spec} tuple should have exactly two elements!'
        )
        with self.assertRaises(Exception) as context:
            Game.parse_move_spec(move_spec)

        self.assertTrue(exc_str in str(context.exception))

    def test_parse_move_spec_6(self):
        addr_1 = 'aa'
        addr_2 = '11'
        move_spec = (addr_1, addr_2)
        exc_str = (
            f'Malformed address! The address {addr_1} supplied '
            f'in arg `move_spec={move_spec}` should be of '
            'the format \'<alpha><number>\' where alpha is '
            'one of [a, b, c, d, e, f, g, h] and number '
            'is from 1 to 8'
        )
        with self.assertRaises(Exception) as context:
            Game.parse_move_spec(move_spec)

        self.assertTrue(exc_str in str(context.exception))

    def test_parse_move_spec_7(self):
        addr_1 = 'a1'
        addr_2 = '11'
        move_spec = (addr_1, addr_2)
        exc_str = (
            f'Malformed address! The address {addr_2} supplied '
            f'in arg `move_spec={move_spec}` should be of '
            'the format \'<alpha><number>\' where alpha is '
            'one of [a, b, c, d, e, f, g, h] and number '
            'is from 1 to 8'
        )
        with self.assertRaises(Exception) as context:
            Game.parse_move_spec(move_spec)

        self.assertTrue(exc_str in str(context.exception))

    def test_parse_move_spec_8(self):
        addr_1 = (10, 30)
        addr_2 = (12, 40)
        move_spec = (addr_1, addr_2)
        exc_str = (
            f'The address {addr_1} supplied in arg '
            f'`move_spec={move_spec}` should exactly be a '
            'tuple of the form (a, b) where both a and b '
            'are one of the numbers 0 to 7'
        )
        with self.assertRaises(Exception) as context:
            Game.parse_move_spec(move_spec)

        self.assertTrue(exc_str in str(context.exception))

    def test_parse_move_spec_9(self):
        addr_1 = (0, 5)
        addr_2 = (12, 40)
        move_spec = (addr_1, addr_2)
        exc_str = (
            f'The address {addr_2} supplied in arg '
            f'`move_spec={move_spec}` should exactly be a '
            'tuple of the form (a, b) where both a and b '
            'are one of the numbers 0 to 7'
        )
        with self.assertRaises(Exception) as context:
            Game.parse_move_spec(move_spec)

        self.assertTrue(exc_str in str(context.exception))

    def test_parse_move_spec_10(self):
        move_spec = ((0, 5), (0, 5))
        exc_str = (
            f'`move_spec={move_spec}` should have distinct source and '
            'destination'
        )
        with self.assertRaises(Exception) as context:
            Game.parse_move_spec(move_spec)

        self.assertTrue(exc_str in str(context.exception))

    def test_parse_move_spec_11(self):
        move_spec = ('a1', 'a1')
        exc_str = (
            f'`move_spec={move_spec}` should have distinct source and '
            'destination'
        )
        with self.assertRaises(Exception) as context:
            Game.parse_move_spec(move_spec)

        self.assertTrue(exc_str in str(context.exception))

    def test_parse_move_spec_12(self):
        move_spec = 'c6c6'
        exc_str = (
            f'`move_spec={move_spec}` should have distinct source and '
            'destination'
        )
        with self.assertRaises(Exception) as context:
            Game.parse_move_spec(move_spec)

        self.assertTrue(exc_str in str(context.exception))

    def test_parse_move_spec_13(self):
        move_spec = (Square('e1'), Square('e4'))
        expected_result = move_spec
        self.assertEqual(Game.parse_move_spec(move_spec), expected_result)


if __name__ == '__main__':
    unittest.main()
