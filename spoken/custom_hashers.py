import hashlib
from django.contrib.auth.hashers import BasePasswordHasher
from django.utils.crypto import constant_time_compare

class LegacyUnsaltedMD5PasswordHasher(BasePasswordHasher):
    """
    Custom hasher to support legacy passwords hashed with UnsaltedMD5PasswordHasher.
    """

    algorithm = "unsalted_md5"

    def salt(self):
        return ""  #  No salt was used in the old hashing scheme

    def encode(self, password, salt=None):
        assert salt in [None, ""], "Unsalted MD5 does not use salt."
        hash_value = hashlib.md5(password.encode()).hexdigest()
        return f"{self.algorithm}${hash_value}"  #  Correct formatting

    def verify(self, password, encoded):
        try:
            algorithm, hashed = encoded.split("$", 1)
            password = hashlib.md5(password.encode()).hexdigest()
        except ValueError:
            hashed = encoded
            password = hashlib.md5((password).encode('utf-8')).hexdigest()
        return constant_time_compare(hashed, password)  #  Secure comparison

    def must_update(self, encoded):
        """Ensures passwords get rehashed to a stronger algorithm after authentication."""
        return True  # Forces rehashing after authentication