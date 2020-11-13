from pychess.core import gamer
from pychess.gui import imager


game = gamer.Game()
image = imager.BoardImage(game.board)
image.show()
for move_spec in ['e2e4', 'e7e5', 'g1f3']:
    game.move(move_spec)

image.update()
image.show()
