import hashlib
import json


def hash_string_256(string):
    """ Returns the hash_256 of the given string. """
    return hashlib.sha256(string).hexdigest()


def hash_block(block):
    """ Returns the hash_256 of the given block. """
    hashable_block = block.__dict__.copy()
    print(hashable_block)
    hashable_block['transactions'] = [str(tx.to_ordered_dict) for tx in
                                      hashable_block['transactions']]
    print(hashable_block)
    return hash_string_256(json.dumps(hashable_block, sort_keys=True).encode())
