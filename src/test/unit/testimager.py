import unittest
import tempfile
import shutil


from PySide2 import QtGui
from PIL import Image as PIL_Image


from pychess import imager, boarder, constant as c


class TestImager(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.mkdtemp()

        self.board = boarder.Board()
        self.board_image = imager.BoardImage(board=self.board)

    def tearDown(self):
        shutil.rmtree(self.tempdir)

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

    def test_widht(self):
        width = 150
        self.board_image.resize(size=width)
        self.board_image.update()
        self.assertEqual(self.board_image.width, width)

    def test_default_height(self):
        self.assertEqual(self.board_image.height, c.IMAGE.DEFAULT_SIZE)

    def test_height(self):
        height = 150
        self.board_image.resize(size=height)
        self.board_image.update()
        self.assertEqual(self.board_image.height, height)

    def test_resize(self):
        new_size = 300
        self.board_image.resize(size=new_size)
        self.assertEqual(self.board_image.image.size, (new_size, new_size))


if __name__ == "__main__":
    unittest.main()
