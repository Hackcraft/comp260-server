import socket
import threading
import json
import time

from queue import *
from base64 import *

from shared.encryption_util import EncryptionUtil
import shared.commands as commands

'''
    Handles the connection to the client
'''
class ClientConnection:

    NO_CONNECTION = 0
    CONNECTED = 1
    WAITING_FOR_PUBLIC_KEY = 2
    WAITING_FOR_ENCRYPTION_KEY = 3
    CONNECTED_SECURELY = 4

    PACKET_ID = "HMUD"
    CHAR_TYPE = "ISO-8859-1"

    def __init__(self, socket, index = 0):
        self.incoming_queue = Queue()
        self.client_index = index

        # Create a public encryption key for use with the client
        self.encrypt_util = EncryptionUtil()
        self.server_private_key = self.encrypt_util.generatePrivateKey()
        self.server_public_key = self.encrypt_util.getPublicKey(self.server_private_key)
        self.client_public_key = None
        self.encryption_key = None
        self.last_sequence_id = 0

        # Start listening to responses from the client
        self.socket = socket
        self.state = self.WAITING_FOR_PUBLIC_KEY
        self.state_lock = threading.Lock()
        self.current_receive_thread = threading.Thread(target=self._receive_thread)
        self.current_receive_thread.start()

        self._send(self.encrypt_util.exportPublicKey(self.server_public_key), False)

    def _receive_thread(self):
        print("Server receiveThread running")

        while self.state >= self.CONNECTED:
            if self._socket_contains_valid_packet_id():
                data = self._socket_get_data()
                if data is not None:

                    if self.state == self.WAITING_FOR_PUBLIC_KEY:

                        try:
                            # Save the public key from the server
                            self.client_public_key = self.encrypt_util.importPublicKey(data)
                        except:
                            print("Error importing the public key sent by the client")
                            return
                        else:
                            with self.state_lock:
                                self.state = self.WAITING_FOR_ENCRYPTION_KEY

                    elif self.state == self.WAITING_FOR_ENCRYPTION_KEY:

                        try:
                            # Save the public key from the server
                            self.encryption_key = self.encrypt_util.decryptKey(self.server_private_key, data)
                        except:
                            print("Error importing the aes key sent by the client")
                            return
                        else:
                            with self.state_lock:
                                self.state = self.CONNECTED_SECURELY

                            print("Connected to client %d securely!" % self.client_index)


                    elif self.state == self.CONNECTED_SECURELY:
                        arr = json.loads(data)

                        if 'si' in arr and self._is_valid_sequence_id(arr['si']):
                            try:
                                iv = arr['iv'] #self.encrypt_util.decryptKey(self.server_private_key, arr['iv'])
                                ct = arr['ct'] #self.encrypt_util.decrypt(self.encryption_key, iv, arr['ct'])

                                msg_encoded = self.encrypt_util.decrypt(self.encryption_key, iv, ct)
                                msg = msg_encoded.decode(self.CHAR_TYPE)
                            except:
                                print("Error decrypting message from client")
                                pass
                            else:
                                self.incoming_queue.put(msg)

                    else:
                        print("Unexpected state passed to receiver, state: " + str(self.state))

    '''
        Send to client with the option of encryption
    '''
    def send(self, data, encrypt=True):
        if self.state == self.CONNECTED_SECURELY:
            self._send(data, encrypt)

    def _send(self, data, encrypt=True):
        if not isinstance(data, str):
            raise ValueError("send only accepts strings!")

        if encrypt:
            iv, ct = self.encrypt_util.encrypt(self.encryption_key, data)
            result = json.dumps({'iv': iv, 'ct': ct, 'si': str(1)})
            data = result

        self._send_header()
        self._send_data(data.encode(self.CHAR_TYPE))

    def _send_header(self):
        try:
            self.socket.send(self.PACKET_ID.encode(self.CHAR_TYPE))
        except socket.error:
            self._lost_client()

    def _send_data(self, data_bytes):
        try:
            self.socket.send(len(data_bytes).to_bytes(2, byteorder="little"))
            self.socket.send(data_bytes)
        except socket.error:
            self._lost_client()

    def _socket_contains_valid_packet_id(self):
        try:
            id_encoded = self.socket.recv(4)
            id = id_encoded.decode(self.CHAR_TYPE)
        except socket.error:
            self._lost_client()
            return False
        else:
            return id == self.PACKET_ID

    def _socket_get_data(self):
        try:
            size = int.from_bytes(self.socket.recv(2), "little")
            data = self.socket.recv(size)
        except socket.error:
            self._lost_client()
            return None
        else:
            return data.decode(self.CHAR_TYPE)

    def _is_valid_sequence_id(self, sequence_id):
        safe_id = False
        try:
            si = int(sequence_id)
            safe_id = si > self.last_sequence_id
        except ValueError as e:
            print("Unable to read sequence_id")

        return safe_id


    def is_connected(self):
        return self.state is not self.NO_CONNECTION

    def _lost_client(self):
        with self.state_lock:
            self.state = self.NO_CONNECTION
        print("Lost client")

    def close(self):
        self.state = self.NO_CONNECTION

        if self.socket is not None:
            self.socket.close()
            self.socket = None

        if self.current_receive_thread is not None:
            self.current_receive_thread.join()

        print("Closed client socket for client: " + str(self.client_index))



'''
    Handles the connection/binding to the ip, port
    
    Observer for connects and disconnects?
'''
class NetConnection:

    NO_CONNECTION = 0

    '''
           Binds to an ip and port
           Throws error if the connection cannot be made
       '''

    def __init__(self, ip="127.0.0.1", port=8222):
        self.clients = {}
        self.clients_lock = threading.Lock()
        self.disconnects = Queue()
        self.connects = Queue()
        self.accepting_clients = True
        self.message_queue = Queue()

        self.client_index = 0
        self.client_index_lock = threading.Lock()

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            self.server_socket.bind((ip, port))
        except socket.error:
            raise ValueError("Can't start server, is another instance running?: %s:%d" % (ip, port))

        self.server_socket.listen(5)

        self._current_accept_thread = threading.Thread(target=self._accept_thread)
        self._current_accept_thread.start()

        self._current__client_message_group_thread = threading.Thread(target=self._client_message_group_thread)
        self._current__client_message_group_thread.start()

    def _accept_thread(self):
        print("Accept thread running!")

        while self.accepting_clients:
            try:
                (clientSocket, address) = self.server_socket.accept()
            except:
                pass

            # New index
            with self.client_index_lock:
                self.client_index += 1
                client_id = self.client_index

            # New connection
            try:
                client = ClientConnection(clientSocket, client_id)
            except:
                print("Failed to accept client")
            else:
                # Add to table
                with self.clients_lock:
                    self.clients[client_id] = client
                self.connects.put(client_id)

    def _client_message_group_thread(self):
        print("Putting client messages into one central queue")

        while self.accepting_clients:
            time.sleep(0.1)
            try:
                for client in self.clients:
                    if self.clients[client].is_connected():
                        while self.clients[client].incoming_queue.qsize() > 0:
                            self.message_queue.put((client, self.clients[client].incoming_queue.get()))
                    else:
                        self.disconnects.put(client)
                        self.clients[client].close()
                        with self.clients_lock:
                            del self.clients[client]

                        print("Lost client")  # TODO HANDLE LOST or move?
            except:
                pass

    def close(self):
        self.accepting_clients = False

        if self.server_socket is not None:
            self.server_socket.close()
            self.server_socket = None

        if self._current_accept_thread is not None:
            self._current_accept_thread.join()

        with self.clients_lock:
            for client_id in self.clients:
                self.clients[client_id].close()

        print("Closed server socket")

    def send(self, client_id, data):
        try:
            self.clients[client_id].send(data)
        except:
            pass


    def recv(self):
        if self.message_queue.qsize() > 0:
            (client, msg) = self.message_queue.get()
            return (client, msg)


    # Check for disconnected clients

