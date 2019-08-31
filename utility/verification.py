from utility.hash_util import hash_string_256, hash_block
from wallet import Wallet


class Verification:

    @classmethod
    def verify_transactions(cls, open_transactions, get_balance):
        """ Verifies all the open transactions. """
        return all([cls.verify_transaction(tx, get_balance, False)
                    for tx in open_transactions])

    @classmethod
    def verify_chain(cls, blockchain):
        """ Verifies all the blocks in the blockchain. """
        for (index, block) in enumerate(blockchain):
            if index == 0:
                continue
            if block.previous_hash != hash_block(blockchain[index-1]):
                return False
            if not cls.valid_proof(block.transactions[:-1],
                                   block.previous_hash,
                                   block.proof):
                print('Proof of work is invalid')
                return False
        return True

    @staticmethod
    def verify_transaction(transaction, get_balance, sender=None,
                           check_funds=True):
        """ Verifies the given transaction. """
        if check_funds:
            return (transaction.amount <= get_balance(transaction.sender) and
                    Wallet.verify_transaction(transaction))
        else:
            return Wallet.verify_transaction(transaction)

    @staticmethod
    def valid_proof(transactions, last_hash, proof):
        """ Validates the proof of work. """
        guess = (str([tx.to_ordered_dict() for tx in transactions]
                     ) + str(last_hash) + str(proof)).encode()
        guess_hash = hash_string_256(guess)
        # print(guess_hash)
        return guess_hash[0:2] == '00'
