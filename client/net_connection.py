import socket
import threading
import json

from queue import *
from base64 import *

from shared.encryption_util import EncryptionUtil


'''
    Creates a connection to the server
    
    Throws an exception when a new instance is created which cannot connect to the given server
'''
class NetConnection:

    NO_CONNECTION = 0
    CONNECTING = 1
    CONNECTED = 2
    WAITING_FOR_PUBLIC_KEY = 3
    WAITING_FOR_ENCRYPTION_KEY = 4
    CONNECTED_SECURELY = 5

    PACKET_ID = "HMUD"
    CHAR_TYPE = "ISO-8859-1"

    '''
        Creates a connection to a server
        Throws error if the connection cannot be made
    '''
    def __init__(self, ip="127.0.0.1", port=8222):
        self.incoming_queue = Queue()

        # Create an encryption key for use with the server
        self.encrypt_util = EncryptionUtil()
        self.encryption_key = self.encrypt_util.generateEncryptionKey()
        self.server_public_key = None
        self.client_private_key = self.encrypt_util.generatePrivateKey()
        self.client_public_key = self.encrypt_util.getPublicKey(self.client_private_key)

        # Establish a connection to the server
        self.state = self.CONNECTING
        self.state_lock = threading.Lock()
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.connect((ip, port))
        except Exception as e:
            self.server_socket.close()
            raise ValueError('Could not connect to socket: %s:%d' % (ip, port))

        # Start listening to responses from the server
        self.state = self.WAITING_FOR_PUBLIC_KEY
        self.current_receive_thread = threading.Thread(target=self._receive_thread)
        self.current_receive_thread.start()

    def _receive_thread(self):
        print("Client receiveThread running")

        while self.state >= self.CONNECTED:
            if self._socket_contains_valid_packet_id():
                data = self._socket_get_data()
                if data is not None:

                    # Ready to receive encryption key (public key)
                    if self.state == self.WAITING_FOR_PUBLIC_KEY:
                        try:
                            # Save the public key from the server
                            self.server_public_key = self.encrypt_util.importPublicKey(data)
                        except:
                            print("Error importing the public key sent by the server")
                            self.close()
                            return
                        else:
                            # Send our public key
                            key_data = self.encrypt_util.exportPublicKey(self.client_public_key)
                            self.send(key_data, False)

                            # Send our aes key encrypted with server's public key
                            aes_data = self.encrypt_util.encryptKey(self.server_public_key, self.encryption_key)
                            self.send(aes_data.decode(self.CHAR_TYPE), False)

                            # Future connections should now all be encrypted
                            with self.state_lock:
                                self.state = self.CONNECTED_SECURELY

                            print("Connected to server securely!")

                    # Ready to process messages
                    elif self.state == self.CONNECTED_SECURELY:
                        arr = json.loads(data)

                        try:
                            msg_encoded = self.encrypt_util.decrypt(self.encryption_key, arr['iv'], arr["ct"])
                            msg = msg_encoded.decode(self.CHAR_TYPE)
                        except Exception as e:
                            print(e)
                            print("Error decrypting message from server")
                        else:
                            self.incoming_queue.put(msg)

                    else:
                        print("Unexpected state passed to receiver, state: " + str(self.state))




    def _socket_contains_valid_packet_id(self):
        try:
            id_encoded = self.server_socket.recv(4)
            id = id_encoded.decode(self.CHAR_TYPE)
        except socket.error:
            print("Server lost")
            self.close()
            return False
        else:
            return id == self.PACKET_ID

    def _socket_get_data(self):
        try:
            size = int.from_bytes(self.server_socket.recv(2), "little")
            data = self.server_socket.recv(size)
        except socket.error:
            print("Server lost")
            self.close()
            return None
        else:
            return data.decode(self.CHAR_TYPE)


    def close(self):
        with self.state_lock:
            self.state = self.NO_CONNECTION

        if self.server_socket is not None:
            self.server_socket.close()

        self.server_socket = None

        ''' Function is sometimes called in the current thread
            Therefore causing a runtime error
            The thread show stop by itself anyway because of the state being changed
        '''
        #if self.current_receive_thread is not None:
        #    self.current_receive_thread.join()


    '''
        Send to server with the option of encryption
            With encryption - data is expected to be in a string
            Without encryption - data is expected to already be in bytes
    '''
    def send(self, data, encrypt=True):
        if not isinstance(data, str):
            raise ValueError("send only accepts strings!")

        if encrypt:
            iv, ct = self.encrypt_util.encrypt(self.encryption_key, data.encode(self.CHAR_TYPE))
            result = json.dumps({'iv': iv, 'ct': ct, 'si': str(1)})
            data = result

        self._send_header()
        self._send_data(data.encode(self.CHAR_TYPE))

    def _send_header(self):
        try:
            print(self.PACKET_ID.encode(self.CHAR_TYPE))
            self.server_socket.send(self.PACKET_ID.encode(self.CHAR_TYPE))
        except socket.error:
            pass  # TODO _lost_server

    def _send_data(self, data_bytes):
        try:
            self.server_socket.send(len(data_bytes).to_bytes(2, byteorder="little"))
            self.server_socket.send(data_bytes)
        except socket.error:
            pass  # TODO _lost_server

    def is_connected(self):
        return self.state is not self.NO_CONNECTION


