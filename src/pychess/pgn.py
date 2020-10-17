import re
import collections


from . import constant as c
from .squarer import Square
from .mover import Move
from .piecer import Piece
from .boarder import Board


class NAMEDTUPLES:
    PARSE_HEADER_RESULT = collections.namedtuple(
        'PARSE_HEADER_RESULT',
        [
            'event',
            'site',
            'date',
            'round',
            'white',
            'black',
            'result',
            'white_elo',
            'black_elo',
            'eco',
            'event_date',
        ]
    )

    PARSE_MOVE_RESULT = collections.namedtuple(
        'PARSE_MOVE_RESULT',
        [
            'no_move_result',
            'move_num',
            'white_castling',
            'white_move',
            'white_piece',
            'white_capture',
            'white_dst',
            'white_promotion',
            'white_check_mate',
            'black_castling',
            'black_move',
            'black_piece',
            'black_capture',
            'black_dst',
            'black_promotion',
            'black_check_mate',
            'result',
        ]
    )

    GAME_DATA = collections.namedtuple(
        'GAME_DATA',
        ['header_data', 'moves_data']
    )

    GAME_MOVE_RESULT = collections.namedtuple(
        'GAME_MOVE_RESULT',
        [
            'castling',
            'src',
            'dst',
        ]
    )

    PIECE_STR_RESULT = collections.namedtuple(
        'PIECE_STR_RESULT',
        [
            'piece_type',
            'src_addr',
            'partial_addr',
        ]
    )


class REGEX:
    move_num = r"([\d]+)"
    literal_dot = r"\."
    group_starts = r"("
    non_capturing_group_starts = r"(?:"
    no_move_result = r"^(1-0|0-1|1/2-1/2)$"
    group_ends = r")"
    castling = r"(O-O-O|O-O)"
    alternative = r"|"
    piece = r"([BKNRQ]?[a-h]?[1-8]?|[a-h]?)"
    capture = r"(x)?"
    address = r"([a-h]{1}[1-8]{1})"
    check_mate = r"(\+|\#)?"
    result = r"(1-0|0-1|1/2-1/2)?"
    zero_or_one = r"?"
    promotion = r"(?:=([BKNRQ]))?"
    possible_white_space = r"\s*"

    HEADER = ''.join([
        r"\[Event\s?\"(.+)?\"\]\s?",
        r"\[Site\s?\"(.+)?\"\]\s?",
        r"\[Date\s?\"(.+)?\"\]\s?",
        r"\[Round\s?\"(.+)?\"\]\s?",
        r"\[White\s?\"(.+)?\"\]\s?",
        r"\[Black\s?\"(.+)?\"\]\s?",
        r"\[Result\s?\"(.+)?\"\]\s?",
        r"(?:\[WhiteElo\s?\"(.+)?\"\])?\s?",
        r"(?:\[BlackElo\s?\"(.+)?\"\])?\s?",
        r"(?:\[ECO\s?\"(.+)?\"\])?\s?",
        r"(?:\[EventDate\s?\"(.+)?\"\])?\s?",
    ])

    MOVE = ''.join([
        non_capturing_group_starts,  # group 1

        no_move_result,

        possible_white_space,

        alternative,

        move_num,

        literal_dot,

        possible_white_space,

        non_capturing_group_starts,

        castling,

        alternative,

        group_starts,  # group 2

        piece,

        capture,

        address,

        promotion,

        check_mate,

        group_ends,  # group 2 ends

        group_ends,  # group 1 ends

        possible_white_space,

        non_capturing_group_starts,

        castling,

        alternative,

        group_starts,

        piece,

        capture,

        address,

        promotion,

        check_mate,

        group_ends,  # group 3 ends

        group_ends,

        zero_or_one,

        possible_white_space,

        result,

        group_ends,
    ])


class PGN2MOVES:
    def __init__(self, pgn_file_path=None):
        self._board = None
        self._games = self._parse_game_file(file_path=pgn_file_path)
        self._nb_games = len(self._games)
        self._game_info = None

    @property
    def nb_games(self):
        return self._nb_games

    @property
    def game_info(self):
        if self._game_info is None:
            self._game_info = self._get_game_info()
        return self._game_info

    def get_moves(self, game_index):
        self._board = Board()
        game = self._games[game_index]
        return self._get_game_moves(game)

    def _get_game_info(self):
        info = []
        for game in self._games:
            header_data = game.header_data
            info.append(f'{self._generate_info_string(header_data)}')

        return info

    def _parse_game_file(self, file_path):
        text = self._get_pgn_text(file_path)
        header_data = self._parse_header(text)
        move_data = self._parse_moves(text)
        error_msg = f'header={len(header_data)}, moves={len(move_data)}'
        assert len(header_data) == len(move_data), error_msg
        return [
            NAMEDTUPLES.GAME_DATA(*data)
            for data in zip(header_data, move_data)
        ]

    def _get_game_moves(self, game):
        if game.moves_data[0].no_move_result is not None:
            return []

        moves = []
        for move in game.moves_data:
            white_move = self._get_player_move(move, c.Color.white)
            if white_move is not None:
                moves.append(white_move)

            black_move = self._get_player_move(move, c.Color.black)
            if black_move is not None:
                moves.append(black_move)

        return moves

    def _get_player_move(self, move, player):
        promotion = None
        if player == c.Color.white:
            castling = move.white_castling
            move_str = move.white_move
            if move.white_promotion is not None:
                promotion = self._piece_type_from_code(
                    move.white_promotion
                )
        else:
            castling = move.black_castling
            move_str = move.black_move
            if move.black_promotion is not None:
                promotion = self._piece_type_from_code(
                    move.black_promotion
                )

        if not any([castling, move_str]):
            return

        result = self._pgn_move_to_src_dst(move, player)
        if result.castling is not None:
            src, dst = self._apply_castling(result.castling, player)
            return src, dst, promotion

        self._apply_move(result, promotion, player)

        return Square(result.src), Square(result.dst), promotion

    @staticmethod
    def _get_pgn_text(file_path):
        text = None
        with open(file_path, 'r') as fp:
            text = fp.read()
        return text

    def _apply_move(self, result, promotion, player):
        src = Square(result.src)
        dst = Square(result.dst)
        if not all([src, dst]):
            error_msg = (
                f'Cannot apply move as both src "{src}" '
                f'and dst "{dst}" are not known '
            )
            raise RuntimeError(error_msg)

        self._board.move(src, dst)

        if promotion is not None:
            promoted_piece = self._create_promoted_piece(
                piece_type=promotion,
                color=player,
                dst=dst
            )
            self._board.promote(promoted_piece, dst)

    def _create_promoted_piece(self, piece_type, color, dst):
        max_order = 0
        existing_pieces = self._get_existing_pieces(
            piece_type=piece_type,
            color=color
            )
        if existing_pieces:
            max_order = max([p.order for p in existing_pieces]) + 1

        return Piece(
            piece_type=piece_type,
            color=color,
            order=max_order,
        )

    def _get_existing_pieces(self, piece_type, color):
        return [
            piece
            for piece in self._board.pieces
            if piece.type == piece_type and piece.color == color
        ]

    def _pgn_move_to_src_dst(self, move, player):
        if player == c.Color.white:
            castling = move.white_castling
            piece_str = move.white_piece
            dst_addr = move.white_dst
        else:
            castling = move.black_castling
            piece_str = move.black_piece
            dst_addr = move.black_dst

        if castling is not None:
            return NAMEDTUPLES.GAME_MOVE_RESULT(
                castling=castling,
                src=None,
                dst=None,
            )

        piece_str_result = self._parse_piece_str(piece_str)
        if piece_str_result.src_addr is not None:
            return NAMEDTUPLES.GAME_MOVE_RESULT(
                castling=None,
                src=piece_str_result.src_addr,
                dst=dst_addr,
            )
        elif piece_str_result.partial_addr is not None:
            src_addr = self._get_source_from_type_and_addr(
                player=player,
                piece_type=piece_str_result.piece_type,
                partial_addr=piece_str_result.partial_addr,
                dst_addr=dst_addr,
            )
        else:
            src_addr = self._get_source_from_type_and_dst(
                player=player,
                piece_type=piece_str_result.piece_type,
                dst_addr=dst_addr,
            )

        return NAMEDTUPLES.GAME_MOVE_RESULT(
            castling=None,
            src=src_addr,
            dst=dst_addr,
        )

    def _apply_castling(self, castling_string, player):
        is_short_castle = castling_string == 'O-O'
        return self._board.castle(
            player=player,
            is_short_castle=is_short_castle
        )

    def _get_source_from_type_and_addr(
            self, player, piece_type, partial_addr, dst_addr
    ):
        tried_moves = []
        is_x = partial_addr in list('abcdefgh')
        possible_pieces = [
            piece
            for piece in self._board.pieces
            if piece.type == piece_type and piece.color == player
        ]
        for piece in possible_pieces:
            if piece.type != piece_type or piece.color != player:
                continue

            src = self._board.get_square(piece)
            addr_to_check = src.x_address if is_x else src.y_address
            if addr_to_check != partial_addr:
                continue

            is_move_legal = Move.is_board_move_legal(
                board=self._board,
                src=src,
                dst=Square(dst_addr),
                piece=piece,
            )
            if is_move_legal:
                return src.address
            else:
                tried_moves.append(Move(piece, src, Square(dst_addr)))
        else:
            move_str = '\n'.join([str(m) for m in tried_moves])
            error_msg = (
                '\n\nERROR:\nTried following moves '
                f'for piece_type="{piece_type}", '
                f'with color="{player}" and partial address="{partial_addr}", '
                f'trying to move to "{dst_addr}", '
                f'none of the moves is legal:\n{move_str}\n\n'
                f'The board fore the move looks like this:\n{self._board}\n\n'
            )
            raise RuntimeError(error_msg)

    def _get_source_from_type_and_dst(self, player, piece_type, dst_addr):
        tried_moves = []
        dst = Square(dst_addr)
        possible_pieces = self._get_existing_pieces(piece_type, player)
        for piece in possible_pieces:
            src = self._board.get_square(piece)
            is_move_legal = Move.is_board_move_legal(
                board=self._board,
                src=src,
                dst=dst,
                piece=piece,
            )
            if is_move_legal:
                return src.address
            else:
                tried_moves.append(Move(piece, src, dst))
        else:
            move_str = '\n'.join([str(m) for m in tried_moves])
            error_msg = (
                '\n\nERROR:\nTried following moves '
                f'for piece_type="{piece_type}", '
                f'with color="{player}" and trying to move to "{dst_addr}", , '
                f'none of the moves is legal:\n{move_str}\n\n'
                f'The board fore the move looks like this:\n{self._board}\n\n'
            )
            raise RuntimeError(error_msg)

    def _parse_piece_str(self, piece_str):
        piece_type = None
        partial_addr = None
        code = None
        if not piece_str:
            code = 'P'
        elif piece_str in list('abcdefgh'):
            code = 'P'
            partial_addr = piece_str
        elif len(piece_str) == 3:
            return NAMEDTUPLES.PIECE_STR_RESULT(
                piece_type=None,
                srd_addr=piece_str[1:],
                partial_addr=None,
            )
        elif len(piece_str) == 2:
            code, partial_addr = piece_str
        elif len(piece_str) == 1:
            code = piece_str
        else:
            error_msg = f'Unknown piece string "{piece_str}"'
            raise RuntimeError(error_msg)

        piece_type = self._piece_type_from_code(code)

        return NAMEDTUPLES.PIECE_STR_RESULT(
            piece_type=piece_type,
            src_addr=None,
            partial_addr=partial_addr,
        )

    @staticmethod
    def _generate_info_string(header_data):
        out = []

        event = header_data.event
        if event is not None:
            out.append(f'[Event "{event}"]')

        site = header_data.site
        if site is not None:
            out.append(f'[Site "{site}"]')

        date = header_data.date
        if date is not None:
            out.append(f'[Date "{date}"]')

        round_ = header_data.round
        if round_ is not None:
            out.append(f'[Round "{round_}"]')

        white = header_data.white
        if white is not None:
            out.append(f'[White "{white}"]')

        black = header_data.black
        if black is not None:
            out.append(f'[Black "{black}"]')

        result = header_data.result
        if result is not None:
            out.append(f'[Result "{result}"]')

        white_elo = header_data.white_elo
        if white_elo is not None:
            out.append(f'[White ELO "{white_elo}"]')

        black_elo = header_data.black_elo
        if black_elo is not None:
            out.append(f'[Black ELO "{black_elo}"]')

        eco = header_data.eco
        if eco is not None:
            out.append(f'[ECO "{eco}"]')

        event_date = header_data.event_date
        if event_date is not None:
            out.append(f'[Event Date "{event_date}"]')

        return '\n'.join(out)

    @staticmethod
    def _parse_header(pgn_text):
        matches = re.finditer(REGEX.HEADER, pgn_text, re.MULTILINE)
        return [
            NAMEDTUPLES.PARSE_HEADER_RESULT(*match.groups())
            for match in matches
        ]

    @staticmethod
    def _parse_moves(pgn_text):
        matches = re.finditer(REGEX.MOVE, pgn_text, re.MULTILINE)
        all_moves = [
            NAMEDTUPLES.PARSE_MOVE_RESULT(*match.groups())
            for match in matches
        ]

        games = []
        game = []
        for move in all_moves:
            if move.no_move_result is not None:
                games.append([move])
                continue

            game.append(move)
            if move.result is not None:
                games.append(game)
                game = []

        return games

    @staticmethod
    def _piece_type_from_code(code):
        code = code.upper()
        if code == 'P':
            return c.PieceType.pawn
        elif code == 'B':
            return c.PieceType.bishop
        elif code == 'K':
            return c.PieceType.king
        elif code == 'N':
            return c.PieceType.knight
        elif code == 'Q':
            return c.PieceType.queen
        elif code == 'R':
            return c.PieceType.rook
        else:
            error_msg = f'Unknown piece code "{code}"'
            raise RuntimeError(error_msg)


class MOVES2PGN:
    def __init__(self, move_history):
        self._move_history = move_history
        self._moves = None
        self._text = None

    @property
    def moves(self):
        if self._moves is None:
            self._moves = self._parse_move_history(self._move_history)
        return self._moves

    @property
    def text(self):
        if self._text is None:
            self._text = self._generate_game_text()
        return self._text

    def _parse_move_history(self, move_history):
        moves = [
            self._parse_move(m)
            for m in move_history
        ]

        return self._pair_moves(moves)

    def _generate_game_text(self):
        game = []
        history = self._parse_move_history(self._move_history)
        for move_num, m1, m2 in history:
            line = f'{move_num}.{m1} {m2}'
            game.append(line)

        return ' '.join(game)

    def _parse_move(self, move):
        winning_string = ''
        if move.winner is not None:
            if move.winner == c.Color.white:
                winning_string = ' 1-0'
            else:
                winning_string = ' 0-1'

        castling = self._get_castling_symbol(move)
        if castling is not None:
            return castling

        promotion_string = self._get_promotion_string(move)
        if promotion_string is not None:
            return f'{promotion_string}{winning_string}'

        std_string = self._get_standard_move_string(move)

        return f'{std_string}{winning_string}'

    def _get_standard_move_string(self, move):
        check_mate = self._get_check_mate_symbol(move)
        piece_str, capture = self._get_piece_and_capture(move)
        disambiguate = self._get_disambiguation(move)
        dst = move.dst.address

        return f'{piece_str}{disambiguate}{capture}{dst}{check_mate}'

    def _get_promotion_string(self, move):
        promoted_piece = move.promoted_piece
        if promoted_piece is None:
            return

        promotion = promoted_piece.code.upper()
        check_mate = self._get_check_mate_symbol(move)
        capture = self._get_capture_symbol(move)
        return f'{move.dst.address}{capture}={promotion}{check_mate}'

    def _get_piece_and_capture(self, move):
        capture = self._get_capture_symbol(move)
        if move.piece.type == c.PieceType.pawn:
            piece_str = ''
            if move.is_capture:
                capture = f'{move.src.x_address}{capture}'
        else:
            piece_str = move.piece.code.upper()

        return piece_str, capture

    @staticmethod
    def _get_check_mate_symbol(move):
        if move.is_mate:
            return '#'
        elif move.is_check:
            return '+'
        else:
            return ''

    @staticmethod
    def _get_capture_symbol(move):
        return 'x' if move.is_capture else ''

    @staticmethod
    def _get_castling_symbol(move):
        if not move.castling_done:
            return

        return (
            'O-O'
            if move.is_king_side_castling
            else 'O-O-O'
        )

    @staticmethod
    def _get_disambiguation(move):
        return (
            move.disambiguate
            if move.disambiguate is not None
            else ''
        )

    @staticmethod
    def _pair_moves(moves):
        pairs = list(zip(moves[::2], moves[1::2]))
        if len(moves) % 2 != 0:
            pairs.append((moves[-1], ''))

        return [
            (index + 1, x[0], x[1])
            for index, x in enumerate(pairs)
        ]
