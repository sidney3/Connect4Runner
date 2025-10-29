import unittest
import struct
import datetime
from io import BytesIO
import runner.codec as codec
import sys

assert sys.byteorder == "little"


class CodecTest(unittest.TestCase):
    def test_header(self) -> None:
        hdr_raw = b"\x01\x03\x00"

        hdr = codec.Header.decode(hdr_raw)
        self.assertEqual(hdr.msg_type, codec.MessageType.MAKE_MOVE)
        self.assertEqual(hdr.msg_length, 3)

        self.assertEqual(hdr.encode(), hdr_raw)

    def test_make_move(self) -> None:
        move_raw = b"\x01\x04\x00\x06"

        move = codec.decode(move_raw)

        print(type(move))
        assert isinstance(move, codec.Move)

        self.assertEqual(move, codec.Move(6))

        self.assertEqual(codec.MoveMsg.make(move).encode(), move_raw)

    def test_game_start(self):
        ms_per_move = 100
        ms_per_move_encoded = struct.pack("<L", ms_per_move)
        game_start = b"\x00\x0c\x00\x31" + ms_per_move_encoded + b"\x03\x01\x00\x02"

        game_params = codec.decode(game_start)

        assert isinstance(game_params, codec.Params)
        self.assertAlmostEqual(
            game_params.time_per_move.total_seconds() * 1000, ms_per_move, places=3
        )
        self.assertEqual(
            game_params.moves, [codec.Move(1), codec.Move(0), codec.Move(2)]
        )
        self.assertEqual(game_params.your_player, codec.Player.PLAYER_1)
        self.assertEqual(codec.ParamsMsg.make(game_params).encode(), game_start)


if __name__ == "__main__":
    unittest.main()
