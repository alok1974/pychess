import unittest
import collections


from pychess.mover import Move
from pychess.squarer import Square
from pychess.piecer import generate_pieces
from pychess.constant import PieceType, Color, Direction


# Move Data
MD = collections.namedtuple(
    'MD',
    ['move', 'is_legal', 'is_orthogonal', 'is_diagonal', 'path']
)


def moves_for_testing(piece):
    """
        a b c d e f g h
     8 | |#| |#| |#| |#| 8
     7 |#| |#| |#| |#| | 7
     6 | |#| |#| |#| |#| 6
     5 |#| |#| |#| |#| | 5
     4 | |#| |#| |#| |#| 4
     3 |#| |#| |#| |#| | 3
     2 | |#| |#| |#| |#| 2
     1 |#| |#| |#| |#| | 1
        a b c d e f g h
    """
    moves = {
        (PieceType.pawn, Color.black): [

                MD(
                    move=('f7', 'f5'),
                    is_legal=True,
                    is_orthogonal=True,
                    is_diagonal=False,
                    path=[Square('f7'), Square('f5')],
                ),

                MD(
                    move=('b6', 'c5'),
                    is_legal=True,
                    is_orthogonal=False,
                    is_diagonal=True,
                    path=[Square('b6'), Square('c5')],
                ),

                MD(
                    move=('g3', 'g4'),
                    is_legal=False,
                    is_orthogonal=True,
                    is_diagonal=False,
                    path=[],
                ),

                MD(
                    move=('e4', 'e2'),
                    is_legal=False,
                    is_orthogonal=True,
                    is_diagonal=False,
                    path=[],
                ),

            ],
        (PieceType.pawn, Color.black): [

                MD(
                    move=('f7', 'f5'),
                    is_legal=True,
                    is_orthogonal=True,
                    is_diagonal=False,
                    path=[Square('f7'), Square('f5')],
                ),

                MD(
                    move=('b6', 'c5'),
                    is_legal=True,
                    is_orthogonal=False,
                    is_diagonal=True,
                    path=[Square('b6'), Square('c5')],
                ),

                MD(
                    move=('g3', 'g4'),
                    is_legal=False,
                    is_orthogonal=True,
                    is_diagonal=False,
                    path=[],
                ),

                MD(
                    move=('e4', 'e2'),
                    is_legal=False,
                    is_orthogonal=True,
                    is_diagonal=False,
                    path=[],
                ),

            ],
        (PieceType.pawn, Color.black): [

                MD(
                    move=('f7', 'f5'),
                    is_legal=True,
                    is_orthogonal=True,
                    is_diagonal=False,
                    path=[Square('f7'), Square('f5')],
                ),

                MD(
                    move=('b6', 'c5'),
                    is_legal=True,
                    is_orthogonal=False,
                    is_diagonal=True,
                    path=[Square('b6'), Square('c5')],
                ),

                MD(
                    move=('g3', 'g4'),
                    is_legal=False,
                    is_orthogonal=True,
                    is_diagonal=False,
                    path=[],
                ),

                MD(
                    move=('e4', 'e2'),
                    is_legal=False,
                    is_orthogonal=True,
                    is_diagonal=False,
                    path=[],
                ),

            ],
        (PieceType.pawn, Color.black): [

                MD(
                    move=('f7', 'f5'),
                    is_legal=True,
                    is_orthogonal=True,
                    is_diagonal=False,
                    path=[Square('f7'), Square('f5')],
                ),

                MD(
                    move=('b6', 'c5'),
                    is_legal=True,
                    is_orthogonal=False,
                    is_diagonal=True,
                    path=[Square('b6'), Square('c5')],
                ),

                MD(
                    move=('g3', 'g4'),
                    is_legal=False,
                    is_orthogonal=True,
                    is_diagonal=False,
                    path=[],
                ),

                MD(
                    move=('e4', 'e2'),
                    is_legal=False,
                    is_orthogonal=True,
                    is_diagonal=False,
                    path=[],
                ),

            ],
        (PieceType.pawn, Color.black): [

                MD(
                    move=('f7', 'f5'),
                    is_legal=True,
                    is_orthogonal=True,
                    is_diagonal=False,
                    path=[Square('f7'), Square('f5')],
                ),

                MD(
                    move=('b6', 'c5'),
                    is_legal=True,
                    is_orthogonal=False,
                    is_diagonal=True,
                    path=[Square('b6'), Square('c5')],
                ),

                MD(
                    move=('g3', 'g4'),
                    is_legal=False,
                    is_orthogonal=True,
                    is_diagonal=False,
                    path=[],
                ),

                MD(
                    move=('e4', 'e2'),
                    is_legal=False,
                    is_orthogonal=True,
                    is_diagonal=False,
                    path=[],
                ),

            ],
        (PieceType.pawn, Color.black): [

                MD(
                    move=('f7', 'f5'),
                    is_legal=True,
                    is_orthogonal=True,
                    is_diagonal=False,
                    path=[Square('f7'), Square('f5')],
                ),

                MD(
                    move=('b6', 'c5'),
                    is_legal=True,
                    is_orthogonal=False,
                    is_diagonal=True,
                    path=[Square('b6'), Square('c5')],
                ),

                MD(
                    move=('g3', 'g4'),
                    is_legal=False,
                    is_orthogonal=True,
                    is_diagonal=False,
                    path=[],
                ),

                MD(
                    move=('e4', 'e2'),
                    is_legal=False,
                    is_orthogonal=True,
                    is_diagonal=False,
                    path=[],
                ),

            ],
        (PieceType.pawn, Color.black): [

                MD(
                    move=('f7', 'f5'),
                    is_legal=True,
                    is_orthogonal=True,
                    is_diagonal=False,
                    path=[Square('f7'), Square('f5')],
                ),

                MD(
                    move=('b6', 'c5'),
                    is_legal=True,
                    is_orthogonal=False,
                    is_diagonal=True,
                    path=[Square('b6'), Square('c5')],
                ),

                MD(
                    move=('g3', 'g4'),
                    is_legal=False,
                    is_orthogonal=True,
                    is_diagonal=False,
                    path=[],
                ),

                MD(
                    move=('e4', 'e2'),
                    is_legal=False,
                    is_orthogonal=True,
                    is_diagonal=False,
                    path=[],
                ),

            ],
        (PieceType.pawn, Color.black): [

                MD(
                    move=('f7', 'f5'),
                    is_legal=True,
                    is_orthogonal=True,
                    is_diagonal=False,
                    path=[Square('f7'), Square('f5')],
                ),

                MD(
                    move=('b6', 'c5'),
                    is_legal=True,
                    is_orthogonal=False,
                    is_diagonal=True,
                    path=[Square('b6'), Square('c5')],
                ),

                MD(
                    move=('g3', 'g4'),
                    is_legal=False,
                    is_orthogonal=True,
                    is_diagonal=False,
                    path=[],
                ),

                MD(
                    move=('e4', 'e2'),
                    is_legal=False,
                    is_orthogonal=True,
                    is_diagonal=False,
                    path=[],
                ),

            ],
        (PieceType.knight, Color.black): [

                MD(
                    move=('b8', 'a6'),
                    is_legal=True,
                    is_orthogonal=False,
                    is_diagonal=False,
                    path=[Square('b8'), Square('a6')],
                ),

                MD(
                    move=('f6', 'g4'),
                    is_legal=True,
                    is_orthogonal=False,
                    is_diagonal=False,
                    path=[Square('f6'), Square('g4')],
                ),

                MD(
                    move=('d5', 'd3'),
                    is_legal=False,
                    is_orthogonal=True,
                    is_diagonal=False,
                    path=[],
                ),

                MD(
                    move=('a3', 'd6'),
                    is_legal=False,
                    is_orthogonal=False,
                    is_diagonal=True,
                    path=[],
                ),

            ],
        (PieceType.knight, Color.black): [
                MD(
                    move=('b8', 'a6'),
                    is_legal=True,
                    is_orthogonal=False,
                    is_diagonal=False,
                    path=[Square('b8'), Square('a6')],
                ),
                MD(
                    move=('f6', 'g4'),
                    is_legal=True,
                    is_orthogonal=False,
                    is_diagonal=False,
                    path=[Square('f6'), Square('g4')],
                ),

                MD(
                    move=('d5', 'd3'),
                    is_legal=False,
                    is_orthogonal=True,
                    is_diagonal=False,
                    path=[],
                ),

                MD(
                    move=('a3', 'd6'),
                    is_legal=False,
                    is_orthogonal=False,
                    is_diagonal=True,
                    path=[],
                ),

            ],
        (PieceType.bishop, Color.black): [

                MD(
                    move=('g1', 'a7'),
                    is_legal=True,
                    is_orthogonal=False,
                    is_diagonal=True,
                    path=[
                        Square('g1'), Square('f2'), Square('e3'), Square('d4'),
                        Square('c5'), Square('b6'), Square('a7')
                    ],
                ),

                MD(
                    move=('f6', 'g5'),
                    is_legal=True,
                    is_orthogonal=False,
                    is_diagonal=True,
                    path=[Square('f6'), Square('g5')],
                ),

                MD(
                    move=('e5', 'e3'),
                    is_legal=False,
                    is_orthogonal=True,
                    is_diagonal=False,
                    path=[],
                ),

                MD(
                    move=('b6', 'c3'),
                    is_legal=False,
                    is_orthogonal=False,
                    is_diagonal=False,
                    path=[],
                ),

            ],
        (PieceType.bishop, Color.black): [

                MD(
                    move=('g1', 'a7'),
                    is_legal=True,
                    is_orthogonal=False,
                    is_diagonal=True,
                    path=[
                        Square('g1'), Square('f2'), Square('e3'),
                        Square('d4'), Square('c5'), Square('b6'), Square('a7')
                    ],
                ),

                MD(
                    move=('f6', 'g5'),
                    is_legal=True,
                    is_orthogonal=False,
                    is_diagonal=True,
                    path=[Square('f6'), Square('g5')],
                ),

                MD(
                    move=('e5', 'e3'),
                    is_legal=False,
                    is_orthogonal=True,
                    is_diagonal=False,
                    path=[],
                ),

                MD(
                    move=('b6', 'c3'),
                    is_legal=False,
                    is_orthogonal=False,
                    is_diagonal=False,
                    path=[],
                ),

            ],
        (PieceType.rook, Color.black): [

                MD(
                    move=('e7', 'e3'),
                    is_legal=True,
                    is_orthogonal=True,
                    is_diagonal=False,
                    path=[
                        Square('e7'), Square('e6'), Square('e5'),
                        Square('e4'), Square('e3')
                    ],
                ),

                MD(
                    move=('a3', 'g3'),
                    is_legal=True,
                    is_orthogonal=True,
                    is_diagonal=False,
                    path=[
                        Square('a3'), Square('b3'), Square('c3'),
                        Square('d3'), Square('e3'), Square('f3'), Square('g3')
                    ],
                ),

                MD(
                    move=('h4', 'f7'),
                    is_legal=False,
                    is_orthogonal=False,
                    is_diagonal=False,
                    path=[],
                ),

                MD(
                    move=('c6', 'b5'),
                    is_legal=False,
                    is_orthogonal=False,
                    is_diagonal=True,
                    path=[],
                ),

            ],
        (PieceType.rook, Color.black): [

                MD(
                    move=('e7', 'e3'),
                    is_legal=True,
                    is_orthogonal=True,
                    is_diagonal=False,
                    path=[
                        Square('e7'), Square('e6'), Square('e5'),
                        Square('e4'), Square('e3')
                    ],
                ),

                MD(
                    move=('a3', 'g3'),
                    is_legal=True,
                    is_orthogonal=True,
                    is_diagonal=False,
                    path=[
                        Square('a3'), Square('b3'), Square('c3'),
                        Square('d3'), Square('e3'), Square('f3'), Square('g3')
                    ],
                ),

                MD(
                    move=('h4', 'f7'),
                    is_legal=False,
                    is_orthogonal=False,
                    is_diagonal=False,
                    path=[],
                ),

                MD(
                    move=('c6', 'b5'),
                    is_legal=False,
                    is_orthogonal=False,
                    is_diagonal=True,
                    path=[],
                ),

            ],
        (PieceType.queen, Color.black): [

                MD(
                    move=('h5', 'e8'),
                    is_legal=True,
                    is_orthogonal=False,
                    is_diagonal=True,
                    path=[
                        Square('h5'), Square('g6'), Square('f7'),
                        Square('e8')
                    ],
                ),

                MD(
                    move=('b5', 'd3'),
                    is_legal=True,
                    is_orthogonal=False,
                    is_diagonal=True,
                    path=[Square('b5'), Square('c4'), Square('d3')],
                ),

                MD(
                    move=('c7', 'f7'),
                    is_legal=True,
                    is_orthogonal=True,
                    is_diagonal=False,
                    path=[
                        Square('c7'), Square('d7'), Square('e7'),
                        Square('f7')
                    ],
                ),

                MD(
                    move=('g1', 'g5'),
                    is_legal=True,
                    is_orthogonal=True,
                    is_diagonal=False,
                    path=[
                        Square('g1'), Square('g2'), Square('g3'),
                        Square('g4'), Square('g5')
                    ],
                ),

                MD(
                    move=('a4', 'c5'),
                    is_legal=False,
                    is_orthogonal=False,
                    is_diagonal=False,
                    path=[],
                ),

                MD(
                    move=('b7', 'd4'),
                    is_legal=False,
                    is_orthogonal=False,
                    is_diagonal=False,
                    path=[],
                ),

            ],
        (PieceType.king, Color.black): [

                MD(
                    move=('e8', 'g8'),
                    is_legal=True,
                    is_orthogonal=True,
                    is_diagonal=False,
                    path=[Square('e8'), Square('g8')],
                ),

                MD(
                    move=('e8', 'c8'),
                    is_legal=True,
                    is_orthogonal=True,
                    is_diagonal=False,
                    path=[Square('e8'), Square('c8')],
                ),

                MD(
                    move=('f6', 'g5'),
                    is_legal=True,
                    is_orthogonal=False,
                    is_diagonal=True,
                    path=[Square('f6'), Square('g5')],
                ),

                MD(
                    move=('b4', 'b3'),
                    is_legal=True,
                    is_orthogonal=True,
                    is_diagonal=False,
                    path=[Square('b4'), Square('b3')],
                ),

                MD(
                    move=('e7', 'd7'),
                    is_legal=True,
                    is_orthogonal=True,
                    is_diagonal=False,
                    path=[Square('e7'), Square('d7')],
                ),

                MD(
                    move=('g6', 'e5'),
                    is_legal=False,
                    is_orthogonal=False,
                    is_diagonal=False,
                    path=[],
                ),

                MD(
                    move=('a6', 'c5'),
                    is_legal=False,
                    is_orthogonal=False,
                    is_diagonal=False,
                    path=[],
                ),

            ],
        (PieceType.pawn, Color.white): [

                MD(
                    move=('d2', 'd4'),
                    is_legal=True,
                    is_orthogonal=True,
                    is_diagonal=False,
                    path=[Square('d2'), Square('d4')],
                ),

                MD(
                    move=('f4', 'f5'),
                    is_legal=True,
                    is_orthogonal=True,
                    is_diagonal=False,
                    path=[Square('f4'), Square('f5')],
                ),

                MD(
                    move=('f7', 'f6'),
                    is_legal=False,
                    is_orthogonal=True,
                    is_diagonal=False,
                    path=[],
                ),

                MD(
                    move=('f4', 'f6'),
                    is_legal=False,
                    is_orthogonal=True,
                    is_diagonal=False,
                    path=[],
                ),

            ],
        (PieceType.pawn, Color.white): [

                MD(
                    move=('d2', 'd4'),
                    is_legal=True,
                    is_orthogonal=True,
                    is_diagonal=False,
                    path=[Square('d2'), Square('d4')],
                ),

                MD(
                    move=('f4', 'f5'),
                    is_legal=True,
                    is_orthogonal=True,
                    is_diagonal=False,
                    path=[Square('f4'), Square('f5')],
                ),

                MD(
                    move=('f7', 'f6'),
                    is_legal=False,
                    is_orthogonal=True,
                    is_diagonal=False,
                    path=[],
                ),

                MD(
                    move=('f4', 'f6'),
                    is_legal=False,
                    is_orthogonal=True,
                    is_diagonal=False,
                    path=[],
                ),

            ],
        (PieceType.pawn, Color.white): [

                MD(
                    move=('d2', 'd4'),
                    is_legal=True,
                    is_orthogonal=True,
                    is_diagonal=False,
                    path=[Square('d2'), Square('d4')],
                ),

                MD(
                    move=('f4', 'f5'),
                    is_legal=True,
                    is_orthogonal=True,
                    is_diagonal=False,
                    path=[Square('f4'), Square('f5')],
                ),

                MD(
                    move=('f7', 'f6'),
                    is_legal=False,
                    is_orthogonal=True,
                    is_diagonal=False,
                    path=[],
                ),

                MD(
                    move=('f4', 'f6'),
                    is_legal=False,
                    is_orthogonal=True,
                    is_diagonal=False,
                    path=[],
                ),

            ],
        (PieceType.pawn, Color.white): [

                MD(
                    move=('d2', 'd4'),
                    is_legal=True,
                    is_orthogonal=True,
                    is_diagonal=False,
                    path=[Square('d2'), Square('d4')],
                ),

                MD(
                    move=('f4', 'f5'),
                    is_legal=True,
                    is_orthogonal=True,
                    is_diagonal=False,
                    path=[Square('f4'), Square('f5')],
                ),

                MD(
                    move=('f7', 'f6'),
                    is_legal=False,
                    is_orthogonal=True,
                    is_diagonal=False,
                    path=[],
                ),

                MD(
                    move=('f4', 'f6'),
                    is_legal=False,
                    is_orthogonal=True,
                    is_diagonal=False,
                    path=[],
                ),

            ],
        (PieceType.pawn, Color.white): [

                MD(
                    move=('d2', 'd4'),
                    is_legal=True,
                    is_orthogonal=True,
                    is_diagonal=False,
                    path=[Square('d2'), Square('d4')],
                ),

                MD(
                    move=('f4', 'f5'),
                    is_legal=True,
                    is_orthogonal=True,
                    is_diagonal=False,
                    path=[Square('f4'), Square('f5')],
                ),

                MD(
                    move=('f7', 'f6'),
                    is_legal=False,
                    is_orthogonal=True,
                    is_diagonal=False,
                    path=[],
                ),

                MD(
                    move=('f4', 'f6'),
                    is_legal=False,
                    is_orthogonal=True,
                    is_diagonal=False,
                    path=[],
                ),

            ],
        (PieceType.pawn, Color.white): [

                MD(
                    move=('d2', 'd4'),
                    is_legal=True,
                    is_orthogonal=True,
                    is_diagonal=False,
                    path=[Square('d2'), Square('d4')],
                ),

                MD(
                    move=('f4', 'f5'),
                    is_legal=True,
                    is_orthogonal=True,
                    is_diagonal=False,
                    path=[Square('f4'), Square('f5')],
                ),

                MD(
                    move=('f7', 'f6'),
                    is_legal=False,
                    is_orthogonal=True,
                    is_diagonal=False,
                    path=[],
                ),

                MD(
                    move=('f4', 'f6'),
                    is_legal=False,
                    is_orthogonal=True,
                    is_diagonal=False,
                    path=[],
                ),

            ],
        (PieceType.pawn, Color.white): [

                MD(
                    move=('d2', 'd4'),
                    is_legal=True,
                    is_orthogonal=True,
                    is_diagonal=False,
                    path=[Square('d2'), Square('d4')],
                ),

                MD(
                    move=('f4', 'f5'),
                    is_legal=True,
                    is_orthogonal=True,
                    is_diagonal=False,
                    path=[Square('f4'), Square('f5')],
                ),

                MD(
                    move=('f7', 'f6'),
                    is_legal=False,
                    is_orthogonal=True,
                    is_diagonal=False,
                    path=[],
                ),

                MD(
                    move=('f4', 'f6'),
                    is_legal=False,
                    is_orthogonal=True,
                    is_diagonal=False,
                    path=[],
                ),

            ],
        (PieceType.pawn, Color.white): [

                MD(
                    move=('d2', 'd4'),
                    is_legal=True,
                    is_orthogonal=True,
                    is_diagonal=False,
                    path=[Square('d2'), Square('d4')],
                ),

                MD(
                    move=('f4', 'f5'),
                    is_legal=True,
                    is_orthogonal=True,
                    is_diagonal=False,
                    path=[Square('f4'), Square('f5')],
                ),

                MD(
                    move=('f7', 'f6'),
                    is_legal=False,
                    is_orthogonal=True,
                    is_diagonal=False,
                    path=[],
                ),

                MD(
                    move=('f4', 'f6'),
                    is_legal=False,
                    is_orthogonal=True,
                    is_diagonal=False,
                    path=[],
                ),

            ],
        (PieceType.knight, Color.white): [

                MD(
                    move=('g1', 'f3'),
                    is_legal=True,
                    is_orthogonal=False,
                    is_diagonal=False,
                    path=[Square('g1'), Square('f3')],
                ),

                MD(
                    move=('c3', 'd5'),
                    is_legal=True,
                    is_orthogonal=False,
                    is_diagonal=False,
                    path=[Square('c3'), Square('d5')],
                ),

                MD(
                    move=('f6', 'g5'),
                    is_legal=False,
                    is_orthogonal=False,
                    is_diagonal=True,
                    path=[],
                ),

                MD(
                    move=('d4', 'b6'),
                    is_legal=False,
                    is_orthogonal=False,
                    is_diagonal=True,
                    path=[],
                ),

            ],
        (PieceType.knight, Color.white): [

                MD(
                    move=('g1', 'f3'),
                    is_legal=True,
                    is_orthogonal=False,
                    is_diagonal=False,
                    path=[Square('g1'), Square('f3')],
                ),

                MD(
                    move=('c3', 'd5'),
                    is_legal=True,
                    is_orthogonal=False,
                    is_diagonal=False,
                    path=[Square('c3'), Square('d5')],
                ),

                MD(
                    move=('f6', 'g5'),
                    is_legal=False,
                    is_orthogonal=False,
                    is_diagonal=True,
                    path=[],
                ),

                MD(
                    move=('d4', 'b6'),
                    is_legal=False,
                    is_orthogonal=False,
                    is_diagonal=True,
                    path=[],
                ),

            ],
        (PieceType.bishop, Color.white): [

                MD(
                    move=('f1', 'a6'),
                    is_legal=True,
                    is_orthogonal=False,
                    is_diagonal=True,
                    path=[
                        Square('f1'), Square('e2'), Square('d3'),
                        Square('c4'), Square('b5'), Square('a6')
                    ],
                ),

                MD(
                    move=('c2', 'd3'),
                    is_legal=True,
                    is_orthogonal=False,
                    is_diagonal=True,
                    path=[Square('c2'), Square('d3')],
                ),

                MD(
                    move=('f6', 'd6'),
                    is_legal=False,
                    is_orthogonal=True,
                    is_diagonal=False,
                    path=[],
                ),

                MD(
                    move=('c4', 'e5'),
                    is_legal=False,
                    is_orthogonal=False,
                    is_diagonal=False,
                    path=[],
                ),

            ],
        (PieceType.bishop, Color.white): [

                MD(
                    move=('f1', 'a6'),
                    is_legal=True,
                    is_orthogonal=False,
                    is_diagonal=True,
                    path=[
                        Square('f1'), Square('e2'), Square('d3'),
                        Square('c4'), Square('b5'), Square('a6')
                    ],
                ),

                MD(
                    move=('c2', 'd3'),
                    is_legal=True,
                    is_orthogonal=False,
                    is_diagonal=True,
                    path=[Square('c2'), Square('d3')],
                ),

                MD(
                    move=('f6', 'd6'),
                    is_legal=False,
                    is_orthogonal=True,
                    is_diagonal=False,
                    path=[],
                ),

                MD(
                    move=('c4', 'e5'),
                    is_legal=False,
                    is_orthogonal=False,
                    is_diagonal=False,
                    path=[],
                ),

            ],
        (PieceType.rook, Color.white): [

                MD(
                    move=('a1', 'a8'),
                    is_legal=True,
                    is_orthogonal=True,
                    is_diagonal=False,
                    path=[
                        Square('a1'), Square('a2'), Square('a3'),
                        Square('a4'), Square('a5'), Square('a6'),
                        Square('a7'), Square('a8')
                    ],
                ),

                MD(
                    move=('b4', 'c4'),
                    is_legal=True,
                    is_orthogonal=True,
                    is_diagonal=False,
                    path=[Square('b4'), Square('c4')],
                ),

                MD(
                    move=('f3', 'e4'),
                    is_legal=False,
                    is_orthogonal=False,
                    is_diagonal=True,
                    path=[],
                ),

                MD(
                    move=('c4', 'e5'),
                    is_legal=False,
                    is_orthogonal=False,
                    is_diagonal=False,
                    path=[],
                ),

            ],
        (PieceType.rook, Color.white): [

                MD(
                    move=('a1', 'a8'),
                    is_legal=True,
                    is_orthogonal=True,
                    is_diagonal=False,
                    path=[
                        Square('a1'), Square('a2'), Square('a3'),
                        Square('a4'), Square('a5'), Square('a6'),
                        Square('a7'), Square('a8')
                    ],
                ),

                MD(
                    move=('b4', 'c4'),
                    is_legal=True,
                    is_orthogonal=True,
                    is_diagonal=False,
                    path=[Square('b4'), Square('c4')],
                ),

                MD(
                    move=('f3', 'e4'),
                    is_legal=False,
                    is_orthogonal=False,
                    is_diagonal=True,
                    path=[],
                ),

                MD(
                    move=('c4', 'e5'),
                    is_legal=False,
                    is_orthogonal=False,
                    is_diagonal=False,
                    path=[],
                ),

            ],
        (PieceType.queen, Color.white): [

                MD(
                    move=('b4', 'e1'),
                    is_legal=True,
                    is_orthogonal=False,
                    is_diagonal=True,
                    path=[
                        Square('b4'), Square('c3'), Square('d2'),
                        Square('e1')
                    ],
                ),

                MD(
                    move=('b2', 'g7'),
                    is_legal=True,
                    is_orthogonal=False,
                    is_diagonal=True,
                    path=[
                        Square('b2'), Square('c3'), Square('d4'),
                        Square('e5'), Square('f6'), Square('g7')
                    ],
                ),

                MD(
                    move=('d4', 'd8'),
                    is_legal=True,
                    is_orthogonal=True,
                    is_diagonal=False,
                    path=[
                        Square('d4'), Square('d5'), Square('d6'),
                        Square('d7'), Square('d8')
                    ],
                ),

                MD(
                    move=('e3', 'b3'),
                    is_legal=True,
                    is_orthogonal=True,
                    is_diagonal=False,
                    path=[
                        Square('e3'), Square('d3'), Square('c3'),
                        Square('b3')
                    ],
                ),

                MD(
                    move=('f2', 'd3'),
                    is_legal=False,
                    is_orthogonal=False,
                    is_diagonal=False,
                    path=[],
                ),

                MD(
                    move=('b6', 'f7'),
                    is_legal=False,
                    is_orthogonal=False,
                    is_diagonal=False,
                    path=[],
                ),

            ],
        (PieceType.king, Color.white): [

                MD(
                    move=('e1', 'g1'),
                    is_legal=True,
                    is_orthogonal=True,
                    is_diagonal=False,
                    path=[Square('e1'), Square('g1')],
                ),

                MD(
                    move=('e1', 'c1'),
                    is_legal=True,
                    is_orthogonal=True,
                    is_diagonal=False,
                    path=[Square('e1'), Square('c1')],
                ),

                MD(
                    move=('g3', 'f4'),
                    is_legal=True,
                    is_orthogonal=False,
                    is_diagonal=True,
                    path=[Square('g3'), Square('f4')],
                ),

                MD(
                    move=('c2', 'c1'),
                    is_legal=True,
                    is_orthogonal=True,
                    is_diagonal=False,
                    path=[Square('c2'), Square('c1')],
                ),

                MD(
                    move=('h2', 'g2'),
                    is_legal=True,
                    is_orthogonal=True,
                    is_diagonal=False,
                    path=[Square('h2'), Square('g2')],
                ),

                MD(
                    move=('f2', 'd3'),
                    is_legal=False,
                    is_orthogonal=False,
                    is_diagonal=False,
                    path=[],
                ),

                MD(
                    move=('b6', 'f7'),
                    is_legal=False,
                    is_orthogonal=False,
                    is_diagonal=False,
                    path=[],
                ),

            ],
        }

    return moves.get((piece.type, piece.color), [])


def generate_piece(piece_type, color, order=0):
    all_pieces = generate_pieces()
    required_pieces = [
        p
        for p in all_pieces
        if p.type == piece_type and
        p.color == color and
        p.order == order
    ]
    assert len(required_pieces) == 1
    return required_pieces[0]


class TestMover(unittest.TestCase):
    def test_is_legal(self):
        for piece in generate_pieces():
            for move_data in moves_for_testing(piece):
                src_address, dst_address = move_data.move
                src = Square(src_address)
                dst = Square(dst_address)
                m = Move(
                    piece=piece,
                    src=src,
                    dst=dst,
                )

                assert_to_use = (
                    self.assertTrue
                    if move_data.is_legal
                    else self.assertFalse
                )
                try:
                    assert_to_use(m.is_legal)
                except AssertionError:
                    error_msg = (
                        f'{piece}: '
                        f'{src.address} -> {dst.address} '
                        f'is_legal: {move_data.is_legal}'
                    )
                    print(error_msg)
                    raise

    def test_piece(self):
        for piece in generate_pieces():
            for move_data in moves_for_testing(piece):
                src_address, dst_address = move_data.move
                src = Square(src_address)
                dst = Square(dst_address)
                m = Move(
                    piece=piece,
                    src=src,
                    dst=dst,
                )
                self.assertEqual(m.piece, piece)

    def test_src(self):
        for piece in generate_pieces():
            for move_data in moves_for_testing(piece):
                src_address, dst_address = move_data.move
                src = Square(src_address)
                dst = Square(dst_address)
                m = Move(
                    piece=piece,
                    src=src,
                    dst=dst,
                )
                self.assertEqual(m.src, src)

    def test_dst(self):
        for piece in generate_pieces():
            for move_data in moves_for_testing(piece):
                src_address, dst_address = move_data.move
                src = Square(src_address)
                dst = Square(dst_address)
                m = Move(
                    piece=piece,
                    src=src,
                    dst=dst,
                )
                self.assertEqual(m.dst, dst)

    def test_distance(self):
        black_queen = generate_piece(
            piece_type=PieceType.queen,
            color=Color.black,
        )

        src = Square((4, 1))
        dst = Square((1, 5))
        m = Move(
            piece=black_queen,
            src=src,
            dst=dst,
        )

        self.assertEqual(m.distance, 5.0)

    def test_angle(self):
        white_bishop = generate_piece(
            piece_type=PieceType.bishop,
            color=Color.white,
        )

        src = Square((0, 0))
        dst = Square('h8')
        m = Move(
            piece=white_bishop,
            src=src,
            dst=dst,
        )

        self.assertEqual(m.angle, 45.0)

    def test_direction(self):
        white_knight = generate_piece(
            piece_type=PieceType.knight,
            color=Color.white,
        )

        src = Square((3, 5))
        dst = Square((4, 7))
        m = Move(
            piece=white_knight,
            src=src,
            dst=dst,
        )

        self.assertEqual(m.direction, Direction.nne)

    def test_repr(self):
        for piece in generate_pieces():
            for move_data in moves_for_testing(piece):
                src_address, dst_address = move_data.move
                src = Square(src_address)
                dst = Square(dst_address)
                m = Move(
                    piece=piece,
                    src=src,
                    dst=dst,
                )
                expected_result = (
                    '<'
                    f'{m.__class__.__name__}'
                    ': '
                    f'{piece.code}'
                    f'({piece.color_code}) '
                    f'{src.address}'
                    f' - '
                    f'{dst.address}'
                    '>'
                )
                self.assertEqual(repr(m), expected_result)

    def test_path(self):
        for piece in generate_pieces():
            for move_data in moves_for_testing(piece):
                src_address, dst_address = move_data.move
                src = Square(src_address)
                dst = Square(dst_address)
                m = Move(
                    piece=piece,
                    src=src,
                    dst=dst,
                )
                self.assertEqual(m.path, move_data.path)

    def test_is_diagonal(self):
        for piece in generate_pieces():
            for move_data in moves_for_testing(piece):
                src_address, dst_address = move_data.move
                src = Square(src_address)
                dst = Square(dst_address)
                m = Move(
                    piece=piece,
                    src=src,
                    dst=dst,
                )
                self.assertEqual(m.is_diagonal, move_data.is_diagonal)

    def test_is_orthogonal(self):
        for piece in generate_pieces():
            for move_data in moves_for_testing(piece):
                src_address, dst_address = move_data.move
                src = Square(src_address)
                dst = Square(dst_address)
                m = Move(
                    piece=piece,
                    src=src,
                    dst=dst,
                )
                self.assertEqual(m.is_orthogonal, move_data.is_orthogonal)

if __name__ == '__main__':
    unittest.main()
