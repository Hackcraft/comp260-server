from server import GameState, Player, PlayerPersistence, Dungeon, Vector2, DataTags, DataPacket, Room

from queue import Queue

class Play(GameState):

    def __init__(self, db):
        super().__init__()
        self.db = db
        self.player_persistence = PlayerPersistence(db)
        self.dungeon = Dungeon(db)
        self.output_queue = Queue() # (player, msg)

    def join(self, player: Player):
        super().join(player)
        self.player_persistence.load_data(player)
        self.clear_players_screen(player)
        self.welcome_message(player)
        self.move(player, player.pos)

    def send(self, player, tag, msg="none"):
        self.output_queue.put((player, DataPacket.combine(tag, msg)))

    def welcome_message(self, player: Player):
        msg = "Welcome to the Dungeon!"
        self.send(player, DataTags.WRITE, msg)

    def clear_players_screen(self, player: Player):
        self.send(player, DataTags.CLEAR)


    def leave(self, player: Player):
        super().leave(player)
        room = self.dungeon.room_at_position(player.pos)
        self.send_msg_to_room(room, "%s has left the server" % player.get_name(), [player])

    def update(self, ply: Player, data_packet: str):
        tag, data = DataPacket.separate(data_packet)

        # Only handle forwarded data
        if tag is not DataTags.FORWARD:
            return

        # Remove leading whitespace
        data = data.lstrip()
        # Separate by word
        split = data.split(' ')
        trimmed = [x for x in split if x != '']

        # Get the command and arg
        command = trimmed[0] if 0 < len(trimmed) else ''
        argStr = data[len(command):].lstrip().rstrip()

        if command == 'move' or command == 'go':
            self.command_move(ply, argStr)
        elif command == 'say':
            self.say(ply, argStr)

        # Save their data # TODO don't run after every command
        self.save(ply)

        # Fetch the command


    def move(self, player: Player, pos: Vector2):
        if self.dungeon.is_valid_position(pos):
            old_pos = player.pos
            player.pos = pos
            self.send_room_data(player)

            # Fetch the rooms
            old_room = self.dungeon.room_at_position(old_pos)
            new_room = self.dungeon.room_at_position(pos)

            # Update players in rooms
            if old_pos != pos:
                old_room.leave(player)
                self.send_msg_to_room(old_room, "%s has left the room" % player.get_name(), [player])

            new_room.join(player)

            # Notify everyone in the room that a player has joined
            self.send_msg_to_room(new_room, "%s has joined the room" % player.get_name(), [player])

            # Notify player of the players in the room they have joined
            if len(new_room.players) > 1:
                player_names = ', '.join([ply.get_name() for ply in new_room.players if ply != player])
                self.send(player, DataTags.WRITE, "There are %d people in this room: %s" %
                          (len(new_room.players) - 1, player_names))
        else:
            self.send(player, DataTags.WRITE, "Not a valid direction!")  # TODO - less confusing message if map changes

    def command_move(self, player: Player, msg: str):
        if msg in self.dungeon.NAME_TO_DIRECTION:
            direction = self.dungeon.NAME_TO_DIRECTION[msg]
            self.move(player, player.pos + direction)
        else:
            self.send(player, DataTags.WRITE, "Not a valid direction!")

    def send_room_data(self, player: Player):
        room = self.dungeon.room_at_position(player.pos)
        dirs = self.dungeon.directions_from_room(room)
        data = '%s\n%s\nDirections: %s' % (room.name, room.desc, dirs)
        self.send(player, DataTags.WRITE, data)

    def say(self, player: Player, msg: str):
        room = self.dungeon.room_at_position(player.pos)
        self.send_msg_to_room(room, player.get_name() + ": " + msg)

    def command_say(self, player: Player, msg: str):
        self.say(player, msg)

    def send_msg_to_room(self, room: Room, msg: str, ignore=[]):
        for player in room.players:
            if player not in ignore:
                self.send(player, DataTags.WRITE, msg)

    # Save the current game state
    def save(self, player: Player = None):
        if player is not None:
            self.player_persistence.save_data(player)
        else:
            # Save player data
            for player in self.players:
                self.player_persistence.save_data(player)



