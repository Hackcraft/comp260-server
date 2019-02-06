import socket
import time

from Dungeon import Dungeon

if __name__ == '__main__':
    dungeon = Dungeon()

    mySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    mySocket.bind(("127.0.0.1", 8222))
    mySocket.listen(5)

    client = mySocket.accept()

    client[0].send((dungeon.CurrentRoom().Description() + "\n" +
                    dungeon.CurrentRoom().DirectionsParser()).encode())

    while True: # time.sleep(0.5)
        #print(self.dungeon.CurrentRoom().Description())
       # print(self.dungeon.CurrentRoom().DirectionsParser())

        data = client[0].recv(4096)
        input_str = data.decode("utf-8")

        user_input = input_str.split(' ')

        user_input = [x for x in user_input if x != '']

        if user_input[0].lower() == 'help':
            client[0].send("do help".encode())
        else:
            if user_input[0].lower() == 'go':
                direction = dungeon.PhraseToDirection(user_input[1].lower())
                if dungeon.CurrentRoom().IsValidDirection(direction):
                    dungeon.MovePlayer(direction)
                    client[0].send((dungeon.CurrentRoom().Description() + "\n" +
                                 dungeon.CurrentRoom().DirectionsParser()).encode())
                else:
                    client[0].send("\nERROR Press any key to continue".encode())
            else:
                client[0].send("\nERROR Press any key to continue".encode())
