from typing import Optional
import runner.codec as codec
from engine.engine_base import EngineBase
import sys

def push_move(engine: EngineBase):
    move = engine.get_move()
    engine.on_move(move)
    sys.stdout.buffer.write(codec.MoveMsg.make(move).encode())
    sys.stdout.flush()

def engine_main(engine_cls: type[EngineBase]):
    engine: Optional[engine_cls] = None

    while True:
        hdr_bytes = sys.stdin.buffer.read(codec.Header.LENGTH)

        if(len(hdr_bytes) == 0):
            return
        else:
            assert len(hdr_bytes) == codec.Header.LENGTH

        hdr = codec.Header.decode(hdr_bytes)

        remaining_data = sys.stdin.buffer.read(hdr.remaining_message_length())

        match hdr.msg_type:
            case codec.MessageType.MAKE_MOVE:
                assert engine
                engine.on_move(codec.MoveMsg.decode(hdr, remaining_data).move)
                push_move(engine)
            case codec.MessageType.GAME_START:
                params = codec.ParamsMsg.decode(hdr, remaining_data).params
                engine = engine_cls.make(params)
                if params.your_player == codec.Player.PLAYER_1:
                    push_move(engine)
