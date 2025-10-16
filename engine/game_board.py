from runner.codec import Move, Player
from enum import Enum
from typing import List, Optional

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

class GameBoard:
    def __init__(self):
        self._state = GameState.ONGOING
        self.columns: List[List[Player]] = [[] for _ in range(NUM_COLS)]
        assert(len(self.columns) == NUM_COLS)

        self._side_to_move = Player.PLAYER_1

    def flip_side_to_move(self):
        self._side_to_move = opposing_player(self._side_to_move)

    def state(self):
        return self._state

    def piece_at(self, row: int, col: int) -> Optional[Player]:
        assert row >= 0 and col >= 0 and col < NUM_COLS and row < NUM_ROWS

        if row >= len(self.columns[col]):
            return None

        return self.columns[col][row]

    def column_space(self, col: int):
        return NUM_ROWS - len(self.columns[col])

    def side_to_move(self):
        return self._side_to_move

    def make_move(self, move: Move):
        assert move.column < NUM_COLS
        assert self._state == GameState.ONGOING
        assert len(self.columns[move.column]) < NUM_ROWS

        start_row, start_col = len(self.columns[move.column]), move.column

        self.columns[move.column].append(self._side_to_move)

        directions = (
            (1,0), (-1, 0), (0, 1), (0, -1),
            (1, 1), (1, -1), (-1, 1), (-1,-1)
        )

        def streak_continues(row: int, col: int) -> bool:
            if not (cur_row >= 0 and cur_row < NUM_ROWS and cur_col >= 0 and cur_col < NUM_COLS):
                return False

            piece = self.piece_at(row, col)
            return piece != None and piece == self._side_to_move

        player_wins = False
        for row_delta, col_delta in directions:
            cur_row, cur_col = start_row, start_col
            streak = 0

            while streak_continues(cur_row, cur_col):
                streak += 1
                cur_row += row_delta
                cur_col += col_delta
            player_wins = player_wins or streak >= 4
        
        if player_wins:
            if self._side_to_move == Player.PLAYER_1:
                self._state = GameState.PLAYER_1_WIN
            else:
                self._state = GameState.PLAYER_2_WIN
        elif all([len(col) == NUM_COLS for col in self.columns]):
            self._state = GameState.DRAW
        else:
            self.flip_side_to_move()

