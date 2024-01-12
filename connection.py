from __future__ import annotations

from types import TracebackType

from socket import socket


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
        
        Args:
            data (bytes): Data to send.

        """
        nb_bytes : int = self.my_socket.send(data)
        print(f"Sent {nb_bytes} bytes")

    def recv(self) -> bytes:
        """Receive data from the socket of the connection. See `socket.recv`.
        
        Returns:
            bytes: Data received.

        """
        data : bytes = self.my_socket.recv(1024)
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
    list_of_accepted: list[tuple[str, int]]

    def __init__(self, socket: socket) -> None:
        self.my_socket = socket
        self.list_of_accepted = []

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
        ...

    def listen(self, address: tuple[str, int]) -> Listener:
        """Listen for connections made to the socket of the server. See `socket.bind` and `socket.listen`."""
        
        new_socket = socket()
        new_socket.bind(address)
        new_socket.listen()
        return Listener(new_socket)


class Client:

    def __init__(self) -> None:
        ...

    def connect(self, address: tuple[str, int]) -> Connection:
        new_socket = socket()
        new_socket.connect(address)
        return Connection(new_socket)
