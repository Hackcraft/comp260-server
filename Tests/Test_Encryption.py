import sys, os
myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../')

from Encryption import Encryption

encrypt = Encryption()

#
# Generate keys
#

# Get the keys
privateKey = encrypt.GeneratePrivateKey()
publicKey = encrypt.GetPublicKey(privateKey)

#
# Messages
#

# Test message + encrypted test message
myMessage = "This is a very lovely message!"
myEncrypted = encrypt.Encrypt(publicKey, myMessage)

# Encrypted message should not be the same as raw
assert myMessage != myEncrypted

# Decrypt
myDecrypted = encrypt.Decrypt(privateKey, myEncrypted)

# Decrypted should be the same as raw/original
assert myMessage == myDecrypted

#
# Verify pem conversion
#

pemPublic = encrypt.ExportKey(publicKey)
pemToKey = encrypt.ImportKey(pemPublic)
assert encrypt.ImportKey("Not a valid key") == None

pemEncrypted = encrypt.Encrypt(pemToKey, myMessage)
pemDecrypted = encrypt.Decrypt(privateKey, pemEncrypted)

assert myMessage == myDecrypted == pemDecrypted

print(__file__ + " - pass")
