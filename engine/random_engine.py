import runner.codec as codec
from engine.engine_main import engine_main
from engine.engine_base import EngineBase
from engine.game_board import GameBoard, GameState, NUM_ROWS, NUM_COLS

from random import randrange


class RandomEngine(EngineBase):
    def make_move(self, move: codec.Move):
        self._board.make_move(move)

    def get_move(self):
        assert self._board.state() == GameState.ONGOING
        for c in range(NUM_COLS):
            if self._board.column_space(c) > 0:
                return codec.Move(c)

        raise RuntimeError("Impossible")

    def on_move(self, move: codec.Move):
        assert self._board.state() == GameState.ONGOING
        self._board.make_move(move)

    def get_friendly(self):
        return self._friendly

    @classmethod
    def make(cls, params: codec.Params):
        cls._board = GameBoard()
        for move in params.moves:
            cls._board.make_move(move)
        cls._friendly = params.your_player
        return cls()


if __name__ == "__main__":
    engine_main(RandomEngine)
