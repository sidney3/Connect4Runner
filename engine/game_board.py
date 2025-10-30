from runner.codec import Move, Player
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Tuple


class GameState(Enum):
    DRAW = 0
    PLAYER_1_WIN = 1
    PLAYER_2_WIN = 2
    ONGOING = 3


NUM_COLS = 7
NUM_ROWS = 6


def opposing_player(player: Player):
    if player == Player.PLAYER_1:
        return Player.PLAYER_2
    else:
        return Player.PLAYER_1


@dataclass
class Delta:
    row_delta: int
    col_delta: int


@dataclass
class Coord:
    row: int
    col: int

    def apply(self, d: Delta):
        return Coord(row=self.row + d.row_delta, col=self.col + d.col_delta)

    def in_bounds(self):
        return (
            self.row >= 0
            and self.row < NUM_ROWS
            and self.col >= 0
            and self.col < NUM_COLS
        )


class GameBoard:
    def __init__(self):
        self._state = GameState.ONGOING
        self.columns: List[List[Player]] = [[] for _ in range(NUM_COLS)]
        assert len(self.columns) == NUM_COLS

        self._side_to_move = Player.PLAYER_1

    def flip_side_to_move(self):
        self._side_to_move = opposing_player(self._side_to_move)

    def state(self):
        return self._state

    def piece_at(self, coord: Coord) -> Optional[Player]:
        assert coord.in_bounds()

        if coord.row >= len(self.columns[coord.col]):
            return None

        return self.columns[coord.col][coord.row]

    def column_space(self, col: int):
        return NUM_ROWS - len(self.columns[col])

    def side_to_move(self):
        return self._side_to_move

    def __str__(self):
        """Return a string representation of the Connect 4 board with game results."""
        lines: List[str] = []
        lines.append("")
        for row in range(NUM_ROWS):
            line = "│"
            for col in range(NUM_COLS):
                piece = self.piece_at(
                    Coord(row=NUM_ROWS - 1 - row, col=col)
                )  # Reverse row order for display
                if piece is None:
                    line += " ."
                elif piece == Player.PLAYER_1:
                    line += " X"
                elif piece == Player.PLAYER_2:
                    line += " O"
                else:
                    line += f" {piece}"
            line += " │"
            lines.append(line)
        lines.append("└───────────────┘")
        lines.append("  0 1 2 3 4 5 6")

        # Add game result messages if the game has ended
        if self._state == GameState.PLAYER_1_WIN:
            lines.append("")
            lines.append("🎉 🏆 PLAYER 1 (X) WINS! 🏆 🎉")
        elif self._state == GameState.PLAYER_2_WIN:
            lines.append("")
            lines.append("🎉 🏆 PLAYER 2 (O) WINS! 🏆 🎉")
        elif self._state == GameState.DRAW:
            lines.append("")
            lines.append("🤝 It's a DRAW! 🤝")

        return "\n".join(lines)

    def _check_win(self, pos: Coord):

        planes = (
            (Delta(0,1), Delta(0,-1)),
            (Delta(1,1), Delta(-1,-1)),
            (Delta(1,0), Delta(-1,0)),
            (Delta(1,-1), Delta(-1,-1)),
        )

        def delta_streak(start_pos: Coord, direction: Delta):
            def streak_continues(pos: Coord) -> bool:
                if not pos.in_bounds():
                    return False

                piece = self.piece_at(pos)

                return piece is not None and piece == self._side_to_move

            length = 0
            cur_pos = start_pos
            while streak_continues(cur_pos):
                length += 1
                cur_pos = cur_pos.apply(direction)

            return length

        return any(delta_streak(pos, p1) + delta_streak(pos, p2) - 1 >= 4 for (p1,p2) in planes)

    def make_move(self, move: Move):
        assert move.column < NUM_COLS
        assert self._state == GameState.ONGOING
        assert len(self.columns[move.column]) < NUM_ROWS

        start_row, start_col = len(self.columns[move.column]), move.column

        self.columns[move.column].append(self._side_to_move)

        if self._check_win(Coord(row=start_row, col=start_col)):
            if self._side_to_move == Player.PLAYER_1:
                self._state = GameState.PLAYER_1_WIN
            else:
                self._state = GameState.PLAYER_2_WIN
        elif all([len(col) == NUM_ROWS for col in self.columns]):
            self._state = GameState.DRAW
        else:
            self.flip_side_to_move()
