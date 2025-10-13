import asyncio
import subprocess
from typing import List, Optional, Coroutine, Any
import src.codec as codec
from datetime import timedelta

class EngineRunner:
    def __init__(self, timeout: Optional[timedelta], args: List[str]):
        self._loop = asyncio.new_event_loop()
        self._timeout = timeout

        async def start_subprocess():
            return await asyncio.create_subprocess_exec(
                *args,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE
            )

        self._engine = self._loop.run_until_complete(asyncio.create_subprocess_exec(
            *args,
            stdin = asyncio.subprocess.PIPE,
            stdout = asyncio.subprocess.PIPE,
        ))

    async def _with_timeout(self, coro: Coroutine[Any, Any, Any]):
        if self._timeout:
            try:
                return await asyncio.wait_for(coro, self._timeout.total_seconds())
            except:
                return None
        else:
            return await coro

    async def receive_move(self) -> Optional[codec.Move]:
        reader = self._engine.stdout
        assert reader

        async def receive_move() -> Optional[codec.Move]:
            assert self._engine, "Need to add a runner!"
            hdr_bytes = await reader.read(codec.Header.LENGTH)
            hdr = codec.Header.decode(BinaryIO(await reader.read(codec.Header.LENGTH)))

            pass

        return self._loop.run_until_complete(self._with_timeout(receive_move()))




    def send_move(self, to_move: codec.Move):
        pass

    def start_game(self, to_make: codec.GameParams):
        assert self._engine, "Need to add a runner!"
        pass


