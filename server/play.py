from server import GameState, Player, PlayerPersistence, Dungeon, Vector2, DataTags, DataPacket, Room

from queue import Queue

class Play(GameState):

    def __init__(self, db):
        super().__init__()
        self.db = db
        self.player_persistence = PlayerPersistence(db)
        self.dungeon = Dungeon(db)
        self.output_queue = Queue()  # (player, msg)
        self.kick_queue = Queue()  # (player, reason)

    def join(self, player: Player):
        # Check for duplicate connections
        for ply in self.players:
            if ply.username == player.username:
                self.kick_queue.put((player, "You are already logged on from a different computer!"))
                return

        super().join(player)
        self.player_persistence.load_data(player)
        self.clear_players_screen(player)
        self.welcome_message(player)
        print("Moving player: %s to %s" % (player.get_name(), player.pos))
        self.move(player, player.pos)

    def send(self, player, tag, msg="none"):
        self.output_queue.put((player, DataPacket.combine(tag, msg)))

    def welcome_message(self, player: Player):
        msg = "Welcome to the Dungeon %s!" % player.get_name()
        self.send(player, DataTags.WRITE, msg)

    def clear_players_screen(self, player: Player):
        self.send(player, DataTags.CLEAR)


    def leave(self, player: Player):
        super().leave(player)
        if player.get_name() is not None:
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
            self.save(ply)

        elif command == 'say':
            self.command_say(ply, argStr)

        elif command == 'name':
            self.command_name(ply, argStr)


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
                self.send_msg_to_room(old_room, "%s has left the room" % player.get_true_name(), [player])

            new_room.join(player)

            # Notify everyone in the room that a player has joined
            self.send_msg_to_room(new_room, "%s has joined the room" % player.get_true_name(), [player])

            # Notify player of the players in the room they have joined
            if len(new_room.players) > 1:
                player_names = ', '.join([ply.get_true_name() for ply in new_room.players if ply != player])
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

    def command_name(self, player: Player, name: str):
        if len(name) > 20:
            reason = "Nickname too long! (max 20)"
            self.send(player, DataTags.WRITE, reason)  # TODO change DUPLICATE_LOGIN
        else:
            old_name = player.get_name()
            player.nickname = name
            # Notify others of name change
            self.send_msg_to_room(self.dungeon.room_at_position(player.pos), "%s (%s) has changed their name to %s" %
                                  (old_name, player.username, player.nickname), [player])
            # Notify the player of name change
            self.send(player, DataTags.WRITE, "You have changed your name from %s to %s" %
                      (old_name, player.get_name()))
            self.save(player)


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



