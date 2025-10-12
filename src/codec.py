from dataclasses import dataclass
import struct
import datetime
from typing import Self, List
from enum import Enum
from typing import BinaryIO, Union

class DecodeError(Exception):
    pass

class EncodeableEnum(Enum):
    @staticmethod
    def FORMAT_STRING() -> str:
        return "<c"

    @staticmethod
    def LENGTH():
        return struct.calcsize(MessageType.FORMAT_STRING())

    def encode(self):
        return struct.pack(self.FORMAT_STRING(), self.value)

    @classmethod
    def decode(cls, data: BinaryIO):
        return cls(struct.unpack(cls.FORMAT_STRING(), data.read(struct.calcsize(cls.FORMAT_STRING())))[0])


class MessageType(EncodeableEnum):
    GAME_START = 0
    MAKE_MOVE = 1
    
    @staticmethod
    def FORMAT_STRING() -> str:
        return "<B"


class Player(EncodeableEnum):
    PLAYER_1 = b'1'
    PLAYER_2 = b'2'

    @staticmethod
    def FORMAT_STRING() -> str:
        return "<c"


@dataclass
class Move:
    column: int

    FORMAT_STRING = "<B"

    def encode(self) -> bytes:
        return struct.pack(self.FORMAT_STRING, self.column)

    @classmethod
    def decode(cls, data: BinaryIO):
        return cls(column = struct.unpack(cls.FORMAT_STRING, data.read(struct.calcsize(cls.FORMAT_STRING)))[0])


@dataclass
class Header:
    msg_type: MessageType
    msg_length: int

    MSG_LENGTH_FORMAT_STRING = "<H"
    LENGTH = struct.calcsize(MSG_LENGTH_FORMAT_STRING) + MessageType.LENGTH()

    def encode(self)  -> bytes:
        return self.msg_type.encode() + struct.pack(self.MSG_LENGTH_FORMAT_STRING, self.msg_length)

    @classmethod
    def decode(cls, data: BinaryIO) -> Self:
        msg_type = MessageType.decode(data)
        msg_length = struct.unpack(cls.MSG_LENGTH_FORMAT_STRING, data.read(struct.calcsize(cls.MSG_LENGTH_FORMAT_STRING)))[0]
        return cls(msg_type=msg_type, msg_length=msg_length)

    def remaining_message_length(self) -> int:
        return self.msg_length - self.LENGTH
    
@dataclass
class MakeMove:
    header: Header
    move: Move

    def encode(self) -> bytes:
        return self.header.encode() + self.move.encode()

    @classmethod
    def decode(cls, header: Header, data: BinaryIO) -> Self:
        return cls(header=header, move=Move.decode(data))

@dataclass
class GameStart:
    header: Header
    your_player: Player
    time_per_move: datetime.timedelta
    moves: List[Move] 

    @staticmethod
    def format_string(len: int) -> str:
        return f"<cL{len}s"

    def encode(self) -> bytes:
        time_per_move = struct.pack("<L", self.time_per_move.total_seconds() * 1000)
        moves = b"".join(m.encode() for m in self.moves)

        fmt= self.format_string(len(self.moves))
        
        return self.header.encode() \
            + struct.pack(fmt, self.your_player.encode(), time_per_move, moves)

    @classmethod
    def decode(cls, header: Header, data: BinaryIO) -> Self:
        your_player = Player.decode(data)
        ms_per_move = struct.unpack("<L", data.read(4))[0]
        time_per_move = datetime.timedelta(milliseconds = ms_per_move)
        num_moves = struct.unpack("<B", data.read(1))[0]
        moves: List[Move] = []
        for _ in range(num_moves):
            moves.append(Move.decode(data))

        return cls(header=header, your_player=your_player, time_per_move = time_per_move, moves=moves)

def decode_generic(data: BinaryIO) -> Union[MakeMove, GameStart]:
    hdr = Header.decode(data)
    match hdr.msg_type:
        case MessageType.GAME_START:
            return GameStart.decode(hdr, data)
        case MessageType.MAKE_MOVE:
            return MakeMove.decode(hdr, data)
