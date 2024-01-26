from __future__ import annotations

import curses
import curses.ascii
import getpass
import traceback

from argparse import ArgumentParser
from collections import deque
from datetime import datetime
from queue import Queue, Empty
from threading import Thread

from connection import Client, Connection
from message import *


exceptions: list[Exception] = []


def get_message_from_server_and_show_them(conn: Connection, mon_id: int, thread_id: int, dict_of_user_id: dict[int, str], last_message_timestamp: dict[int, float], outqueue: Queue[list[message[str]]], nb_message: int = 64) -> None:
    # DEBUT DE LA DEMANDE DE MESSAGE
    message = MessageRequest(mon_id, thread_id, nb_message)
    conn.send(message.encode())

    receive_message = conn.recv()
    receive_message_decode: MessageResponse = MessageResponse.decode(receive_message)

    userid_temp: list[int] = list()

    # verification de la connaisance dans le dict
    for mes in receive_message_decode.message_header:
        if mes[2] not in dict_of_user_id and mes[2] not in userid_temp:
            userid_temp.append(mes[2])

    # si un user pas connu alors, userrequest, sinon go a la suite
    user = UsersRequest(mon_id, len(userid_temp), userid_temp)
    conn.send(user.encode())

    receive_user = conn.recv()
    receive_user_decode: UsersResponse = UsersResponse.decode(receive_user)
    for users in receive_user_decode.list_of_users:
        if users[0] not in dict_of_user_id:
            dict_of_user_id[users[0]] = users[1]

    # si un user pas connu alors, userrequest, sinon go a la suite
    for mes in receive_message_decode.message_header:
        message_timestamp = datetime.fromtimestamp(mes[1])
        last_known_timestamp = last_message_timestamp.get(mes[2], datetime.min).timestamp()

        # Check if the message is newer than the last known message for the user
        if message_timestamp.timestamp() > last_known_timestamp:
            outqueue.put([(mes[0], message_timestamp, mes[2], mes[4])])
            last_message_timestamp[mes[2]] = message_timestamp.timestamp()


def smart_handler(inqueue: Queue[str], outqueue: Queue[list[message[str]]], address: tuple[str, int], username : str, password : str, userid_dict : dict[int,str]):
    _counter = 0
    threadid_temp : int = 0
    
    try:
        with Client().connect(address) as conn:
            mon_id : int
            connect = ConnectRequest(0, username, password)
            conn.send(connect.encode())

            receive_connect = conn.recv()
            receive_connect_decode : ConnectResponse = ConnectResponse.decode(receive_connect)
            mon_id = receive_connect_decode.userid
            userid_dict[mon_id]=username
            # FIN DE CONNEXION

            # DEBUT DE LA DEMANDE DE MESSAGE
            get_message_from_server_and_show_them(conn, mon_id, threadid_temp, userid_dict, outqueue)
            
            while True : 
                # recuperer depuis la Queue les messages, les envoyer, et attendre la réponse pour verification et si bonne reponse
                # afficher dans le chat via outqueue 
                message = MessageRequest(mon_id, threadid_temp, 4)
                conn.send(message.encode())

                try:
                    message = inqueue.get(timeout=2)
                    post = PostRequest(mon_id, threadid_temp, len(message), message)
                    conn.send(post.encode())

                    receive_post = conn.recv()
                    receive_post_decode : PostResponse = PostResponse.decode(receive_post)

                    outqueue.put([(receive_post_decode.messageid, datetime.now(), receive_post_decode.userid,message)]) 
                except Empty:
                    get_message_from_server_and_show_them(conn, mon_id, threadid_temp, userid_dict, outqueue, 10)
 
            
    except Exception as exn:
        exceptions.append(exn)   

#while True:
       #message = inqueue.get()
       #conn.send(message.encode())
        #message = conn.recv().decode()
        #counter += 1
        #outqueue.put([(counter, datetime.now(), 1, message)])


def dummy_handler(inqueue: Queue[str], outqueue: Queue[list[message[str]]], address: tuple[str, int]):
    counter = 0
    try:
        with Client().connect(address) as conn:
            while True:
                message = inqueue.get()
                conn.send(message.encode())
                message = conn.recv().decode()
                counter += 1
                outqueue.put([(counter, datetime.now(), 1, message)])
    except Exception as exn:
        exceptions.append(exn)


def print_message(window: curses.window, usernames: dict[int, str], message: message[str]):
    (_, date, uid, text) = message
    # Negative user IDs represent error messages
    if uid < 0:
        window.addstr(f"\n{date.isoformat(sep=' ', timespec='seconds')} ERROR: ",
                      curses.A_BOLD | curses.color_pair(1) | curses.A_REVERSE)
        window.addstr(text, curses.color_pair(1) | curses.A_REVERSE)

    # The null user ID is reserved for the server
    elif uid == 0:
        window.addstr(f"\n{date.isoformat(sep=' ', timespec='seconds')} SERVER: ",
                      curses.A_BOLD | curses.color_pair(0) | curses.A_REVERSE)
        window.addstr(text, curses.color_pair(0) | curses.A_REVERSE)

    # Positive user IDs represent regular users whose names are stored in 'usernames'
    else:
        user = usernames[uid] if uid in usernames else f"UNKNOWN {uid}"
        window.addstr(f"\n{date.isoformat(sep=' ', timespec='seconds')} {user}: ",
                      curses.A_BOLD | curses.color_pair(hash(user) % 7))
        window.addstr(text)


def reset_input_window(window: curses.window, str: str | None = None):
    window.erase()
    if str:
        window.addstr(str)
    window.noutrefresh()


def reset_output_window(window: curses.window, usernames: dict[int, str], msgs: deque[message[str]] | None = None):
    y, _ = window.getmaxyx()
    window.erase()
    window.move(y - 1, 0)
    if msgs:
        for msg in msgs:
            print_message(window, usernames, msg)
    window.noutrefresh()


def split_window(window: curses.window, line: int) -> tuple[curses.window, curses.window, curses.window]:
    if line < 2:
        raise ValueError

    curses.update_lines_cols()
    top = window.subwin(curses.LINES - line, curses.COLS, 0, 0)
    top.scrollok(True)

    mid = window.subwin(1, curses.COLS, curses.LINES - line, 0)
    mid.hline(curses.ACS_HLINE, curses.COLS)
    mid.noutrefresh()

    bot = window.subwin(curses.LINES - line + 1, 0)
    bot.scrollok(True)
    bot.timeout(100)  # 0.1 seconds, determine refresh rate

    return (top, mid, bot)


def main(window: curses.window, address: tuple[str, int], username: str, password: str):
    ERASECHAR: int = int.from_bytes(curses.erasechar(), byteorder='big')

    curses.echo()
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_BLUE, curses.COLOR_BLACK)
    curses.init_pair(5, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
    curses.init_pair(6, curses.COLOR_CYAN, curses.COLOR_BLACK)

    # Initialize messages handling thread
    inqueue: Queue[str] = Queue()
    outqueue: Queue[list[message[str]]] = Queue()
    usernames: dict[int, str] = {}

    thread = Thread(target=smart_handler, args=(inqueue, outqueue, address, username, password, usernames), daemon=True)
    thread.start()

    # Initialize terminal windows
    top, _, bot = split_window(window, 4)
    reset_output_window(top, usernames)
    reset_input_window(bot)

    # https://docs.python.org/3/library/collections.html#collections.deque
    history: deque[message[str]] = deque(maxlen=256)
    line: bytearray = bytearray()

    # Main event loop
    while (thread.is_alive() or not outqueue.empty()):
        curses.doupdate()

        try:
            # Check for new messages
            msgs = outqueue.get_nowait()
            for msg in msgs:
                # Print new messages
                print_message(top, usernames, msg)
            # Update the history, then refresh the window
            history.extend(msgs)
            top.noutrefresh()
            reset_input_window(bot, line.decode())

        except Empty:  # Empty mailbox ˙◠˙
            pass

        match bot.getch():

            # Newline
            case  curses.ascii.NL:
                if line:
                    inqueue.put(line.decode())
                    line.clear()
                    reset_input_window(bot)

            # Backspace or Delete
            case curses.ascii.BS | curses.ascii.DEL:
                if line:
                    line.pop()
                reset_input_window(bot, line.decode())

            # Other characters
            case c:
                # ¯\_(ツ)_/¯
                if c == ERASECHAR:
                    if line:
                        line.pop()
                    reset_input_window(bot)
                # Timeout event
                elif c < 0:
                    pass
                # Other events, including terminal resize events, and non-ASCII characters
                elif c > 255:
                    top, _, bot = split_window(window, 4)
                    reset_output_window(top, usernames, history)
                    reset_input_window(bot, line.decode())
                # ASCII characters
                else:
                    if len(line) < 65536:
                        line.append(c)
                    else:
                        reset_input_window(bot, line.decode())


if __name__ == '__main__':
    parser = ArgumentParser(prog='Client')
    parser.add_argument('-u', '--username', metavar='USER', required=True, help="User name")
    parser.add_argument('ip', metavar='IP', help='IP address to connect')
    parser.add_argument('port', metavar='PORT', type=int, help='port number to connect')

    args = parser.parse_args()
    password = getpass.getpass()
    try:
        curses.wrapper(main, (args.ip, args.port), args.username, password)
        for exn in exceptions:
            traceback.print_exception(exn)
    except KeyboardInterrupt:
        pass
