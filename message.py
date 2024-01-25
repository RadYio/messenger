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
    def decode(cls, data: bytes) -> MessageRequest :
        (_, userid, threadid, nbrmsg) = struct.unpack('!BQQB', data)
        return MessageRequest(userid, threadid, nbrmsg)
          
    def encode(self) -> bytes:
        return struct.pack('!BQQB', self.code, self.userid, self.threadid, self.nbrmsg)

class MessageResponse(Message):

    code = Code.MESSAGES_RESPONSE
    nbrmsg : int
    message_header : list[tuple[int, float, int, int, str]]

    def __init__(self, userid : int, nbrmsg : int, message_header : list[tuple[int, float, int, int, str]]):

        self.userid = userid
        self.nbrmsg = nbrmsg
        self.message_header = message_header


    @classmethod    
    def decode(cls, data: bytes) -> MessageResponse :
        message_header : list[tuple[int, float, int, int]] = list()
        size_start = struct.calcsize('!BQB')
        (_, userid, nbrmsg) = struct.unpack('!BQB', data[:size_start])
        size_header = struct.calcsize('!QdQH')

        for i in range(0, nbrmsg):
            (messageid, datepub, userauthorid, lenghtmsg) = struct.unpack('!QdQH', data[size_start:size_start+size_header])
            message_header.append((messageid, datepub, userauthorid, lenghtmsg))
            size_start += size_header

        message : list[tuple[int, float, int, int, str]] = list()
        for i in range(0, nbrmsg):
            message.append((message_header[i][0], message_header[i][1], message_header[i][2], message_header[i][3], data[size_start:size_start+message_header[i][3]].decode()))
            size_start += message_header[i][3]
        return MessageResponse(userid, nbrmsg, message)

    def encode(self) -> bytes :
            msgresponse = struct.pack('!BQB', self.code, self.userid, self.nbrmsg)
            for elem in self.message_header:
                header = struct.pack('!QdQH', elem[0], elem[1], elem[2], elem[3])
                msgresponse += header

            for elem in self.message_header:  
                msgresponse += elem[4].encode()
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
        #

    @classmethod 
    def decode(cls, data: bytes) -> PostRequest :
        size_header = struct.calcsize('!BQQH')
        (_, userid, threadid, lenghtmsg) = struct.unpack('!BQQH', data[0:size_header])
        message = data[size_header:].decode()
        return PostRequest(userid, threadid, lenghtmsg, message)       
    def encode(self) -> bytes :
        request = struct.pack('!BQQH', self.code, self.userid, self.threadid, self.lenghtmsg)
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
    def decode(cls, data: bytes) -> PostResponse :
        (_, userid, threadid, messageid) = struct.unpack('!BQQQ', data)
        return PostResponse(userid, threadid, messageid)   
    def encode(self) -> bytes:
        return struct.pack('!BQQQ', self.code, self.userid, self.threadid, self.messageid)




class ConnectRequest(Message):

    code = Code.CONNECT_REQUEST
    userid : int
    username : str
    passwd : str

    def __init__(self, userid : int, username : str, passwd : str,):
         self.userid = userid
         self.username = username
         self.passwd = passwd
         

    @classmethod
    def decode(cls, data: bytes) -> ConnectRequest :
        size_of_header : int = struct.calcsize('!BQBB')
        (_, userid, length_username, length_pwd) = struct.unpack('!BQBB', data[:size_of_header])

        print('data:  -- len(data): ', data, len(data))
        print('size_of_header:', size_of_header)
        print('length_username:', length_username)
        print('length_pwd:', length_pwd)

        
        
        # On se place à la fin de l'entête pour récupérer les données puis on se deplace de la taille de l'username pour recuperer l'username en bytes
        username = data[size_of_header:size_of_header+length_username].decode()

        # On se place à la fin de l'en-tête et de l'username, puis on se deplace de la taille du password pour recuperer le password en bytes
        passwd = data[size_of_header+length_username:size_of_header+length_username+length_pwd].decode()

        print ('username: ', username)
        print ('passwd : ', passwd)
        return ConnectRequest(userid, username, passwd)

    def encode(self) -> bytes:
        start_of_header = struct.pack('!BQBB', self.code, self.userid, len(self.username), len(self.passwd))
        username = self.username.encode()
        passwd = self.passwd.encode()
        return start_of_header + username + passwd




class ConnectResponse(Message):
    
    code = Code.CONNECT_RESPONSE
    userid : int

    def __init__(self, userid : int):
        self.userid = userid

    @classmethod
    def decode(cls, data: bytes) -> ConnectResponse :
        (_, userid) = struct.unpack('!BQ', data)
        return ConnectResponse(userid)

    def encode(self) -> bytes:
        return struct.pack('!BQ', self.code, self.userid)





class UsersRequest(Message):
    
    code = Code.USERS_REQUEST
    userid : int
    nbr_user_request : int
    list_userid : list[int]

    def __init__(self, userid : int, nbr_user_request : int, list_userid : list[int]):
        self.userid = userid
        self.nbr_user_request = nbr_user_request
        self.list_userid = list_userid

    @classmethod
    def decode(cls, data: bytes) -> UsersRequest :

        first_unpack = struct.calcsize('!BQB')
        (_, userid, nbr_user_request) = struct.unpack('!BQB', data[:first_unpack])
        size_of_user = struct.calcsize('!Q')

        list_of_users_id : list[int] = list()

        for _ in range(nbr_user_request): 
            (temp,) = struct.unpack('!Q', data[first_unpack:first_unpack + size_of_user])
            
            first_unpack += size_of_user
            list_of_users_id.append(temp)

        return UsersRequest(userid, nbr_user_request, list_of_users_id)

    def encode(self) -> bytes:
        request = struct.pack('!BQB', self.code, self.userid, self.nbr_user_request)

        for element in self.list_userid:
            request  += struct.pack('!Q', element)

        return request




class UsersResponse(Message):

    code = Code.USERS_RESPONSE    
    userid : int
    nbr_user_request : int
    list_of_users : list[tuple[int, str]]
    

    def __init__(self, userid : int, nbr_user_request : int, list_of_users : list[tuple[int, str]]):
        self.userid = userid
        self.nbr_user_request = nbr_user_request
        self.list_of_users = list_of_users


    @classmethod
    def decode(cls, data: bytes) -> UsersResponse :

        first_unpack = struct.calcsize('!BQB')
        (_, userid, nbr_user_request) = struct.unpack('!BQB', data[:first_unpack])
        list_temp : list[tuple[int, int]] = list()

        size_of_response = struct.calcsize('!QB') # user: Q + size of username: B

        for _ in range(nbr_user_request):
            (id_ask, length_ask) = struct.unpack('!QB', data[first_unpack:first_unpack + size_of_response])
            first_unpack += size_of_response
            list_temp.append((id_ask, length_ask))

        list_of_needed_users : list[tuple[int, str]] = list()

        for element in list_temp:
            (id_ask, length_ask) = element
            username = data[first_unpack:first_unpack + length_ask].decode()
            first_unpack += length_ask
            list_of_needed_users.append((id_ask, username))


        return UsersResponse(userid, nbr_user_request, list_of_needed_users)

    def encode(self) -> bytes:
        request = struct.pack('!BQB', self.code, self.userid, self.nbr_user_request)

        for user in self.list_of_users:
            request += struct.pack('!QB', user[0], len(user[1]))

        for user in self.list_of_users:
            request += user[1].encode()

        return request
    

