from . import constant as c


def parse_move_history(move_history):
    moves = [
        parse_move(m)
        for m in move_history
    ]

    return _pair_moves(moves)


def parse_move(move):
    if move.castling_done:
        if move.is_king_side_castling:
            return 'O-O'
        else:
            return 'O-O-O'

    check = (
        '+'
        if move.is_check
        else ''
    )

    mate = (
        '#'
        if move.is_mate
        else ''
    )

    capture = 'x' if move.is_capture else ''

    promoted_piece = move.promoted_piece
    if promoted_piece is not None:
        promotion = promoted_piece.code.upper()
        return f'{move.dst.address}={promotion}{capture}{check}{mate}'

    if move.piece.type == c.PieceType.pawn:
        piece_str = ''
        if move.is_capture:
            capture = f'{move.src.x_address}{capture}'
    else:
        piece_str = move.piece.code.upper()

    disambiguate = (
        move.disambiguate
        if move.disambiguate is not None
        else ''
    )

    return f'{piece_str}{disambiguate}{capture}{move.dst.address}{check}{mate}'


def _pair_moves(moves):
    pairs = list(zip(moves[::2], moves[1::2]))
    if len(moves) % 2 != 0:
        pairs.append((moves[-1], ''))

    return [
        (index + 1, x[0], x[1])
        for index, x in enumerate(pairs)
    ]
