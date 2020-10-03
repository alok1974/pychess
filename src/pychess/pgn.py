from . import constant as c


class Parser:
    def __init__(self, board):
        self._board = board

    def parse_move_history(self, move_history):
        moves = [
            self._parse_move(m)
            for m in move_history
        ]

        return self._pair_moves(moves)

    def _parse_move(self, move):
        piece_str = (
            ''
            if move.piece.type == c.PieceType.pawn
            else move.piece.code.upper()
        )
        address_str = move.dst.address

        return f'{piece_str}{address_str}'

    # def _pair_moves(self, moves):
    #     pairs = list(zip(moves[::2], moves[1::2]))
    #     if len(moves) % 2 != 0:
    #         pairs.append((moves[-1], ''))

    #     return [
    #         f'{index + 1}. {x[0]} {x[1]}'
    #         for index, x in enumerate(pairs)
    #     ]

    def _pair_moves(self, moves):
        pairs = list(zip(moves[::2], moves[1::2]))
        if len(moves) % 2 != 0:
            pairs.append((moves[-1], ''))

        return [
            (index + 1, x[0], x[1])
            for index, x in enumerate(pairs)
        ]
