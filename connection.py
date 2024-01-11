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

    def __init__(self, socket: socket) -> None:
        ...

    def __enter__(self) -> Listener:
        return self

    def __exit__(self, exc_type: type[Exception] | None, exc_value: Exception | None, exc_tb: TracebackType | None):
        self.close()

    def accept(self) -> Connection:
        ...

    def last_accepted(self) -> tuple[str, int] | None:
        ...

    def fileno(self) -> int:
        ...

    def close(self) -> None:
        ...


class Server:

    def __init__(self, certfile: str, keyfile: str | None = None, password: str | None = None) -> None:
        ...

    def listen(self, address: tuple[str, int]) -> Listener:
        ...


class Client:

    def __init__(self) -> None:
        ...

    def connect(self, address: tuple[str, int]) -> Connection:
        ...
