import argparse
from dataclasses import dataclass
from typing import Self
from engine.game_board import Player
from itertools import product
from runner.engine_container import EngineContainer
from runner.run_one import GameResult, run_one


@dataclass
class RatingAdjustmentSettings:
    adjustment_factor: float = 30
    initial_elo: float = 1500


@dataclass
class MatchResult:
    wins: int = 0
    losses: int = 0
    draws: int = 0

    def flip(self):
        return MatchResult(wins=self.losses, losses=self.wins, draws=self.draws)


@dataclass
class Rating:
    elo: float
    settings: RatingAdjustmentSettings

    def __init__(self, settings: RatingAdjustmentSettings):
        self.elo = settings.initial_elo
        self.settings = settings

    def update(self, other: Self, result: MatchResult):
        win_probability = 1 / (1 + 10 ** ((other.elo - self.elo) / 400))
        num_games = result.wins + result.losses + result.draws
        score = result.wins + 0.5 * result.draws
        expected_score = win_probability * num_games

        self.elo = self.elo + self.settings.adjustment_factor * (score - expected_score)


def run_match(playerA: EngineContainer, playerB: EngineContainer) -> MatchResult:
    """Run a match between playerA and playerB.

    MatchResult is returned from playerB's perspective
    """

    res = MatchResult()

    round_one = run_one(playerA, playerB)

    res.draws += round_one == GameResult.DRAW
    res.wins += round_one == GameResult.PLAYER_1_WIN
    res.losses += round_one == GameResult.PLAYER_2_WIN

    round_two = run_one(playerB, playerA)

    res.draws += round_two == GameResult.DRAW
    res.wins += round_two == GameResult.PLAYER_2_WIN
    res.losses += round_two == GameResult.PLAYER_1_WIN

    return res


def compute_elo(
    engines: dict[int, EngineContainer],
    settings: RatingAdjustmentSettings,
    allowed_games: int = 50,
) -> dict[int, Rating]:
    engine_ids = engines.keys()
    engine_ratings = {engine_id: Rating(settings) for engine_id in engine_ids}

    num_rounds = allowed_games // (len(engines) ** 2)

    for _ in range(num_rounds):
        for id1, id2 in product(engine_ids, engine_ids):
            if id1 == id2:
                continue

            match_result = run_match(engines[id1], engines[id2])

            first_rating = engine_ratings[id1]
            second_rating = engine_ratings[id2]

            first_rating.update(second_rating, match_result)
            second_rating.update(first_rating, match_result.flip())

    return engine_ratings


def main(args: argparse.Namespace):
    container_args: dict[int, list[str]] = dict(enumerate(args.engine))
    engine_containers: dict[int, EngineContainer] = {
        i: EngineContainer(args) for (i, args) in container_args.items()
    }

    ratings = compute_elo(engine_containers, RatingAdjustmentSettings())

    print(f"{[(*container_args[id], ratings[id].elo) for id in container_args]}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument(
        "--engine",
        "-e",
        type=str,
        action="append",
        nargs="+",
        required=True,
        help="One of any number of engines to have participate in the elo arena",
    )
    parser.add_argument(
        "-t",
        "--timeout",
        default=100,
        help="The allowed delay between receiving and responding \
                        to a message",
    )

    return parser.parse_args()


if __name__ == "__main__":
    main(parse_args())
