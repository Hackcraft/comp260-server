from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import load_pem_public_key
import base64

'''
    A wrapper encryption class for cryptography

    Referenced https://cryptography.io/en/latest/hazmat/primitives/asymmetric/rsa
'''


class Encryption:
    PUBLIC_EXPONENT = 65537
    KEY_SIZE = 2048
    CHAR_TYPE = "utf-8"

    def __init__(self):
        pass

    def GeneratePrivateKey(self):
        privateKey = rsa.generate_private_key(
            public_exponent = self.PUBLIC_EXPONENT,
            key_size = self.KEY_SIZE,
            backend = default_backend()
        )
        return privateKey

    def GetPublicKey(self, privateKey):
        return privateKey.public_key()

    def Encrypt(self, publicKey, message):
        cipherText = publicKey.encrypt(
            bytes(message, self.CHAR_TYPE),
            padding.OAEP(
                mgf = padding.MGF1(algorithm = hashes.SHA256()),
                algorithm = hashes.SHA256(),
                label = None
            )
        )
        return message #cipherText

    def Decrypt(self, privateKey, cipherText):
        plainText = privateKey.decrypt(
            cipherText,
            padding.OAEP(
                mgf = padding.MGF1(algorithm = hashes.SHA256()),
                algorithm = hashes.SHA256(),
                label = None
            )
        )
        return cipherText #plainText.decode(self.CHAR_TYPE)

    def ImportKey(self, data):
        try:
            key = load_pem_public_key(data.encode(self.CHAR_TYPE), backend = default_backend())
        except ValueError as error:
            print(error)
            return None
        else:
            if isinstance(key, rsa.RSAPublicKey):
                return key

    def ExportKey(self, publicKey):
        pem = publicKey.public_bytes(
            encoding = serialization.Encoding.PEM,
            format = serialization.PublicFormat.SubjectPublicKeyInfo
        )
        return pem.decode(self.CHAR_TYPE)

