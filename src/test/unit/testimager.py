import unittest


from PySide2 import QtGui
from PIL import Image as PIL_Image


from pychess import constant as c
from pychess.gui import imager
from pychess.element import boarder


class TestImager(unittest.TestCase):
    def setUp(self):
        self.board = boarder.Board()
        self.board_image = imager.BoardImage(board=self.board)

    def tearDown(self):
        pass

    def test_board(self):
        self.assertEqual(self.board_image.board, self.board)

    def test_qt_image(self):
        qt_image = self.board_image.qt_image
        self.assertTrue(isinstance(qt_image, QtGui.QImage))

    def test_image(self):
        image = self.board_image.image
        self.assertTrue(isinstance(image, PIL_Image.Image))

    def test_default_width(self):
        self.assertEqual(self.board_image.width, c.IMAGE.DEFAULT_SIZE)

    def test_default_height(self):
        self.assertEqual(self.board_image.height, c.IMAGE.DEFAULT_SIZE)


if __name__ == "__main__":
    unittest.main()
