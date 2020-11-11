from .. import constant as c
from .gamer import Game


class Engine:
    def __init__(self, engine_type=c.EngineType.stockfish):
        self._engine_type = engine_type
        self._engine = _get_engine(engine_type=engine_type)

    def get_best_move(self, moves=None):
        moves = moves or []
        self._apply_moves(moves=moves)
        return self._engine.get_best_move()

    def _apply_moves(self, moves):
        moves = list(map(Game.parse_move_spec, moves))
        moves = list(map(lambda x: f'{x[0].address}{x[1].address}', moves))
        self._engine.set_position(moves)


def _get_engine(engine_type, engine_params=None):
    if engine_type == c.EngineType.stockfish:
        from stockfish import Stockfish
        # TODO: Added parameter for the engine here
        if engine_params is not None:
            pass

        return Stockfish()
    elif engine_type == c.EngineType.leela:
        raise NotImplementedError('Leela chess engine is not implelemented')
    else:
        error_msg = f"Unsupported engine {engine_type}"
        raise RuntimeError(error_msg)
