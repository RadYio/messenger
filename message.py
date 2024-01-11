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
        def ConnectRequest(lenghtID : bytes, lenghtPWD : bytes, passwd : bytes):
            lenghtID = len(self.userid)
            lenghtPWD = len(passwd)


            struct.pack('QBBBB', lenghtID, lenghtPWD, self.userid, passwd)
            if self.userid = 0 :
                    raise ValueError


"""
str(userid).encode("utf-8")
str(password).encode("utf-8")
"""


"""encoded = bytes(fonction, 'utf-8')"""
            
"""self.code.CONNECT_REQUEST"""

"""size = 5

arr = bytes(size)

print(arr)

résultat: b'\x00\x00\x00\x00\x00'

"""