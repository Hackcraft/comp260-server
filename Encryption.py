from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa

'''
    A wrapper encryption class

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
            public_exponent=self.PUBLIC_EXPONENT,
            key_size=self.KEY_SIZE,
            backend=default_backend()
        )
        return privateKey

    def GetPublicKey(self, privateKey):
        return privateKey.public_key()

    def Encrypt(self, publicKey, message):
        cipherText = publicKey.encrypt(
            message.encode(),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return cipherText

    def Decrypt(self, privateKey, cipherText):
        plainText = privateKey.decrypt(
            cipherText,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return plainText.decode(self.CHAR_TYPE)

