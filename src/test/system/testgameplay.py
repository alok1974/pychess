from pychess.gamer import Game


def log_game_stats(game):
    print(f'game.move_history:\n{game.move_history}\n')
    print(f'game.captured_black:\n{game.captured_black}\n')
    print(f'game.captured_white:\n{game.captured_white}\n')
    print(f'game.pieces_checking_black:\n{game.pieces_checking_black}\n')
    print(f'game.pieces_checking_white:\n{game.pieces_checking_white}\n')
    print(f'game.capturables:\n{game.capturables}\n')


def run_game(moves):
    game = Game()
    for index, move in enumerate(moves):
        mov_no = str(index + 1).zfill(2)
        print(f'Move {mov_no} - \'{move}\'')
        game.move(move)
        if game.is_game_over:
            print(f'{game.winner} wins!')
            log_game_stats(game)
            print(game.board)
            break
        print(game.board)
        print(game.description)


def parse_moves(move_string=None, game_file=None):
    moves = None
    if move_string is not None:
        moves = move_string.split('\n')
        print(moves)
        for move in moves:
            Game.parse_move_spec(move)

    return moves


def run(move_string=None, game_file=None):
    moves = parse_moves(move_string)
    run_game(moves)


if __name__ == '__main__':
    move_string_test2_game = (
        'e2e4\n'
        'e7e6\n'
        'd2d4\n'
        'd7d5\n'
        'b1d2\n'
        'd5e4\n'
        'd2e4\n'
        'd8d5\n'
        'e4c3\n'
        'd5e4\n'
        'c3e4\n'
        'f8b4\n'
        'c2c3\n'
        'b4c3\n'
        'b2c3\n'
        'g8f6\n'
        'e4f6\n'
        'g7f6\n'
        'd1g4\n'
        'f6f5\n'
        'g4g7\n'
        'h8f8\n'
        'c1a3\n'
        'b8c6\n'
        'g7f8\n'
        'e8d7\n'
        'f1b5\n'
        'a7a6\n'
        'f8e7'
    )

    move_string_test3_game = (
        'g1f3\n'
        'g8f6\n'
        'b1c3\n'
        'd7d5\n'
        'd2d4\n'
        'g7g6\n'
        'e2e4\n'
        'f6e4\n'
        'c3d5\n'
        'd8d5\n'
        'c2c4\n'
        'd5a5\n'
        'd1d2\n'
        'e4d2\n'
        'c1d2\n'
        'a5f5\n'
        'd2h6\n'
        'f8h6\n'
        'd4d5\n'
        'f5c2\n'
        'f3d2\n'
        'c2d2'
    )
    run(move_string=move_string_test3_game)
