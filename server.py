import logging

from message import *
from gestionBdd import *

from argparse import ArgumentParser
from threading import current_thread, Thread
from connection import Connection, Server



def smart_handler(conn: Connection):
    # A smart echo handler
    thread = current_thread()
    with conn:
        try:
            while True:
                # Receive some data from a connection
                data = conn.recv()
                logging.debug(f'{thread.name} fileno {conn.fileno()}: {repr(data)}')
                
                match Code.decode(data):
                    case Code.MESSAGES_REQUEST:
                        logging.info(f'{thread.name} fileno {conn.fileno()}: MESSAGES_REQUEST')
                        message : MessageRequest = MessageRequest.decode(data)

                        #message2 = MessageResponse(1, message.nbrmsg, fesse, 'coucou' + 'fesse')
                        #conn.send(message2.encode())
                    case Code.USERS_REQUEST:
                        logging.info(f'{thread.name} fileno {conn.fileno()}: USER_REQUEST')
                        message : Message = UsersRequest.decode(data)
                    case Code.CONNECT_REQUEST:
                        logging.info(f'{thread.name} fileno {conn.fileno()}: CONNECT_REQUEST')
                        message : Message = ConnectRequest.decode(data)
                    case Code.POST_REQUEST:
                        logging.info(f'{thread.name} fileno {conn.fileno()}: POST_REQUEST')
                        message : Message = PostRequest.decode(data)
                    case _:
                        logging.info(f'{thread.name} fileno {conn.fileno()}: UNKNOWN')
                        conn.send(data)

        except BrokenPipeError:
            logging.info(f'{thread.name} fileno {conn.fileno()} closed the connection')
        except Exception as exn:
            logging.error(f'{thread.name}: {repr(exn)}')

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
                thread = Thread(target=smart_handler, args=(conn,), daemon=True)
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

    list_of_users = [(1, 'Allan', hash512('coucou')), (2, 'Marceau', hash512('coucou2')), (3, 'Matthieu', hash512('coucou3'))]
    
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO,
                        format='%(asctime)s [%(levelname)s] %(message)s',
                        datefmt='%m-%d-%Y %H:%M:%S')
    serve((args.ip, args.port), args.certfile, args.keyfile)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
