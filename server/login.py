from game_state import GameState
import threading
import sqlite3
import hashlib

class Login(GameState):

    def __init__(self, db):
        super().__init__()
        self.db = db
        self.cursor = db.cursor()

        self.verified = []
        self.verified_lock = threading.Lock()

        self.user_names = []
        self.user_names_lock = threading.Lock()

        self.salts = []
        self.salts_lock = threading.Lock()

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
                # Or generate a temporary one
                else:
                    with self.salts_lock:
                        self.salts[player_id] = self.generate_salt()
                # TODO Send salt to user
                return # Set username - wait for next call for password

        username = self.selected_username(player_id)
        saltedPassword = message

        # Log into existing account
        if self.username_exists(username):
            if self.password_correct(username, saltedPassword):
                with self.verified_lock:
                    self.verified[player_id] = username

        # Create a new account
        else:
            self.create_account(username, saltedPassword, self.salts[player_id])
            with self.verified_lock:
                self.verified[player_id] = username


    def create_account(self, username, saltedPassword, salt):
        pass # TODO sql

    def username_exists(self, username):
        return True # TODO implinent sql call

    def password_correct(self, username, saltedPassword):
        return True # TODO impliment SQL call

    def user_salt(self, username):
        return "" # TODO impliment sql call

    def generate_salt(self):
        return "" # TODO impliment salt



