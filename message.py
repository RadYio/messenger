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

    code = Code.MESSAGES_REQUEST
    threadid : int
    nbrmsg : int

    def __init__(self, userid : int, threadid : int, nbrmsg : int):

        self.userid = userid
        self.threadid = threadid
        self.nbrmsg = nbrmsg

    @classmethod
    def decode(cls, data: bytes) -> Message :
        (_, userid, threadid, nbrmsg) = struct.unpack('BQQB', data)
        return MessageRequest(userid, threadid, nbrmsg)
          
    def encode(self) -> bytes:
        return struct.pack('BQQB', self.code, self.userid, self.threadid, self.nbrmsg)

class MessageResponse(Message):

    code = Code.MESSAGES_RESPONSE
    nbrmsg : int
    messageid : int
    pubdate : datetime
    authoruserid : int
    lenghtmsg : int
    message : str

    def __init__(self, userid : int, nbrmsg : int, messageid : int, pubdate : datetime, authoruserid : int, lenghtmsg : int, message : str):

        self.userid = userid
        self.nbrmsg = nbrmsg
        self.messageid = messageid
        self.pubdate = pubdate
        self.authoruserid = authoruserid
        self.lenghtmsg = lenghtmsg
        self.message = message

    @classmethod    
    def decode(cls, data: bytes) -> Message :
        size_start = struct.calcsize('BQB')
        (_, userid, nbrmsg) = struct.unpack('BQB', data[0:size_start])
        size_header = struct.calcsize('QQQH')
        for _i in range (0, nbrmsg):
            (messageid, pubdate, authoruserid, lenghtmsg) = struct.unpack('QQQH', data[size_start:size_header])
            size_start = size_header
            size_header += size_header 
        message = data[size_header:].decode()
        return MessageResponse(userid, nbrmsg, messageid, pubdate, authoruserid, lenghtmsg, message)

    def encode(self) -> bytes :
            msgresponse = struct.pack('BQB', self.code, self.userid, self.nbrmsg)
            for _i in range (0,self.nbrmsg):
                header = struct.pack('QQQH', self.messageid, self.pubdate, self.authoruserid, self.lenghtmsg)
                msgresponse += header
            byte_message = self.message.encode()
            msgresponse += byte_message
            return msgresponse
    
class PostRequest(Message):

    code = Code.POST_REQUEST
    threadid : int
    lenghtmsg : int
    message : str

    def __init__(self, userid : int, threadid : int, lenghtmsg : int, message : str):
        self.userid = userid
        self.threadid = threadid
        self.lenghtmsg = lenghtmsg
        self.message = message

    @classmethod 
    def decode(cls, data: bytes) -> Message :
        size_header = struct.calcsize('BQQH')
        (_, userid, threadid, lenghtmsg) = struct.unpack('BQQH', data[0:size_header])
        message = data[size_header:].decode()
        return PostRequest(userid, threadid, lenghtmsg, message)       
    def encode(self) -> bytes :
        request = struct.pack('BQQH', self.code, self.userid, self.threadid, self.lenghtmsg)
        byte_message = self.message.encode()
        request += byte_message
        return request



class PostResponse(Message):

    code = Code.POST_RESPONSE
    threadid : int
    messageid : int

    def __init__(self, userid : int, threadid : int, messageid : int):

        self.userid = userid 
        self.threadid = threadid
        self.messageid = messageid

    @classmethod
    def decode(cls, data: bytes) -> Message :
        (_, userid, threadid, messageid) = struct.unpack('BQQQ', data)
        return PostResponse(userid, threadid, messageid)   
    def encode(self) -> bytes:
        return struct.pack('BQQQ', self.code, self.userid, self.threadid, self.messageid)


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

class UsersRequest(Message):
    

    def __init__(self):
         ...
    @classmethod
    def decode(cls, data: bytes) -> Message:
        ...

    def encode(self) -> bytes:
        ...


class UsersResponse(Message):
    

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
              
