from blockchain import Blockchain
from uuid import uuid4
from utility.verification import Verification


class Node:

    def __init__(self):
        self.id = 'Varun Vats'
        self.blockchain = Blockchain(self.id)

    def listen_to_input(self):
        waiting_for_input = True
        while waiting_for_input:
            print('Please choose')
            print('1: Add a new transaction value')
            print('2: Output the blockchain blocks')
            print('3: Mine a new block')
            print('4: Check transactions validity')
            print('q: Quit')
            user_choice = self.get_user_choice()
            if user_choice == '1':
                tx_data = self.get_transaction_value()
                recipient, amount = tx_data
                if self.blockchain.add_transaction(recipient, self.id,
                                                   amount=amount):
                    print('Added transaction!')
                else:
                    print('Transaction failed!')
                print(self.blockchain.get_open_transactions())
            elif user_choice == '2':
                self.print_blockchain_elements(self.blockchain)
            elif user_choice == '3':
                self.blockchain.mine_block()
            elif user_choice == '4':
                if Verification.verify_transactions(
                        self.blockchain.get_open_transactions(),
                        self.blockchain.get_balance):
                    print('All transactions are valid!!')
                else:
                    print('There are invalid transactions')
            elif user_choice == 'q':
                waiting_for_input = False
            else:
                print('Input was invalid, please pick another value!')
            if not Verification.verify_chain(self.blockchain.get_chain()):
                self.print_blockchain_elements(self.blockchain)
                print('Invalid blockchain!')
                break
            print('Balance of {}: {:6.2f}'.format(
                self.id, self.blockchain.get_balance()))
        else:
            print('User left!')

        print('Done!!')

    def get_user_choice(self):
        """ Returns the user choice. """
        return input('Your choice: ')

    def print_blockchain_elements(self, blockchain):
        """ Prints all the blockchain elements. """
        for block in self.blockchain.get_chain():
            print('Outputting block')
            print(block)
        else:
            print('-' * 20)

    def get_transaction_value(self):
        """ Returns the input of the user (a new transaction amount) as a
            float.
        """
        tx_recipient = input('Enter the recipient name: ')
        tx_amount = float(input('Enter the transaction amount: '))
        return tx_recipient, tx_amount


node = Node()
node.listen_to_input()
