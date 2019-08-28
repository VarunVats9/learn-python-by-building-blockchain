import functools
import hashlib
import json
import pickle

from utility.hash_util import hash_block
from block import Block
from transaction import Transaction
from utility.verification import Verification
from wallet import Wallet

MINING_REWARD = 10


class Blockchain:

    def __init__(self, hosting_node_id):
        genesis_block = Block(0, '', [], 100, 0)
        self.__chain = [genesis_block]
        self.__open_transactions = []
        self.load_data()
        self.hosting_node = hosting_node_id

    def get_chain(self):
        return self.__chain[:]

    def get_open_transactions(self):
        return self.__open_transactions[:]

    def load_data(self):
        """ Loads the data from the file. """
        try:
            with open('blockchain.txt', mode='r') as f:
                file_content = f.readlines()
                blockchain = json.loads(file_content[0][:-1])
                updated_blockchain = []
                for block in blockchain:
                    converted_tx = [Transaction(tx['sender'], tx['recipient'],
                                                tx['signature'],
                                                tx['amount'])
                                    for tx in block['transactions']]
                    updated_block = Block(
                        block['index'], block['previous_hash'], converted_tx,
                        block['proof'], block['timestamp'])
                    updated_blockchain.append(updated_block)
                self.__chain = updated_blockchain
                open_transactions = json.loads(file_content[1])
                updated_open_transactions = []
                for tx in open_transactions:
                    updated_tx = Transaction(
                        tx['sender'], tx['recipient'], tx['signature'],
                        tx['amount'])
                    updated_open_transactions.append(updated_tx)
                self.__open_transactions = updated_open_transactions
        except (IOError, IndexError):
            print('Handled Exception ...')
        finally:
            print('Cleanup!')

    def save_data(self):
        """ Saves the data to the file. """
        try:
            with open('blockchain.txt', mode='w') as f:
                saveable_chain = [block.__dict__ for block in
                                  [Block(block_el.index,
                                         block_el.previous_hash,
                                         [tx.__dict__ for tx in
                                          block_el.transactions],
                                         block_el.proof, block_el.timestamp)
                                   for block_el in self.__chain]]
                f.write(json.dumps(saveable_chain))
                f.write('\n')
                saveable_tx = [tx.__dict__ for tx in self.__open_transactions]
                f.write(json.dumps(saveable_tx))
        except IOError:
            print('Serving failed!')

    def get_last_blockchain(self):
        """ Returns the last value of the crrent blockchain. """
        if len(self.__chain) < 1:
            return None
        return self.__chain[-1]

    def proof_of_work(self):
        """ Returns the proof (nonce). """
        proof = 0
        last_hashed_block = hash_block(self.get_last_blockchain())
        while not Verification.valid_proof(self.__open_transactions,
                                           last_hashed_block, proof):
            proof += 1
        return proof

    def get_balance(self):
        """ Returns the balance for the given participant. """
        if self.hosting_node is None:
            return None
        participant = self.hosting_node
        tx_sender = [[tx.amount for tx in block.transactions if
                      tx.sender == participant] for block in self.__chain]
        open_tx_sender = [tx.amount for tx in self.__open_transactions if
                          tx.sender == participant]
        tx_sender.append(open_tx_sender)
        amount_sent = functools.reduce(lambda tx_sum, tx_amnt:
                                       tx_sum + sum(tx_amnt)
                                       if len(tx_amnt) > 0
                                       else tx_sum + 0, tx_sender, 0)
        tx_recipient = [[tx.amount for tx in block.transactions if
                         tx.recipient == participant]
                        for block in self.__chain]
        amount_recipient = functools.reduce(lambda tx_sum, tx_amnt:
                                            tx_sum + sum(tx_amnt)
                                            if len(tx_amnt) > 0
                                            else tx_sum + 0, tx_recipient, 0)
        return amount_recipient - amount_sent

    def add_transaction(self, recipient, sender, signature, amount=1.0):
        """ Append a new value as well as the last blockchain value to the
            blockchain.

        Arguments:
            :transaction_amount: The amount that should be added.
            :last_transaction: The last blockchian transaction (default [1]).
        """
        if self.hosting_node is None:
            return False
        transaction = Transaction(sender, recipient, signature, amount)
        if Verification.verify_transaction(transaction, self.get_balance):
            self.__open_transactions.append(transaction)
            self.save_data()
            return True
        return False

    def mine_block(self):
        """ Mines a new block. """
        if self.hosting_node is None:
            return None
        last_block = self.__chain[-1]
        hashed_block = hash_block(last_block)
        proof = self.proof_of_work()
        reward_transaction = Transaction('MINING', self.hosting_node, '',
                                         MINING_REWARD)
        copied_transactions = self.__open_transactions[:]
        for tx in copied_transactions:
            if not Wallet.verify_transaction(tx):
                return None
        copied_transactions.append(reward_transaction)
        block = Block(len(self.__chain), hashed_block,
                      copied_transactions, proof)
        self.__chain.append(block)
        self.__open_transactions = []
        self.save_data()
        return block
