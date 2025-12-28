import argparse
from runner.engine_container import EngineContainer
import engine.game_board as game_board
from datetime import timedelta
import runner.codec as codec
from runner.timer import Timer
from enum import Enum, auto


class GameResult(Enum):
    DRAW = game_board.GameState.DRAW
    PLAYER_1_WIN = game_board.GameState.PLAYER_1_WIN
    PLAYER_2_WIN = game_board.GameState.PLAYER_2_WIN


def run_one(
    player1: EngineContainer,
    player2: EngineContainer,
    time_per_move: timedelta = timedelta(milliseconds=100000),
) -> GameResult:
    players = {
        codec.Player.PLAYER_1: player1,
        codec.Player.PLAYER_2: player2,
    }
    timer = Timer()

    for player_type, player in players.items():
        player.send_game_params(
            codec.Params(your_player=player_type, time_per_move=time_per_move, moves=[])
        )

    board = game_board.GameBoard()

    while board.state() == game_board.GameState.ONGOING:
        friendly = players[board.side_to_move()]
        enemy = players[game_board.opposing_player(board.side_to_move())]

        timer.start()
        move_made = friendly.read_message()

        time_taken = timer.stop()
        if time_taken > time_per_move:
            print(f"Player {board.side_to_move()} timed out. Took {time_taken}")

            if board.side_to_move() == game_board.Player.PLAYER_1:
                return GameResult.PLAYER_2_WIN
            else:
                return GameResult.PLAYER_1_WIN

        assert isinstance(move_made, codec.Move)

        board.make_move(move_made)

        if board.state() == game_board.GameState.ONGOING:
            enemy.send_move(move_made)

    return GameResult(board.state())
