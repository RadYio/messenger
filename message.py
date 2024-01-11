from __future__ import annotations

from datetime import datetime
from typing import AnyStr, Protocol
from enum import IntEnum
import struct

message = tuple[int, datetime, int, AnyStr]


# Python 3.10 and below
#
# from enum import Enum
#
# class Code(int, Enum):
#     CONNECT_REQUEST = 0
#     CONNECT_RESPONSE = 1
#     USERS_REQUEST = 2
#     USERS_RESPONSE = 3
#     MESSAGES_REQUEST = 4
#     MESSAGES_RESPONSE = 5
#     POST_REQUEST = 6
#     POST_RESPONSE = 7
#
#     @staticmethod
#     def decode(data: bytes) -> Code:
#         if len(data) > 0 and 0 <= data[0] <= 7:
#             return Code(data[0])
#         else:
#             raise ValueError(repr(data))


class Code(IntEnum):
    CONNECT_REQUEST = 0
    CONNECT_RESPONSE = 1
    USERS_REQUEST = 2
    USERS_RESPONSE = 3
    MESSAGES_REQUEST = 4
    MESSAGES_RESPONSE = 5
    POST_REQUEST = 6
    POST_RESPONSE = 7

    @staticmethod
    def decode(data: bytes) -> Code:
        if len(data) > 0 and 0 <= data[0] <= 7:
            return Code(data[0])
        else:
            raise ValueError(repr(data))


class Message(Protocol):

    code: Code
    userid: int

    @classmethod
    def decode(cls, data: bytes) -> Message:
        ...

    def encode(self) -> bytes:

        def MessageRequest(threadid : int, nbrmsg : int) -> bytes :
            code_msgrequest = self.code.MESSAGES_REQUEST
            userid_msgrequest = self.userid
            msgrequest = struct.pack('BQQB', code_msgrequest, userid_msgrequest, threadid, nbrmsg)
            return msgrequest 
        
        def MessageResponse():
            ...

        def PostRequest(threadid : int, lenghtmsg : int, message : str) -> bytes :
            code_postrequest = self.code.POST_REQUEST
            userid_postrequest = self.userid
            postrequest = struct.pack('BQQBH', code_postrequest, userid_postrequest, threadid, lenghtmsg, message)
