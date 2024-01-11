from __future__ import annotations

from types import TracebackType

from socket import socket


class Connection:

    def __init__(self, socket: socket) -> None:
        ...

    def __enter__(self) -> Connection:
        return self

    def __exit__(self, exc_type: type[Exception] | None, exc_value: Exception | None, exc_tb: TracebackType | None):
        self.close()

    def send(self, data: bytes):
        ...

    def recv(self) -> bytes:
        ...

    def fileno(self) -> int:
        ...

    def close(self) -> None:
        ...


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
