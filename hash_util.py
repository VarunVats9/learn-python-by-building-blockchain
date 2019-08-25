import hashlib
import json


def hash_string_256(string):
    """ Returns the hash_256 of the given string. """
    return hashlib.sha256(string).hexdigest()


def hash_block(block):
    """ Returns the hash_256 of the given block. """
    return hash_string_256(json.dumps(block, sort_keys=True).encode())
