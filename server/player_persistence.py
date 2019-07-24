import sqlite3
from server import Player, Vector2

class PlayerPersistence:

    PLAYER_TABLE = 'player'

    def __init__(self, db):
        self.db = db
        self.cursor = db.cursor()

        self._set_up_table()

    def _set_up_table(self):
        try:
            self.cursor.execute( # TODO - Remember to check nickname length before saving - varchar(20) limit
                '''CREATE TABLE IF NOT EXISTS %s (
                player_id int primary key not null,
                nickname varchar(20),
                pos_x int not null,
                pos_y int not null)''' % self.PLAYER_TABLE
            )
        except Exception as e:
            print("Failed to create %s table" % self.PLAYER_TABLE)
            print(e)

    def _player_data(self, player_id: int):
        self.cursor.execute('select player_id, nickname, pos_x, pos_y from %s where player_id = ?' %
                            self.PLAYER_TABLE, [player_id])
        rows = self.cursor.fetchall()
        if len(rows) >= 1:
            data = {}
            data['player_id'] = rows[0][0]
            data['nickname'] = rows[0][1]
            data['pos_x'] = rows[0][2]
            data['pos_y'] = rows[0][3]
            return data
        return None

    def load_data(self, player: Player):
        data = self._player_data(player.player_id)

        print(data)

        if data is not None:
            player.nickname = data['nickname']
            player.pos.x = data['pos_x']
            player.pos.y = data['pos_y']


    def save_data(self, player: Player):
        print("Saving data")
        try:
            self.cursor.execute(
                'INSERT OR IGNORE INTO %s (player_id, nickname, pos_x, pos_y) VALUES (?,?,?,?)' % self.PLAYER_TABLE,
                (player.player_id, player.get_name(), player.pos.x, player.pos.y))

            self.cursor.execute('UPDATE %s SET nickname = ?, pos_x = ?, pos_y = ? WHERE player_id = ?' % self.PLAYER_TABLE,
                                (player.get_name(), player.pos.x, player.pos.y, player.player_id))
        except Exception as e:
            print(e)
        else:
            self.db.commit()
