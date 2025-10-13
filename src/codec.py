from dataclasses import dataclass
import struct
import datetime
from typing import Self, List, Protocol
from enum import Enum
from typing import BinaryIO, Union
from io import BytesIO

"""
Example Usage:

# To read a message
stdin_line = however_the_hell_you_read_a_line_of_stdin()



"""

class MessageType(Enum):
    GAME_START = 0
    MAKE_MOVE = 1
    
class Player(Enum):
    PLAYER_1 = b'1'
    PLAYER_2 = b'2'

@dataclass
class Move:
    column: int

@dataclass
class Header:
    msg_type: MessageType
    msg_length: int

    FORMAT_STRING = "<BH"
    LENGTH = struct.calcsize(FORMAT_STRING) 

    def encode(self)  -> bytes:
        return struct.pack(self.FORMAT_STRING, self.msg_type.value, self.msg_length)

    @classmethod
    def decode(cls, data: bytes) -> Self:
        (msg_type, msg_length) = struct.unpack(cls.FORMAT_STRING, data)
        return cls(msg_type=MessageType(msg_type), msg_length=msg_length)

    def remaining_message_length(self) -> int:
        return self.msg_length - self.LENGTH
    
@dataclass
class MakeMove:
    header: Header
    move: Move

    FORMAT_STRING = "<B"
    LENGTH = Header.LENGTH + struct.calcsize(FORMAT_STRING)

    @staticmethod
    def from_move(move: Move):
        hdr = Header(msg_type = MessageType.MAKE_MOVE, msg_length = MakeMove.LENGTH)
        return MakeMove(header=hdr, move = move)

    def encode(self) -> bytes:
        return self.header.encode() + struct.pack(MakeMove.FORMAT_STRING, self.move.column)

    @classmethod
    def decode(cls, header: Header, data: bytes) -> Self:
        return cls(header=header, move=Move(struct.unpack(MakeMove.FORMAT_STRING, data)[0]))

@dataclass 
class GameParams:
    your_player: Player
    time_per_move: datetime.timedelta
    moves: List[Move] 

@dataclass
class GameStartMsg:
    header: Header
    params: GameParams

    FIXED_FORMAT_STRING = "<cLB"
    FIXED_LENGTH = struct.calcsize(FIXED_FORMAT_STRING)

    @staticmethod
    def VARIABLE_FORMAT_STRING(num_moves: int):
        return f"<{num_moves}s"

    @staticmethod 
    def from_game_params(params: GameParams):
        msg_length = Header.LENGTH + GameStartMsg.FIXED_LENGTH + len(params.moves)
        return GameStartMsg(
            header = Header(msg_type=MessageType.GAME_START, msg_length=msg_length),
            params = params
        )

    def encode(self) -> bytes:
        num_moves = len(self.params.moves)
        return self.header.encode() \
            + struct.pack(GameStartMsg.FIXED_FORMAT_STRING,
                           self.params.your_player.value, 
                           int(self.params.time_per_move.total_seconds() * 1000),
                           num_moves) \
            + struct.pack(self.VARIABLE_FORMAT_STRING(num_moves), b"".join(m.column.to_bytes(1, 'little') for m in self.params.moves))

    @classmethod
    def decode(cls, header: Header, data: bytes) -> Self:
        buf = BytesIO(data)
        (your_player, ms_per_move, num_moves) = struct.unpack(cls.FIXED_FORMAT_STRING, buf.read(cls.FIXED_LENGTH))

        time_per_move = datetime.timedelta(milliseconds = ms_per_move)

        variable_fmt = cls.VARIABLE_FORMAT_STRING(num_moves)
        variable_length = struct.calcsize(variable_fmt)
        moves: List[Move] = [Move(b) for b in struct.unpack(variable_fmt, 
                     buf.read(variable_length))[0]]

        return cls(header=header, params=GameParams(your_player=Player(your_player), time_per_move = time_per_move, moves=moves))


AnyMessage = Union[Move, GameParams]


def decode(data: bytes) -> AnyMessage:
    buffer = BytesIO(data)
    hdr = Header.decode(buffer.read(Header.LENGTH))
    rest = buffer.read(hdr.remaining_message_length())

    match hdr.msg_type:
        case MessageType.GAME_START:
            return GameStartMsg.decode(hdr, rest).params
        case MessageType.MAKE_MOVE:
            return MakeMove.decode(hdr, rest).move

class AsyncBuffer(Protocol):
    async def read(self, n: int) -> bytes:
        ...

async def async_decode(buffer: AsyncBuffer) -> AnyMessage:
    hdr = Header.decode(await buffer.read(Header.LENGTH))
    rest = await buffer.read(hdr.remaining_message_length())

    match hdr.msg_type:
        case MessageType.GAME_START:
            return GameStartMsg.decode(hdr, rest).params
        case MessageType.MAKE_MOVE:
            return MakeMove.decode(hdr, rest).move
