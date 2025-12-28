import os
import asyncio
import subprocess
from typing import TypeVar, List, Optional, Coroutine, Any, Union
import runner.codec as codec
from datetime import timedelta


class EngineContainer:
    def __init__(self, args: List[str]):
        self._loop = asyncio.new_event_loop()

        self._engine = subprocess.Popen(
            args,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            bufsize=0,
            start_new_session=True,
        )

    def read_message(self):
        reader = self._engine.stdout
        assert reader

        return codec.decode_buffer(reader)

    def send_move(self, to_move: codec.Move):
        writer = self._engine.stdin
        assert writer

        writer.write(codec.MoveMsg.make(to_move).encode())

    def send_game_params(self, to_make: codec.Params):
        writer = self._engine.stdin
        assert writer

        msg = codec.ParamsMsg.make(to_make).encode()
        writer.write(msg)
