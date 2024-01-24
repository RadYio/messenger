import logging

from message import *
from gestionBdd import *

from argparse import ArgumentParser
from threading import current_thread, Thread
from connection import Connection, Server

from gestionBdd import *

the_bdd : Bdd = Bdd.load_bdd_from_disk() # Global variable

def smart_handler(conn: Connection):
    # A smart echo handler
    thread = current_thread()

    user_id_of_the_session : int = -1

    with conn:
        try:
            while True:
                # Receive some data from a connection
                data = conn.recv()
                logging.debug(f'{thread.name} fileno {conn.fileno()}: {repr(data)}')
                
                match Code.decode(data):
                    case Code.MESSAGES_REQUEST:
                        logging.info(f'{thread.name} fileno {conn.fileno()}: MESSAGES_REQUEST')

                        message = MessageRequest.decode(data)
                        all_messages : list[tuple[int, datetime, int, str]] = the_bdd.get_x_message(message.nbrmsg)
                        message_header : list[tuple[int, datetime, int, int]] = list()
                        # Pour tous tous les messages, on ajoute le header
                        for msg in all_messages:
                            message_header.append((msg[0], msg[1], msg[2], len(msg[3])))
                        message2 = MessageResponse(message.userid, message.nbrmsg, message_header, all_messages[0][3])

                        # Envoie de la réponse
                        conn.send(message2.encode())
                    case Code.USERS_REQUEST:
                        logging.info(f'{thread.name} fileno {conn.fileno()}: USER_REQUEST')
                        ...
                        message  = UsersRequest.decode(data)

                    case Code.CONNECT_REQUEST:
                        logging.info(f'{thread.name} fileno {conn.fileno()}: CONNECT_REQUEST')
                        message = ConnectRequest.decode(data)
                        logging.info(f'{thread.name} fileno {conn.fileno()}: message.username = {message.username}')
                        if the_bdd.username_exists(message.username):
                            logging.info(f'{thread.name} fileno {conn.fileno()}: check_connexion')
                            user_id_of_the_session = the_bdd.check_connexion(message.username, message.passwd)
                        else:
                            user_id_of_the_session = the_bdd.add_user(message.username, message.passwd)
                            logging.info(f'{thread.name} fileno {conn.fileno()}: add_user')
                        logging.info(f'{thread.name} fileno {conn.fileno()}: user_id_of_the_session = {user_id_of_the_session}')

                        message2 = ConnectResponse(user_id_of_the_session) 
                        conn.send(message2.encode())

                    case Code.POST_REQUEST:
                        logging.info(f'{thread.name} fileno {conn.fileno()}: POST_REQUEST')
                        message = PostRequest.decode(data)

                        #Check if the userid provided is the same as the one in the session
                        if user_id_of_the_session == message.userid:
                            id_message : int = the_bdd.add_new_message(datetime.now(), message.userid, message.message)

                            # A Corriger on pourrait mettre le threadid à 0 en default et verifier le renvoie de l'user id
                            message2 = PostResponse(message.userid, 0, id_message)
                        else:
                            message2 = PostResponse(message.userid, 0, -1)
                        
                        conn.send(message2.encode())



                    case _:
                        logging.info(f'{thread.name} fileno {conn.fileno()}: UNKNOWN')
                        ...
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

    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO,
                        format='%(asctime)s [%(levelname)s] %(message)s',
                        datefmt='%m-%d-%Y %H:%M:%S')
    serve((args.ip, args.port), args.certfile, args.keyfile)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
