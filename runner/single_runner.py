import argparse
import runner.engine_container as engine_container
import engine.game_board as game_board
from datetime import timedelta
import runner.codec as codec
from runner.timer import Timer


def main(args: argparse.Namespace):
    print(f"{args=}")
    timeout = timedelta(milliseconds=args.timeout)
    timer = Timer()

    players = {
        codec.Player.PLAYER_1: engine_container.EngineContainer(args.player1),
        codec.Player.PLAYER_2: engine_container.EngineContainer(args.player2),
    }

    for player_type, player in players.items():
        player.send_game_params(
            codec.Params(your_player=player_type, time_per_move=timeout, moves=[])
        )

    board = game_board.GameBoard()

    while board.state() == game_board.GameState.ONGOING:
        friendly = players[board.side_to_move()]
        enemy = players[game_board.opposing_player(board.side_to_move())]

        timer.start()
        move_made = friendly.read_message()

        time_taken = timer.stop()
        if time_taken > timeout:
            print(f"Player {board.side_to_move()} timed out. Took {time_taken}")
            break

        assert isinstance(move_made, codec.Move)

        player_name = (
            "Player 1 (X)"
            if board.side_to_move() == codec.Player.PLAYER_1
            else "Player 2 (O)"
        )
        board.make_move(move_made)
        print(f"\n🎯 {player_name} places a piece in column {move_made.column}")

        print(f"{board}")

        if board.state() == game_board.GameState.ONGOING:
            enemy.send_move(move_made)


def parse_args():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument(
        "-t",
        "--timeout",
        type=int,
        default=100,
        help="The allowed delay between receiving and responding \
                        to a message",
    )
    parser.add_argument(
        "--player1",
        "-p1",
        nargs="+",
        required=True,
        help="""\
            Executable to run.
            Can be more than one string.
            E.x. python3 my_connect4_engine.py")
            """,
    )

    parser.add_argument(
        "--player2", "-p2", required=True, nargs="+", help="See --player1"
    )

    return parser.parse_args()


if __name__ == "__main__":
    main(parse_args())
