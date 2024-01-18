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
    message_header : list[tuple[int, datetime, int, int]]
    message : str

    def __init__(self, userid : int, nbrmsg : int, message_header : list[tuple[int, datetime, int, int]], message : str):

        self.userid = userid
        self.nbrmsg = nbrmsg
        self.message_header = message_header
        self.message = message

    @classmethod    
    def decode(cls, data: bytes) -> Message :
        message_header : list[tuple[int, datetime, int, int]] = list()
        size_start = struct.calcsize('BQB')
        (_, userid, nbrmsg) = struct.unpack('BQB', data[0:size_start])
        size_header = struct.calcsize('QQQH')
        for i in range (0, nbrmsg):
            (messageid, datepub, userauthorid, lenghtmsg) = struct.unpack('QQQH', data[size_start:size_header])
            message_header[i] = (messageid, datepub, userauthorid, lenghtmsg)
            size_start = size_header
            size_header += size_header 
        message = data[size_header:].decode()
        return MessageResponse(userid, nbrmsg, message_header, message)

    def encode(self) -> bytes :
            msgresponse = struct.pack('BQB', self.code, self.userid, self.nbrmsg)
            for i in range (0,self.nbrmsg):
                header = struct.pack('QQQH', self.message_header[i])
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

    code = Code.CONNECT_REQUEST
    userid : int
    length_id : bytes
    length_pwd : bytes
    username : bytes
    passwd : bytes

    def __init__(self, userid : int, length_id : bytes, length_pwd : bytes, username : bytes, passwd : bytes,):
         self.userid = userid
         self.length_id = bytes(len(username))
         self.length_pwd = bytes(len(passwd))
         self.username = username
         self.passwd = passwd
         

    @classmethod
    def decode(cls, data: bytes) -> Message:
        (_, userid, length_id, length_pwd, username, passwd) = struct.unpack('BQBBBB', data)
        return ConnectRequest(userid, length_id, length_pwd, username, passwd)

    def encode(self) -> bytes:
        return struct.pack('BQBBBB', self.code, self.userid, self.length_id, self.length_pwd, self.username, self.passwd)




class ConnectResponse(Message):
    
    code = Code.CONNECT_RESPONSE
    userid : int

    def __init__(self, userid : int):
        self.userid = userid

    @classmethod
    def decode(cls, data: bytes) -> Message:
        (_, userid) = struct.unpack('BQ', data)
        return ConnectResponse(userid)

    def encode(self) -> bytes:
        return struct.pack('BQ', self.code, self.userid)





class UsersRequest(Message):
    
    code = Code.USERS_REQUEST
    userid : int
    nbr_user_request : bytes
    nbr_userid : bytes

    def __init__(self, userid : int, nbr_user_request : bytes, nbr_userid : bytes):
        self.userid = userid
        self.nbr_user_request = nbr_user_request
        for x in range(int(nbr_user_request)):  #test
            nbr_userid = nbr_userid * x

    @classmethod
    def decode(cls, data: bytes) -> Message:
        (_, userid, nbr_user_request, nbr_userid) = struct.unpack('BQBQ', data)
        return UsersRequest(userid, nbr_user_request, nbr_userid)

    def encode(self) -> bytes:
        return struct.pack('BQBQ', self.code, self.userid, self.nbr_user_request, self.nbr_userid)




class UsersResponse(Message):

    code = Code.USERS_RESPONSE    
    userid : int
    nbr_user_request : bytes
    length_id : bytes
    username : bytes
    nbr_userid : bytes

    def __init__(self, username : bytes, length_id : bytes, userid : int, nbr_user_request : bytes, nbr_userid : bytes):
        self.username = username
        self.length_id = bytes(len(username))
        self.userid = userid
        self.nbr_user_request = nbr_user_request
        "self.nbr_userid = nbr_userid* nbr_user_request" #CORRECTION

    @classmethod
    def decode(cls, data: bytes) -> Message:
        (_, userid, nbr_user_request, "nbr_userid", length_id, username) = struct.unpack('BQBQBQBB', data) #CORRECTION
        return UsersResponse(userid, nbr_user_request, "nbr_userid", length_id, username)

    def encode(self) -> bytes:
        return struct.pack('BQBQBQBB', self.code, self.userid, self.nbr_user_request, "self.nbr_userid", self.length_id, self.username) #CORRECTION


