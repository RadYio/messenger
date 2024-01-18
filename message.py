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
    def decode(cls, data: bytes) -> Message :
        ...

    def encode(self) -> bytes:
        ...

class MessageRequest(Message):

    threadid : int
    nbrmsg : int

    def __init__(self, threadid : int, nbrmsg : int):
        self.threadid = threadid
        self.nbrmsg = nbrmsg
    @classmethod
    def decode(cls, data: bytes) -> Message :
        ...
        #(code, userid, threadid, nbrmsg) = struct.unpack('BQQB', data)
        #return (code, userid, threadid, nbrmsg)
    
    def encode(self) -> bytes:
        return struct.pack('BQQB', self.code.MESSAGES_REQUEST, self.userid, self.threadid, self.nbrmsg)

class MessageResponse(Message):

    nbrmsg : int
    messageid : int
    pubdate : datetime
    authoruserid : int
    lenghtmsg : int
    message : str

    def __init__(self, nbrmsg : int, messageid : int, pubdate : datetime, authoruserid : int, lenghtmsg : int, message : str):
        self.nbrmsg = nbrmsg
        self.messageid = messageid
        self.pubdate = pubdate
        self.authoruserid = authoruserid
        self.lenghtmsg = lenghtmsg
        self.message = message

    @classmethod    
    def decode(cls, data: bytes) -> Message :
        ...
         #size = calcsize
         #(code, userid, ) = unq data[0:size]
    def encode(self) -> bytes :
            msgresponse = struct.pack('BQB', self.code.MESSAGES_RESPONSE, self.userid, self.nbrmsg)
            for i in range (0,self.nbrmsg):
                header = struct.pack('QQQB', self.messageid, self.pubdate, self.authoruserid, self.lenghtmsg)
                msgresponse += header
                i += 1
            #messages = bytes(message)
            #msgresponse +=  messages
            return msgresponse
class PostRequest(Message):

    threadid : int
    lenghtmsg : int
    message : str

    def __init__(self, threadid : int, lenghtmsg : int, message : str):
        self.threadid = threadid
        self.lenghtmsg = lenghtmsg
        self.message = message

    @classmethod 
    def decode(cls, data: bytes) -> Message :
        ...#(code, userid, threadid, lenghtmsg)        
    def encode(self) -> bytes :
        ...
        #request= struct.pack('BQQB', self.code.POST_REQUEST, self.userid, self.threadid, self.lenghtmsg)


class PostResponse(Message):

    threadid : int
    messageid : int

    def __init__(self, threadid : int, messageid : int):
        self.threadid = threadid
        self.messageid = messageid

    @classmethod
    def decode(cls, data: bytes) -> Message :
        ...
        #(code, userid, threadid, messageid) = struct.unpack('BQQQ', data)
        #return  (code, userid, threadid, messageid)   
    def encode(self) -> bytes:
        return struct.pack('BQQQ', self.code.POST_RESPONSE, self.userid, self.threadid, self.messageid)
