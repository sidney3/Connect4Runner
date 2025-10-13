import unittest
import struct
import datetime
from io import BytesIO
from src.codec import (
        Player, Move, Header, MessageType, GameParams, MakeMove, GameStartMsg, decode_generic
)
import sys

assert sys.byteorder == 'little'

class CodecTest(unittest.TestCase):
    def test_header(self) -> None:
        hdr_raw = b'\x01\x03\x00'

        hdr = Header.decode(hdr_raw)
        self.assertEqual(hdr.msg_type, MessageType.MAKE_MOVE)
        self.assertEqual(hdr.msg_length, 3)
    
        self.assertEqual(hdr.encode(), hdr_raw)

    def test_make_move(self) -> None:
        move_raw = b'\x01\x04\x00\x06'

        move = decode_generic(move_raw)

        print(type(move))
        assert isinstance(move, Move)

        self.assertEqual(move, Move(6))

        self.assertEqual(MakeMove.from_move(move).encode(), move_raw)

    def test_game_start(self):
        ms_per_move = 100
        ms_per_move_encoded = struct.pack('<L', ms_per_move)
        game_start = b'\x00\x0C\x00\x31' + ms_per_move_encoded + b'\x03\x01\x00\x02'

        game_params= decode_generic(game_start)

        assert isinstance(game_params, GameParams)
        self.assertAlmostEqual(game_params.time_per_move.total_seconds() * 1000, ms_per_move, places=3)
        self.assertEqual(game_params.moves, [Move(1), Move(0), Move(2)])
        self.assertEqual(game_params.your_player, Player.PLAYER_1)
        self.assertEqual(GameStartMsg.from_game_params(game_params).encode(), game_start)


if __name__ == "__main__":
    unittest.main()
