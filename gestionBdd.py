
import hashlib
import pickle
import hmac
import os.path
import threading as th # Pour les threads (et les verrous)

def hash512(password : str) -> str:
    h = hashlib.new('sha512')
    h.update(password.encode())
    return h.hexdigest()

  

class Bdd():
    
    list_of_users : list[tuple[int, str, str]]
    list_of_messages : list[int]
    user_lock : th.Lock

    def __init__(self):
        self.list_of_users = []
        self.list_of_messages = []
        self.user_lock = th.Lock()

    def __reduce__(self):
        # Exclude the lock from pickling
        return (self.__class__, (self.list_of_users, self.list_of_messages))


    def save_bdd_on_disk(self, secret_key: bytes = b'password') -> bytes:
        with self.user_lock:
            data = pickle.dumps(self)
            signature = hmac.new(secret_key, data, hashlib.sha512).digest()
            with open('bdd.pickle', 'wb') as f:
                f.write(signature)
                f.write(data)

            
            return signature

    @staticmethod
    def load_bdd_from_disk(secret_key: bytes = b'password') -> "Bdd":
        """Load the database from the disk. The database is signed with HMAC-SHA512.
            Also check if the file exists. If not, create a new database from scratch.
        
        Args:
            secret_key (bytes, optional): Secret key used to sign the database. Defaults to b'password'.
            
        Returns:
            Bdd: The database.
            
        Raises:
            ValueError: If the signature is invalid.
                
        """
        if not os.path.isfile('bdd.pickle'):
            print("Bdd created from scratch")
            return Bdd()

        with open('bdd.pickle', 'rb') as f:
            signature = f.read(64)
            data = f.read()
        if not hmac.compare_digest(signature, hmac.new(secret_key, data, hashlib.sha512).digest()):
            raise ValueError('Invalid signature')
        
        return pickle.loads(data)
    
    
    def add_user(self, username : str, password : str) -> int:
        """Add a user to the database. 

        Args:
            username (str): username of the user.
            password (str): password of the user.

        Returns:
            int: id of the user added.
        """
        with self.user_lock:
            id = len(self.list_of_users) + 1
            self.list_of_users.append((id, username, hash512(password)))
            return id
    
    def check_connexion(self, username : str, password : str) -> int:
        """Check if the username and password are correct.

        Args:
            username (str): username of the user.
            password (str): password of the user.

        Returns:
            int: id of the user if the username and password are correct, -1 otherwise. 
            (We could also raise an exception)
        """
        with self.user_lock:
            for user in self.list_of_users:
                if user[1] == username and user[2] == hash512(password):
                    return user[0]
            return -1
            


labdd : Bdd = Bdd.load_bdd_from_disk()

# try with so many threads that some of them are killed by the OS before they can finish
for i in range(300):
    th.Thread(target=labdd.add_user, args=(f"User{i}", f"Password{i}")).start()

labdd.save_bdd_on_disk()