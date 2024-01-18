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
    list_userid : list[int]

    def __init__(self, userid : int, nbr_user_request : bytes, list_userid : list[int]):
        self.userid = userid
        self.nbr_user_request = nbr_user_request
        self.list_userid = list_userid

    @classmethod
    def decode(cls, data: bytes) -> Message:

        first_unpack = struct.calcsize('BQB')
        (_, userid, nbr_user_request) = struct.unpack('BQB', data[:first_unpack])
        size_of_user = struct.calcsize('Q')


        list_of_users_id : list[int] = list()

        for _ in range(nbr_user_request): 
            (temp,_) = struct.unpack('Q', data[first_unpack:first_unpack + size_of_user])
            
            first_unpack += size_of_user
            list_of_users_id.append(temp)

        return UsersRequest(userid, nbr_user_request, list_of_users_id)

    def encode(self) -> bytes:
        request = struct.pack('BQB', self.code, self.userid, self.nbr_user_request)

        for element in self.list_userid:
            request  += struct.pack('Q', element)

        return request




class UsersResponse(Message):

    code = Code.USERS_RESPONSE    
    userid : int
    nbr_user_request : bytes
    list_userid : list[int]
    list_of_users : list[tuple[int, str]]
    

    def __init__(self, userid : int, nbr_user_request : bytes, list_userid : list[int], list_of_users : list[tuple[int, str]]):
        self.userid = userid
        self.nbr_user_request = nbr_user_request
        self.list_userid = list_userid
        self.list_of_users = list_of_users


    @classmethod
    def decode(cls, data: bytes) -> Message:

        first_unpack = struct.calcsize('BQB')
        (_, userid, nbr_user_request) = struct.unpack('BQB', data[:first_unpack])

        size_of_user = struct.calcsize('Q')
        list_of_users_id : list[int] = []

        for _ in range(nbr_user_request):
            (temp,) = struct.unpack('Q', data[first_unpack:first_unpack + size_of_user])
            first_unpack += size_of_user
            list_of_users_id.append(temp)

        size_of_username = struct.calcsize('B')
        list_of_users : list[tuple[int, str]] = []

        for _ in range(nbr_user_request):
            user_id, username_length = struct.unpack('QB', data[first_unpack:first_unpack + size_of_username])
            first_unpack += size_of_username
            username = data[first_unpack:first_unpack + username_length].decode()
            first_unpack += username_length
            list_of_users.append((user_id, username))

        return UsersResponse(userid, nbr_user_request, list_of_users_id, list_of_users)

    def encode(self) -> bytes:
        request = struct.pack('BQB', self.code, self.userid, self.nbr_user_request)

        for user_id in self.list_userid:
            request += struct.pack('Q', user_id)

        for user_id, username in self.list_of_users:
            username_length = len(username)
            request += struct.pack('QB', user_id, username_length)
            request += username.encode()

        return request
    

"""
        first_unpack = struct.calcsize('BQB')
        (_, userid, nbr_user_request) = struct.unpack('BQB', data[:first_unpack])
        size_of_user = struct.calcsize('Q')

        list_of_users_id : list[int] = list()

        for _ in range(nbr_user_request): 
            (temp,_) = struct.unpack('Q', data[first_unpack:first_unpack + size_of_user])
        
            first_unpack += size_of_user
            list_of_users_id.append(temp)
            

        (_, userid, nbr_user_request, "nbr_userid", ) = struct.unpack('BQBQBQBB', data) #CORRECTION
        return UsersResponse(userid, nbr_user_request, "nbr_userid", length_id, username)

    def encode(self) -> bytes:
        #return struct.pack('BQBQBQBB', self.code, self.userid, self.nbr_user_request, "self.nbr_userid", self.length_id, self.username) #CORRECTION
        
        request = struct.pack('BQB', self.code, self.userid, self.nbr_user_request)

        for element in self.list_userid:
            request  += struct.pack('Q', element)

        return request

"""