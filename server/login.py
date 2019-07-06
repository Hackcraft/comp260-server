from server.game_state import GameState
import threading
import sqlite3
import hashlib
import uuid
from queue import Queue

class Login(GameState):

    LOGIN_TABLE = "logins"

    def __init__(self, db):
        super().__init__()
        self.database = db
        self.cursor = db.cursor()

        self.verified = []
        self.verified_lock = threading.Lock()

        self.user_names = []
        self.user_names_lock = threading.Lock()

        self.salts = []
        self.salts_lock = threading.Lock()

        self.output_queue = Queue()  # (player_id, msg)

        self._setup_tables()

    def _setup_tables(self):
        try:
            self.cursor.execute(
                '''create table %s (
                username varchar(20),
                salted_password varchar(20),
                salt varchar(20))''' % self.LOGIN_TABLE
            )
        except Exception as e:
            print("Failed to create %s table" % self.LOGIN_TABLE)
            print(e)

    def join(self, player_id):
        super().join(player_id)

    def leave(self, player_id):
        super().leave(player_id)
        # Remove salt
        with self.salts_lock:
            if player_id in self.salts_lock:
                del self.salts_lock[player_id]
        # Remove from verified
        with self.verified_lock:
            if player_id in self.verified:
                self.verified.remove(player_id)
        # Remove selected username
        with self.user_names_lock:
            if player_id in self.user_names:
                del self.user_names[player_id]

    def is_verified(self, player_id):
        with self.verified_lock:
            return player_id in self.verified

    def selected_username(self, player_id):
        # If verified - pass the username which was verified
        if self.is_verified(player_id):
            with self.verified_lock:
                return self.verified[player_id]
        else:
            with self.user_names_lock:
                if player_id in self.user_names:
                    return self.user_names[player_id]

    def update(self, player_id, message):
        # Verified users should't be sending messages here
        with self.verified_lock:
            if player_id in self.verified:
                return

        username = message

        # Set username first
        with self.user_names_lock:
            if player_id not in self.user_names:
                self.user_names[player_id] = username
                # Load the salt for the user if one is found
                if self.username_exists(message):
                    with self.salts_lock:
                        self.salts = self.user_salt(username)
                        self.output_queue.put((player_id, self.salts[player_id]))
                # Or generate a temporary one
                else:
                    with self.salts_lock:
                        self.salts[player_id] = self.generate_salt()
                        self.output_queue.put((player_id, self.salts[player_id]))
                return # Set username - wait for next call for password

        username = self.selected_username(player_id)
        saltedPassword = message

        # Log into existing account
        if self.username_exists(username):
            if self.password_correct(username, saltedPassword):
                with self.verified_lock:
                    self.verified[player_id] = username
            else:
                self.output_queue.put(player_id, "bad password")

        # Create a new account
        else:
            self.create_account(username, saltedPassword, self.salts[player_id])
            with self.verified_lock:
                self.verified[player_id] = username


    def create_account(self, username, salted_password, salt):
        self.cursor.execute(
            'insert into %s(username, salted_password, salt) values(?,?,?)' % self.LOGIN_TABLE,
            (username, salted_password, salt)
        )
        self.database.commit()

    def _user_login_data(self, username):
        self.cursor.execute('select * from %s where username = ?' % self.LOGIN_TABLE, [username])
        rows = self.cursor.fetchall()
        return len(rows) >= 1 and rows[0] or None

    def username_exists(self, username):
        data = self._user_login_data(username)
        return data is not None

    def password_correct(self, username, salted_password):
        data = self._user_login_data(username)
        return data is not None and data['salted_password'] == salted_password or False

    def user_salt(self, username):
        data = self._user_login_data(username)
        return data is not None and data['salt'] or None

    @staticmethod
    def generate_salt(): # https://stackoverflow.com/a/9595108
        return uuid.uuid4().hex

    @staticmethod
    def salt_password(salt, password):
        hashlib.sha512(password.encode() + salt.encode()).hexdigest()



