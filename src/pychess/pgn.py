from . import constant as c


def parse_move_history(move_history):
    moves = [
        parse_move(m)
        for m in move_history
    ]

    return _pair_moves(moves)


def parse_move(move):
    castling = _get_castling_symbol(move)
    if castling is not None:
        return castling

    promotion_string = _get_promotion_string(move)
    if promotion_string is not None:
        return promotion_string

    return _get_standard_move_string(move)


def _get_standard_move_string(move):
    check_mate = _get_check_mate_symbol(move)
    piece_str, capture = _get_piece_and_capture(move)
    disambiguate = _get_disambiguation(move)

    return f'{piece_str}{disambiguate}{capture}{move.dst.address}{check_mate}'


def _get_check_mate_symbol(move):
    if move.is_mate:
        return '#'
    elif move.is_check:
        return '+'
    else:
        return ''


def _get_capture_symbol(move):
    return 'x' if move.is_capture else ''


def _get_castling_symbol(move):
    if not move.castling_done:
        return

    return (
        'O-O'
        if move.is_king_side_castling
        else 'O-O-O'
    )


def _get_promotion_string(move):
    promoted_piece = move.promoted_piece
    if promoted_piece is None:
        return

    promotion = promoted_piece.code.upper()
    check_mate = _get_check_mate_symbol(move)
    capture = _get_capture_symbol(move)
    return f'{move.dst.address}={promotion}{capture}{check_mate}'


def _get_disambiguation(move):
    return (
        move.disambiguate
        if move.disambiguate is not None
        else ''
    )


def _get_piece_and_capture(move):
    capture = _get_capture_symbol(move)
    if move.piece.type == c.PieceType.pawn:
        piece_str = ''
        if move.is_capture:
            capture = f'{move.src.x_address}{capture}'
    else:
        piece_str = move.piece.code.upper()

    return piece_str, capture


def _pair_moves(moves):
    pairs = list(zip(moves[::2], moves[1::2]))
    if len(moves) % 2 != 0:
        pairs.append((moves[-1], ''))

    return [
        (index + 1, x[0], x[1])
        for index, x in enumerate(pairs)
    ]
