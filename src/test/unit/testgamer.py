import unittest


from pychess.gamer import Game
from pychess.squarer import Square


class TestGamer(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_move(self):
        game = Game()

        # Illegal move of white rook, will do nothing
        game.move(Square('a1'), Square('h8'))

        game.move(Square('d2'), Square('d4'))
        game.move(Square('d7'), Square('d5'))

        # Illegal move trying to capture white pawn at d4 by white queen
        # this move will not happen
        game.move(Square('d1'), Square('d4'))

        game.move(Square('d1'), Square('d3'))

        # queen trying to jump over white pawn at d4
        # nothing will happen
        game.move(Square('d3'), Square('d5'))

        # legal capture of black pawn at h7 by the queen
        game.move(Square('d3'), Square('h7'))
        print(game.board)
        print(game.captured_black)
        print(game.captured_white)
        print(game.leader)
        print(game.lead)


if __name__ == '__main__':
    unittest.main()
