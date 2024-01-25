from __future__ import annotations
import struct

from types import TracebackType

from socket import socket, SOCK_STREAM
import ssl
import time


class Connection:

    my_socket: socket

    def __init__(self, socket: socket) -> None:
        self.my_socket = socket

    def __enter__(self) -> Connection:
        """Return the connection. Context manager method."""
        return self

    def __exit__(self, exc_type: type[Exception] | None, exc_value: Exception | None, exc_tb: TracebackType | None):
        """Close the socket of the connection. Context manager method. See `socket.close`."""
        self.close()

    def send(self, data: bytes):
        """Send data to the socket of the connection. See `socket.send`.
            the send method will prefix a 4-bytes big-endian header indicating the length of the subsequent data.
        Args:
            data (bytes): Data to send.

        """
        size_of_payload_in_header = struct.pack("!L", len(data))
        self.my_socket.sendall(size_of_payload_in_header+data)

    def recv(self) -> bytes:
        """Receive data from the socket of the connection. See `socket.recv`.
        
        Returns:
            bytes: Data received.

        """
        t = self.my_socket.recv(4)
        while len(t) < 4:
            t += self.my_socket.recv(4-len(t))
        print(t)
        time.sleep(10)
        (size_of_payload_in_header, ) = struct.unpack('!L', t)
        data : bytes = self.my_socket.recv(size_of_payload_in_header)
        print(f"Received {len(data)} bytes")
        return data

    def fileno(self) -> int:
        """Return the file descriptor of the socket of the connection. See `socket.fileno`.
        
        Returns:
            int: File descriptor of the socket of the connection.

        """
        return self.my_socket.fileno()

    def close(self) -> None:
        """Close the socket of the connection. See `socket.close`.
        
        """
        self.my_socket.close()


class Listener:

    my_socket: socket
    context: ssl.SSLContext
    list_of_accepted: list[tuple[str, int]]

    def __init__(self, socket: socket) -> None:
        self.my_socket = socket
        self.list_of_accepted = []
        self.context = ssl.create_default_context()

    def __enter__(self) -> Listener:
        return self

    def __exit__(self, exc_type: type[Exception] | None, exc_value: Exception | None, exc_tb: TracebackType | None):
        self.close()

    def accept(self) -> Connection:
        """Accept a connection. See `socket.accept`.
        
        Add the address of the accepted connection to the list of accepted connections.

        Returns:
        
            Connection: Connection accepted.
            
        """
        
        socket_accepted, address = self.my_socket.accept()
        self.list_of_accepted.append(address)
        return Connection(socket_accepted)

    def last_accepted(self) -> tuple[str, int] | None:
        return self.list_of_accepted[-1] if self.list_of_accepted else None

    def fileno(self) -> int:
        return self.my_socket.fileno()

    def close(self) -> None:
        self.my_socket.close()


class Server:

    def __init__(self, certfile: str, keyfile: str | None = None, password: str | None = None) -> None:
        
        self.context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        self.context.load_cert_chain(certfile=certfile, keyfile=keyfile, password=password)

    def listen(self, address: tuple[str, int]) -> Listener:
        """Listen for connections made to the socket of the server. See `socket.bind` and `socket.listen`."""
        
        new_socket = self.context.wrap_socket(socket(type=SOCK_STREAM),
                                                server_side=True # server side
                                                )
        new_socket.bind(address)
        new_socket.listen()

        return Listener(new_socket)


class Client:

    def __init__(self) -> None:
        
        self.context = ssl.create_default_context()
        self.context.check_hostname = False  # Disable hostname verification
        self.context.verify_mode = ssl.CERT_NONE  # Disable certificate verification

    def connect(self, address: tuple[str, int]) -> Connection:

        
        new_socket = self.context.wrap_socket(socket(type=SOCK_STREAM),
                                                server_side=False, # client side
                                                server_hostname=address[0]
                                                )
        new_socket.connect(address)
        return Connection(new_socket)
