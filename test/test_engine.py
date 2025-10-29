from engine.game_board import GameBoard, Coord, GameState
from runner.codec import Move, Player
import unittest


class EngineTest(unittest.TestCase):
    def test_straight_victory(self):
        b = GameBoard()

        for i in range(4):
            b.make_move(Move(0))

            if i != 3:
                b.make_move(Move(1))

        self.assertEqual(b.state(), GameState.PLAYER_1_WIN)

    def test_diagonal_victory(self):
        b = GameBoard()

        """
        X = player1, Y = player2
        
              X
            X X 
          X Y Y
        X Y X Y Y
        """

        b.make_move(Move(0))
        b.make_move(Move(3))

        b.make_move(Move(2))
        b.make_move(Move(3))

        b.make_move(Move(3))
        b.make_move(Move(1))

        b.make_move(Move(1))
        b.make_move(Move(2))

        b.make_move(Move(2))
        b.make_move(Move(4))

        b.make_move(Move(3))

        self.assertEqual(b.state(), GameState.PLAYER_1_WIN)


if __name__ == "__main__":
    unittest.main()
