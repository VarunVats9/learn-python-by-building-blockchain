import functools
import hashlib
from collections import OrderedDict
import json
import pickle

from hash_util import hash_string_256, hash_block

MINING_REWARD = 10

blockchain = []
open_transactions = []
owner = 'Varun Vats'
participants = {'Varun Vats'}


def load_data_with_pickle():
    with open('blockchain.txt', mode='rb') as f:
        file_content = pickle.loads(f.read())
        global blockchain
        global open_transactions
        blockchain = file_content['chain']
        open_transactions = file_content['ot']


def save_data_with_pickle():
    with open('blockchain.txt', mode='wb') as f:
        save_data = {
            'chain': blockchain,
            'ot': open_transactions
        }
        f.write(pickle.dumps(save_data))


def load_data():
    """ Loads the data from the file. """
    global blockchain
    global open_transactions
    try:
        with open('blockchain.txt', mode='r') as f:
            file_content = f.readlines()
            blockchain = json.loads(file_content[0][:-1])
            updated_blockchain = []
            for block in blockchain:
                updated_block = {
                    'previous_hash': block['previous_hash'],
                    'index': block['index'],
                    'proof': block['proof'],
                    'transactions': [OrderedDict([('sender', tx['sender']),
                                                  ('recipient',
                                                   tx['recipient']),
                                                  ('amount', tx['amount'])])
                                     for tx in block['transactions']]
                }
                updated_blockchain.append(updated_block)
            blockchain = updated_blockchain
            open_transactions = json.loads(file_content[1])
            updated_open_transactions = []
            for tx in open_transactions:
                updated_tx = OrderedDict([('sender', tx['sender']),
                                          ('recipient', tx['recipient']),
                                          ('amount', tx['amount'])])
                updated_open_transactions.append(updated_tx)
            open_transactions = updated_open_transactions
    except IOError:
        genesis_block = {
            'previous_hash': '',
            'index': 0,
            'transactions': [],
            'proof': 100
        }
        blockchain = [genesis_block]
        open_transactions = []
    finally:
        print('Cleanup!')


load_data()


def save_data():
    """ Saves the data to the file. """
    try:
        with open('blockchain.txt', mode='w') as f:
            f.write(json.dumps(blockchain))
            f.write('\n')
            f.write(json.dumps(open_transactions))
    except IOError:
        print('Serving failed!')


def get_last_blockchain_value():
    """ Returns the last value of the crrent blockchain. """
    if len(blockchain) < 1:
        return None
    return blockchain[-1]


def valid_proof(transactions, last_hash, proof):
    """ Validates the proof of work. """
    guess = (str(transactions) + str(last_hash) + str(proof)).encode()
    guess_hash = hash_string_256(guess)
    # print(guess_hash)
    return guess_hash[0:2] == "00"


def proof_of_work():
    """ Returns the proof (nonce). """
    proof = 0
    last_hashed_block = hash_block(get_last_blockchain_value())
    while not valid_proof(open_transactions, last_hashed_block, proof):
        proof += 1
    return proof


def verify_transaction(transaction):
    """ Verifies the given transaction. """
    return transaction['amount'] <= get_balance(transaction['sender'])


def get_balance(participant):
    """ Returns the balance for the given participant. """
    tx_sender = [[tx['amount'] for tx in block['transactions'] if
                  tx['sender'] == participant] for block in blockchain]
    open_tx_sender = [tx['amount'] for tx in open_transactions if
                      tx['sender'] == participant]
    tx_sender.append(open_tx_sender)
    amount_sent = functools.reduce(lambda tx_sum, tx_amnt:
                                   tx_sum + sum(tx_amnt)
                                   if len(tx_amnt) > 0
                                   else tx_sum + 0, tx_sender, 0)
    tx_recipient = [[tx['amount'] for tx in block['transactions'] if
                     tx['recipient'] == participant] for block in blockchain]
    amount_recipient = functools.reduce(lambda tx_sum, tx_amnt:
                                        tx_sum + sum(tx_amnt)
                                        if len(tx_amnt) > 0
                                        else tx_sum + 0, tx_recipient, 0)
    return amount_recipient - amount_sent


def add_transaction(recipient, sender=owner, amount=1.0):
    """ Append a new value as well as the last blockchain value to the
        blockchain.

    Arguments:
        :transaction_amount: The amount that should be added.
        :last_transaction: The last blockchian transaction (default [1]).
    """
    transaction = OrderedDict([('sender', sender),
                               ('recipient', recipient), ('amount', amount)])
    if verify_transaction(transaction):
        open_transactions.append(transaction)
        participants.add(sender)
        participants.add(recipient)
        save_data()
        return True
    return False


def get_transaction_value():
    """ Returns the input of the user (a new transaction amount) as a
        float. """
    tx_recipient = input('Enter the recipient name: ')
    tx_amount = float(input('Enter the transaction amount: '))
    return tx_recipient, tx_amount


def mine_block():
    """ Mines a new block. """
    last_block = get_last_blockchain_value()
    hashed_block = hash_block(last_block)
    proof = proof_of_work()
    reward_transaction = OrderedDict([('sender', 'MINING'),
                                      ('recipient', owner),
                                      ('amount', MINING_REWARD)])
    copied_transactions = open_transactions[:]
    copied_transactions.append(reward_transaction)
    block = {
        'previous_hash': hashed_block,
        'index': len(blockchain),
        'transactions': copied_transactions,
        'proof': proof
    }
    blockchain.append(block)
    return True


def get_user_choice():
    """ Returns the user choice. """
    return input('Your choice: ')


def print_blockchain_elements():
    """ Prints all the blockchain elements. """
    for block in blockchain:
        print('Outputting block')
        print(block)
    else:
        print('-' * 20)


def verify_chain():
    """ Verifies all the blocks in the blockchain. """
    for (index, block) in enumerate(blockchain):
        if index == 0:
            continue
        if block['previous_hash'] != hash_block(blockchain[index-1]):
            return False
        if not valid_proof(block['transactions'][:-1], block['previous_hash'],
                           block['proof']):
            print('Proof of work is invalid')
            return False
    return True


def verify_transactions():
    """ Verifies all the open transactions. """
    return all([verify_transaction(tx) for tx in open_transactions])


waiting_for_input = True
while waiting_for_input:
    print('Please choose')
    print('1: Add a new transaction value')
    print('2: Output the blockchain blocks')
    print('3: Mine a new block')
    print('4: Print participants')
    print('5: Check transactions validity')
    print('h: Hack the blockchain')
    print('q: Quit')
    user_choice = get_user_choice()
    if user_choice == '1':
        tx_data = get_transaction_value()
        recipient, amount = tx_data
        if add_transaction(recipient, amount=amount):
            print('Added transaction!')
        else:
            print('Transaction failed!')
        print(open_transactions)
    elif user_choice == '2':
        print_blockchain_elements()
    elif user_choice == '3':
        if mine_block():
            open_transactions = []
            save_data()
    elif user_choice == '4':
        print(participants)
    elif user_choice == '5':
        if verify_transactions():
            print('All transactions are valid')
        else:
            print('There are invalid transactions')
    elif user_choice == 'q':
        waiting_for_input = False
    elif user_choice == 'h':
        if (len(blockchain)) >= 1:
            blockchain[0] = {
                'previous_hash': '',
                'index': 0,
                'transactions': [{'sender': 'Chris',
                                  'recipient': 'Max', 'amount': 100.0}]
            }
    else:
        print('Input was invalid, please pick another value!')
    if not verify_chain():
        print_blockchain_elements()
        print('Invalid blockchain!')
        break
    print('Balance of {}: {:6.2f}'.format(owner, get_balance(owner)))
else:
    print('User left!')

print('Done!!')
