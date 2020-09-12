from pychess import imager, piecer, constant as c

ci = imager.CapturedImage()

captured_white = [
    piecer.Piece(c.PieceType.pawn, c.Color.white, 0),
    piecer.Piece(c.PieceType.pawn, c.Color.white, 1),
    piecer.Piece(c.PieceType.pawn, c.Color.white, 2),
    piecer.Piece(c.PieceType.pawn, c.Color.white, 3),
    piecer.Piece(c.PieceType.pawn, c.Color.white, 4),
    piecer.Piece(c.PieceType.pawn, c.Color.white, 5),
    piecer.Piece(c.PieceType.pawn, c.Color.white, 6),
    piecer.Piece(c.PieceType.pawn, c.Color.white, 7),
    piecer.Piece(c.PieceType.knight, c.Color.white, 0),
    piecer.Piece(c.PieceType.knight, c.Color.white, 1),
    piecer.Piece(c.PieceType.bishop, c.Color.white, 0),
    piecer.Piece(c.PieceType.bishop, c.Color.white, 1),
    piecer.Piece(c.PieceType.rook, c.Color.white, 0),
    piecer.Piece(c.PieceType.rook, c.Color.white, 1),
    piecer.Piece(c.PieceType.queen, c.Color.white, 0),
]

captured_black = [
    piecer.Piece(c.PieceType.pawn, c.Color.black, 0),
    piecer.Piece(c.PieceType.pawn, c.Color.black, 1),
    piecer.Piece(c.PieceType.pawn, c.Color.black, 2),
    piecer.Piece(c.PieceType.pawn, c.Color.black, 3),
    piecer.Piece(c.PieceType.pawn, c.Color.black, 4),
    piecer.Piece(c.PieceType.pawn, c.Color.black, 5),
    piecer.Piece(c.PieceType.pawn, c.Color.black, 6),
    piecer.Piece(c.PieceType.pawn, c.Color.black, 7),
    piecer.Piece(c.PieceType.knight, c.Color.black, 0),
    piecer.Piece(c.PieceType.knight, c.Color.black, 1),
    piecer.Piece(c.PieceType.bishop, c.Color.black, 0),
    piecer.Piece(c.PieceType.bishop, c.Color.black, 1),
    piecer.Piece(c.PieceType.rook, c.Color.black, 0),
    piecer.Piece(c.PieceType.rook, c.Color.black, 1),
    piecer.Piece(c.PieceType.queen, c.Color.black, 0),
]

ci.update(captured_white, captured_black, c.Color.black, 3)
ci.image_white.show()
ci.image_black.show()


ci_2 = imager.CapturedImage()

captured_white_2 = []
captured_black_2 = []
ci_2.update(captured_white_2, captured_black_2, None, 0)
ci_2.image_white.show()

captured_white_2.append(piecer.Piece(c.PieceType.pawn, c.Color.white, 0))
ci_2.update(captured_white_2, captured_black_2, c.Color.black, 1)
ci_2.image_white.show()


captured_white_2.append(piecer.Piece(c.PieceType.bishop, c.Color.white, 0))
ci_2.update(captured_white_2, captured_black_2, c.Color.black, 4)
ci_2.image_white.show()

captured_white_2.append(piecer.Piece(c.PieceType.bishop, c.Color.white, 1))
ci_2.update(captured_white_2, captured_black_2, c.Color.black, 7)
ci_2.image_white.show()


captured_white_2.append(piecer.Piece(c.PieceType.pawn, c.Color.white, 1))
ci_2.update(captured_white_2, captured_black_2, c.Color.black, 8)
ci_2.image_white.show()


captured_white_2.append(piecer.Piece(c.PieceType.knight, c.Color.white, 0))
ci_2.update(captured_white_2, captured_black_2, c.Color.black, 11)
ci_2.image_white.show()


captured_white_2.append(piecer.Piece(c.PieceType.queen, c.Color.white, 0))
ci_2.update(captured_white_2, captured_black_2, c.Color.black, 20)
ci_2.image_white.show()

captured_white_2.append(piecer.Piece(c.PieceType.rook, c.Color.white, 0))
ci_2.update(captured_white_2, captured_black_2, c.Color.black, 25)
ci_2.image_white.show()
