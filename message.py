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
        ...


class ConnectRequest(Message):

    username : int
    passwd : int
    #length_id : bytes = bytes(len(username))
    #length_pwd : bytes = bytes(len(passwd))

    def __init__(self, username : bytes, passwd : bytes, length_id : bytes, length_pwd : bytes):
         """self.username = username
         self.passwd = passwd
         self.length_id = length_id
         self.passwd = passwd"""

    @classmethod
    def decode(cls, data: bytes) -> Message:
        raise ValueError

    def encode(self) -> bytes:
        raise ValueError

class ConnectResponse(Message):
    

    def __init__(self):
         ...
    @classmethod
    def decode(cls, data: bytes) -> Message:
        ...

    def encode(self) -> bytes:
        ...

class UserRequest(Message):
    

    def __init__(self):
         ...
    @classmethod
    def decode(cls, data: bytes) -> Message:
        ...

    def encode(self) -> bytes:
        ...


class UserResponse(Message):
    

    def __init__(self,):
         ...
    @classmethod
    def decode(cls, data: bytes) -> Message:
        ...

    def encode(self) -> bytes:
        ...




        #start_of_request = struct.pack

    
    #start_of_request = struct.pack('BQBB', self.code.CONNECT_REQUEST, self.userid, length_id, length_pwd)

     #       if self.userid == 0 :
      #              raise ValueError
            
        #    completed_request = start_of_request + length_id + length_pwd + username + passwd
            
       #     return connectRequest
        

       # def connectResponse():

       #     struct.pack('Q',bytes(self.userid))

      #      if self.userid == 0 :
       #             raise ValueError
            
       # def userRequest():
              