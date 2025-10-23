import asyncio
import subprocess
from typing import TypeVar, List, Optional, Coroutine, Any, Union
import runner.codec as codec
from datetime import timedelta

T = TypeVar("T")

class Timeout:
    pass

class EngineContainer:
    def __init__(self, timeout: Optional[timedelta], args: List[str]):
        self._loop = asyncio.new_event_loop()
        self._timeout = timeout

        self._engine = self._loop.run_until_complete(asyncio.create_subprocess_exec(
            *args,
            stdin = asyncio.subprocess.PIPE,
            stdout = asyncio.subprocess.PIPE,
        ))

    async def _with_timeout(self, coro: Coroutine[Any, Any, T]):
        if self._timeout:
            try:
                return await asyncio.wait_for(coro, self._timeout.total_seconds())
            except:
                return Timeout()
        else:
            return await coro

    def read_message(self):
        reader = self._engine.stdout
        assert reader

        with_tm = self._with_timeout(codec.async_decode(reader))

        return self._loop.run_until_complete(with_tm)


    def send_move(self, to_move: codec.Move):
        writer = self._engine.stdin
        assert writer

        writer.write(codec.MoveMsg.make(to_move).encode())
        self._loop.run_until_complete(writer.drain())

    def send_game_params(self, to_make: codec.Params):
        writer = self._engine.stdin
        assert writer

        msg = codec.ParamsMsg.make(to_make).encode()
        writer.write(msg)
        return self._loop.run_until_complete(writer.drain())

    def cleanup(self):
        """Properly terminate the engine subprocess and cleanup resources."""
        if self._engine and self._engine.returncode is None:
            try:
                # Close stdin to signal the engine to terminate
                if self._engine.stdin:
                    self._engine.stdin.close()

                # Wait for the process to terminate gracefully
                try:
                    self._loop.run_until_complete(asyncio.wait_for(self._engine.wait(), timeout=1.0))
                except asyncio.TimeoutError:
                    # Force kill if it doesn't terminate gracefully
                    self._engine.terminate()
                    try:
                        self._loop.run_until_complete(self._engine.wait())
                    except:
                        pass  # Process already terminated

                # Close stdout if it's still open
                if self._engine.stdout:
                    self._engine.stdout.close()
            except Exception:
                # If cleanup fails, just force kill the process
                try:
                    self._engine.terminate()
                except:
                    pass

    def __del__(self):
        """Ensure cleanup happens when the container is garbage collected."""
        self.cleanup()
