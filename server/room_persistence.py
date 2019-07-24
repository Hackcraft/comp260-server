import sqlite3
from server import Room

class RoomPersistence:

    ROOM_TABLE = "room"

    def __init__(self, db):
        self.db = db
        self.cursor = db.cursor()

        self._set_up_table()

    def _set_up_table(self):
        try:
            self.cursor.execute(
                '''CREATE TABLE IF NOT EXISTS %s (
                room_id int primary key not null,
                name varchar(30),
                desc varchar(30))''' % self.ROOM_TABLE
            )
        except Exception as e:
            print("Failed to create %s table" % self.ROOM_TABLE)
            print(e)

    def _room_data(self, room_id: int):
        self.cursor.execute('select room_id, name, desc from %s where room_id = ?' % self.ROOM_TABLE,
                            [room_id])
        rows = self.cursor.fetchall()
        if len(rows) >= 1:
            data = {}
            data['room_id'] = rows[0][0]
            data['name'] = rows[0][1]
            data['desc'] = rows[0][2]
            return data
        return None

    def save_data(self, room: Room):
        print("Saving room data")
        try:
            self.cursor.execute(
                'INSERT OR IGNORE INTO %s (room_id, name, desc) VALUES (?,?,?)' % self.ROOM_TABLE,
                (room.room_id, room.name, room.desc))

            self.cursor.execute(
                'UPDATE %s SET name = ?, desc = ? WHERE room_id = ?' % self.ROOM_TABLE,
                (room.name, room.desc, room.room_id))
        except Exception as e:
            print(e)
        else:
            self.db.commit()

    def load_data(self, room: Room):
        data = self._room_data(room.room_id)

        if data is not None:
            room.name = data['name']
            room.desc = data['desc']
