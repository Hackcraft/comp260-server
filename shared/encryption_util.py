import json
from base64 import *

# cryptography
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import load_pem_public_key

# pycryptodome
from Crypto.Cipher import AES
from Crypto.Util.Padding import *
from Crypto.Random import *

'''
    A wrapper encryption class for cryptography
    Referenced https://cryptography.io/en/latest/hazmat/primitives/asymmetric/rsa

    And AES encryption
'''


class EncryptionUtil:
    PUBLIC_EXPONENT = 65537
    RSA_KEY_SIZE = 2048
    KEY_SIZE = 16
    CHAR_TYPE = "utf-8"

    def __init__(self):
        pass

    def generatePrivateKey(self):
        privateKey = rsa.generate_private_key(
            public_exponent=self.PUBLIC_EXPONENT,
            key_size=self.RSA_KEY_SIZE,
            backend=default_backend()
        )
        return privateKey

    def generateEncryptionKey(self):
        return get_random_bytes(16)

    '''
        Encrypts bytes with a key
    '''
    def encrypt(self, key, data):
        if not isinstance(data, bytes):
            raise TypeError("Only accepts bytes")

        cipher = AES.new(key, AES.MODE_CBC)
        ct_bytes = cipher.encrypt(pad(data, AES.block_size))

        iv = b64encode(cipher.iv).decode(self.CHAR_TYPE)
        ct = b64encode(ct_bytes).decode(self.CHAR_TYPE)

        return iv, ct

    '''
        Decrypts bytes with a key
    '''
    def decrypt(self, key, iv, ct):
        iv = b64decode(iv)
        ct = b64decode(ct)

        cipher = AES.new(key, AES.MODE_CBC, iv)
        pt = unpad(cipher.decrypt(ct), AES.block_size)

        return pt

    def getPublicKey(self, privateKey):
        return privateKey.public_key()

    def encryptKey(self, publicKey, message):
        cipherText = publicKey.encrypt(
            message,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return b64encode(cipherText)

    def decryptKey(self, privateKey, cipher64):
        cipherText = b64decode(cipher64)

        plainText = privateKey.decrypt(
            cipherText,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return plainText

    def importPublicKey(self, data):
        try:
            key = load_pem_public_key(data.encode(self.CHAR_TYPE), backend=default_backend())
        except ValueError as error:
            print(error)
            return None
        else:
            if isinstance(key, rsa.RSAPublicKey):
                return key

    def exportPublicKey(self, publicKey):
        pem = publicKey.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        return pem.decode(self.CHAR_TYPE)
