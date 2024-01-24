from __future__ import annotations
import hashlib
import pickle
import hmac
import os.path
import threading as th # Pour les threads (et les verrous)
from datetime import datetime


NAME_OF_BDD_FILE = "bdd.pickle"

def hash512(password : str) -> str:
    h = hashlib.new('sha512')
    h.update(password.encode())
    return h.hexdigest()

  

class Bdd():
    
    list_of_users : list[tuple[int, str, str]]
    list_of_messages : list[tuple[int, datetime, int, str]]
    lock_user : th.Lock
    lock_message : th.Lock

    def __init__(self):
        self.list_of_users = []
        self.list_of_messages = []
        self.lock_user = th.Lock() 
        self.lock_message = th.Lock() 

    def __getstate__(self):
        state = self.__dict__.copy()
        del state['lock_user']  # Exclude the lock_user from pickling, it can't be pickled
        del state['lock_message']  # Exclude the lock_message from pickling
        return state

    def __setstate__(self, state : dict[str, list[tuple[int, str, str]]]):
        self.__dict__.update(state)
        self.lock_user = th.Lock()  # Recreate the lock_user when unpickling
        self.lock_message = th.Lock() # Recreate the lock_user when unpickling

    @staticmethod
    def load_bdd_from_disk(secret_key: bytes = b'password') -> Bdd:
        """Load the database from the disk. The database is signed with HMAC-SHA512.
            Also check if the file exists. If not, create a new database from scratch.
        
        Args:
            secret_key (bytes, optional): Secret key used to sign the database. Defaults to b'password'.
            
        Returns:
            Bdd: The database.
            
        Raises:
            ValueError: If the signature is invalid.
                
        """

        # Check if the file exists and create a new database from scratch if not
        if not os.path.isfile(NAME_OF_BDD_FILE):
            print("Bdd created from scratch")
            return Bdd()

        # Load the database from the disk and check the signature to avoid tampering héhé
        with open(NAME_OF_BDD_FILE, 'rb') as f:
            signature = f.read(64)
            data = f.read()
        if not hmac.compare_digest(signature, hmac.new(secret_key, data, hashlib.sha512).digest()):
            raise ValueError('Invalid signature')
        
        test : Bdd = pickle.loads(data)

        print(test.list_of_users)
        return pickle.loads(data)
    

    def save_bdd_on_disk(self, secret_key: bytes = b'password') -> bytes:
        with self.lock_user:
            data = pickle.dumps(self)
            signature = hmac.new(secret_key, data, hashlib.sha512).digest()
            with open(NAME_OF_BDD_FILE, 'wb') as f:
                f.write(signature)
                f.write(data)
            return signature

    
    def username_exists(self, username : str) -> bool:
        """Check if the username is already used. ⚠️⚠️We are not using the lock here⚠️⚠️

        Args:
            username (str): username to check.

        Returns:
            bool: True if the username is already used, False otherwise.
        """
        
        for user in self.list_of_users:
            if user[1] == username:
                return True
        return False
    
    def add_user(self, username : str, password : str) -> int:
        """Add a user to the database. ⚠️⚠️We are using the lock here⚠️⚠️

        Args:
            username (str): username of the user.
            password (str): password of the user.

        Returns:
            int: id of the user added.
        """
        with self.lock_user:
            if self.username_exists(username):
                raise ValueError("Username already exists")
            
            id = len(self.list_of_users) + 1
            self.list_of_users.append((id, username, hash512(password)))
            return id
    
    def check_connexion(self, username : str, password : str) -> int:
        """Check if the username and password are correct. ⚠️⚠️We are using the lock here⚠️⚠️

        Args:
            username (str): username of the user.
            password (str): password of the user.

        Returns:
            int: id of the user if the username and password are correct, -1 otherwise. 
            (We could also raise an exception)
        """
        with self.lock_user:
            for user in self.list_of_users:
                if user[1] == username and user[2] == hash512(password):
                    return user[0]
            return -1
        
    def add_new_message(self, datetime_of_message : datetime, author_id: int, text_message: str) -> int:
        ...
        with self.lock_message:
            id_of_message : int = len(self.list_of_messages) + 1

            # Construct a new tuple before adding. We should do -- self.list_of_messages.append((id_of_message, datetime_of_message, author_id, text_message))
            new_tuple : tuple[int, datetime, int, str] = (id_of_message, datetime_of_message, author_id, text_message)
            self.list_of_messages.append(new_tuple)
            return id_of_message


    def get_x_message(self, nb_of_message_request : int = 20) -> list[tuple[int, datetime, int, str]]:
        ...
        with self.lock_message:
            nb_message_in_list : int = len(self.list_of_messages)
            nb_message : int = nb_message_in_list if nb_of_message_request > nb_message_in_list else nb_of_message_request
            return self.list_of_messages[nb_message_in_list - nb_message:]
        

    



labdd : Bdd = Bdd.load_bdd_from_disk()

# try with so many threads that some of them are killed by the OS before they can finish
#for i in range(10000):
    #th.Thread(target=labdd.add_user, args=(f"Userr{i}", f"Password{i}")).start()

labdd.add_new_message(datetime.now(), 1, "Message 1")
labdd.add_new_message(datetime.now(), 1, "Message 2")
labdd.add_new_message(datetime.now(), 1, "Message 3")

print(labdd.get_x_message())
labdd.save_bdd_on_disk()