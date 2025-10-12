import unittest
import struct
import datetime
from io import BytesIO
from src.codec import (
        Move, Header, MessageType, MakeMove, GameStart, decode_generic
)
import sys

assert sys.byteorder == 'little'

class CodecTest(unittest.TestCase):
    def test_header(self) -> None:
        hdr_raw = b'\x01\x03\x00'
        hdr_buf = BytesIO(hdr_raw)

        hdr = Header.decode(hdr_buf)
        self.assertEqual(hdr.msg_type, MessageType.MAKE_MOVE)
        self.assertEqual(hdr.msg_length, 3)
        self.assertEqual(hdr_buf.tell(), 3)
    
        self.assertEqual(hdr.encode(), hdr_raw)

    def test_make_move(self) -> None:
        move_raw = b'\x01\x03\x00\x06'
        move_buf = BytesIO(move_raw)

        move = decode_generic(move_buf)

        assert isinstance(move, MakeMove)

        self.assertEqual(move.move, Move(6))
        self.assertEqual(move_buf.tell(), len(move_raw))

        self.assertEqual(move.encode(), move_raw)

    def test_game_start(self):
        ms_per_move = 100
        ms_per_move_encoded = struct.pack('<L', ms_per_move)
        game_start_raw = b'\x00\x0C\x00\x31' + ms_per_move_encoded + b'\x03\x01\x00\x02'
        game_start_buf = BytesIO(game_start_raw)

        game_start = decode_generic(game_start_buf)

        assert isinstance(game_start, GameStart)
        self.assertAlmostEqual(game_start.time_per_move.total_seconds() * 1000, ms_per_move, places=3)
        self.assertEqual(game_start.moves, [Move(1), Move(0), Move(2)])



if __name__ == "__main__":
    unittest.main()
