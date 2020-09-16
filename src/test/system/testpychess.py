from pychess import gamer, imager


game = gamer.Game()
image = imager.BoardImage(game.board)
image.show()

moves = ['e2e4', 'e7e5', 'g1f3']
size = [300, 450, 600]
for index, move_spec in enumerate(moves):
    game.move(move_spec)
    image.resize(size[index])
    image.update()
    image.show()


game.reset()
image.resize()
image.update()
image.show()
