import unittest
from shared import EncryptionUtil

class TestEncryptionUtil(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.encrypt_util = EncryptionUtil()

    def test_string_encryption(self):
        original_string = "This is the test string"
        encrypt_key = self.encrypt_util.generateEncryptionKey()

        iv, ct = self.encrypt_util.encrypt(encrypt_key, original_string.encode("utf-8"))
        assert ct != original_string
        decrypted_string = self.encrypt_util.decrypt(encrypt_key, iv, ct)
        assert original_string == decrypted_string.decode("utf-8")
