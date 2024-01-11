import logging

from argparse import ArgumentParser
from threading import current_thread, Thread
from connection import Connection, Server


def dummy_handler(conn: Connection):
    # A dummy echo handler
    thread = current_thread()
    with conn:
        try:
            while True:
                # Receive some data from a connection
                data = conn.recv()
                logging.debug(f'{thread.name} fileno {conn.fileno()}: {repr(data)}')
                # Send the data back to the connection
                conn.send(data)
        except Exception as exn:
            logging.error(f'{thread.name}: {repr(exn)}')


def serve(address: tuple[str, int], certfile: str, keyfile: str | None = None):
    # Start a new server listening to 'address'
    with Server(certfile, keyfile, None).listen(address) as listener:
        while True:
            try:
                # Accept a new incoming connection
                conn = listener.accept()
                logging.info(f'Connection accepted from {listener.last_accepted()} on fileno {conn.fileno()}')
                # Start a new thread handling the connection
                thread = Thread(target=dummy_handler, args=(conn,), daemon=True)
                thread.start()
                logging.info(f'{thread.name} started with fileno {conn.fileno()}')
            except Exception as exn:
                logging.error(exn)


def main():
    parser = ArgumentParser(prog='Listener')
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument("ip", metavar='IP', help='IP address to listen')
    parser.add_argument("port", metavar='PORT', type=int, help='port number to listen')
    parser.add_argument("--certfile", required=True, help='path to certificate in PEM format')
    parser.add_argument("--keyfile",  required=True, help='path to the private key')

    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO,
                        format='%(asctime)s [%(levelname)s] %(message)s',
                        datefmt='%m-%d-%Y %H:%M:%S')
    serve((args.ip, args.port), args.certfile, args.keyfile)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
