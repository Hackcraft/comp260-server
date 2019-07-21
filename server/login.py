from server.game_state import GameState
import threading
import sqlite3
import hashlib
import uuid
from queue import Queue

from server.player import Player

class Login(GameState):

    LOGIN_TABLE = "logins"

    def __init__(self, db):
        super().__init__()
        self.database = db
        self.cursor = db.cursor()

        self.output_queue = Queue()  # (player_id, msg)
        self.verified_queue = Queue()

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

    def join(self, player: Player):
        super().join(player)

    def leave(self, player: Player):
        super().leave(player)

    # Update is not thread safe
    def update(self, player: Player, message):
        # Verified users should't be sending messages here
        if player.login_verified:
            return

        username = message

        # TODO check if user is already logged in

        # Set username first
        if player.username is None:
            player.username = username
            # Load the salt for the user if one is found
            if self.username_exists(message):
                player.salt = self.user_salt(username)
                self.output_queue.put((player, player.salt))
            # Or generate a temporary one
            else:
                player.salt = self.generate_salt()
                self.output_queue.put((player, player.salt))
            return # Set username - wait for next call for password

        # Otherwise - try password
        username = player.username
        saltedPassword = message

        # Log into existing account
        if self.username_exists(username):
            if self.password_correct(username, saltedPassword):
                player.login_verified = True
            else:
                self.output_queue.put(player, "bad password - try again!")

        # Create a new account
        else:
            self.create_account(username, saltedPassword, player.salt)
            player.login_verified = True
            self.verified_queue.put(player)

    def create_account(self, username, salted_password, salt):
        self.cursor.execute(
            'insert into %s(username, salted_password, salt) values(?,?,?)' % self.LOGIN_TABLE,
            (username, salted_password, salt)
        )
        self.database.commit()

    def _user_login_data(self, username):
        self.cursor.execute('select * from %s where username = ?' % self.LOGIN_TABLE, [username])
        rows = self.cursor.fetchall()
        if len(rows) >= 1:
            data = {}
            data['username'] = rows[0][0]
            data['salted_password'] = rows[0][1]
            data['salt'] = rows[0][2]
            return data
        return None

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



