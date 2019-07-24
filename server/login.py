import threading
import sqlite3
import hashlib
import uuid
import json
from queue import Queue

from server import Player, GameState, DataPacket, LoginTags, DataTags

class Login(GameState):

    LOGIN_TABLE = "logins"

    def __init__(self, db):
        super().__init__()
        self.database = db
        self.cursor = db.cursor()

        self.output_queue = Queue()  # (player, msg)
        self.verified_queue = Queue()

        self._setup_tables()

    def _setup_tables(self):
        try:
            self.cursor.execute(
                '''CREATE TABLE IF NOT EXISTS %s (
                player_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username varchar(20),
                salted_password varchar(20),
                salt varchar(20))''' % self.LOGIN_TABLE
            )
        except Exception as e:
            print("Failed to create %s table" % self.LOGIN_TABLE)
            print(e)

    def join(self, player: Player):
        super().join(player)
        print("Player joined login state")
        self.send(player, LoginTags.ENTER_USERNAME)  # When they join - request username

    def leave(self, player: Player):
        super().leave(player)

    def send(self, player, tag, msg="none"):
        self.output_queue.put((player, DataPacket.combine(tag, msg)))

    # Update is not thread safe
    def update(self, player: Player, data_packet: str):
        # Verified users should't be sending messages here
        if player.login_verified:
            return

        tag, data = DataPacket.separate(data_packet)

        if tag is LoginTags.CHECK_USERNAME:
            self.check_username(player, data)
        elif tag is LoginTags.CHECK_PASSWORD:
            self.check_password(player, data)
        else:
            print("Login | Unidentified tag: %s" % tag)


    def check_username(self, player: Player, username: str):
        # TODO check if user is already logged in
        if len(username) > 20:
            reason = "Username too long! (max 20)"
            self.send(player, DataTags.DUPLICATE_LOGIN, reason) # TODO change DUPLICATE_LOGIN
            self.send(player, LoginTags.ENTER_USERNAME)
            return
        # Set username first
        if player.username is None:
            player.username = username
            # Load user's salt or create one
            if self.username_exists(username):
                player.salt = self.user_salt(username)
            else:
                player.salt = self.generate_salt()
            # Tell user to enter password
            self.send(player, LoginTags.ENTER_PASSWORD, player.salt)

    def check_password(self, player, saltedPassword):
        username = player.username

        # Log into existing account
        if self.username_exists(username):
            if self.password_correct(username, saltedPassword):
                player.login_verified = True
                player.player_id = self._user_login_data(player.username)['player_id']
                self.verified_queue.put(player)
            else:
                self.send(player, LoginTags.BAD_PASSWORD, player.salt)

        # Create a new account
        else:
            self.create_account(username, saltedPassword, player.salt)
            player.login_verified = True
            player.player_id = self._user_login_data(player.username)['player_id']
            self.verified_queue.put(player)

    def create_account(self, username, salted_password, salt):
        try:
            self.cursor.execute(
                'insert into %s(username, salted_password, salt) values(?,?,?)' % self.LOGIN_TABLE,
                (username, salted_password, salt)
            )
        except Exception as e:
            print(e)
        else:
            self.database.commit()

    def _user_login_data(self, username):
        self.cursor.execute('select player_id, username, salted_password, salt from %s where username = ?' %
                            self.LOGIN_TABLE, [username])
        rows = self.cursor.fetchall()
        if len(rows) >= 1:
            data = {}
            data['player_id'] = rows[0][0]
            data['username'] = rows[0][1]
            data['salted_password'] = rows[0][2]
            data['salt'] = rows[0][3]
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



