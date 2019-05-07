import sys, os
myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../')

from Encryption import Encryption

encrypt = Encryption()

# Get the keys
privateKey = encrypt.GeneratePrivateKey()
publicKey = encrypt.GetPublicKey(privateKey)

# Test message + encrypted test message
myMessage = "This is a very lovely message!"
myEncrypted = encrypt.Encrypt(publicKey, myMessage)

# Encrypted message should not be the same as raw
assert myMessage != myEncrypted

# Decrypt
myDecrypted = encrypt.Decrypt(privateKey, myEncrypted)

# Decrypted should be the same as raw/original
assert myMessage == myDecrypted

print(__file__ + " - pass")
