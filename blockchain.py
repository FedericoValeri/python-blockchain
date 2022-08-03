"""Import reduce list function"""
from functools import reduce
import json

from hash_util import hash_block
from block import Block
from transaction import Transaction
from verification import Verification

# Global variables
MINING_REWARD = 10
BLOCKCHAIN = []
OPEN_TRANSACTIONS = []
OWNER = 'Federico'


def load_data():
    """Initialize blockchain + open transactions data from a file."""
    global BLOCKCHAIN
    global OPEN_TRANSACTIONS
    try:
        with open('blockchain.txt', mode='r') as file:
            # file_content = pickle.loads(file.read())
            file_content = file.readlines()
            # BLOCKCHAIN = file_content['chain']
            # OPEN_TRANSACTIONS = file_content['ot']
            # Read the blockchain line without the '\n' special character
            BLOCKCHAIN = json.loads(file_content[0][:-1])
            updated_blockchain = []
            for block in BLOCKCHAIN:
                coverted_tx = [Transaction(
                    tx['sender'], tx['recipient'], tx['amount']) for tx in block['transactions']]
                updated_block = Block(
                    block['index'], block['previous_hash'], coverted_tx, block['proof'], block['timestamp'])
                updated_blockchain.append(updated_block)
            BLOCKCHAIN = updated_blockchain
            OPEN_TRANSACTIONS = json.loads(file_content[1])
            updated_transactions = []
            for tx in OPEN_TRANSACTIONS:
                updated_transaction = Transaction(
                    tx['sender'], tx['recipient'], tx['amount'])
                updated_transactions.append(updated_transaction)
            OPEN_TRANSACTIONS = updated_transactions
    except (IOError, IndexError):
        genesis_block = Block(0, '', [], 100, 0)
        BLOCKCHAIN = [genesis_block]
        OPEN_TRANSACTIONS = []
        print('File not found!')
    finally:
        print('Cleanup!')


load_data()


def save_data():
    """Save blockchain + open transactions snapshot to a file."""
    try:
        with open('blockchain.txt', mode='w') as file:
            saveable_chain = [block.__dict__ for block in [Block(block_el.index, block_el.previous_hash, [
                                                                 tx.__dict__ for tx in block_el.transactions], block_el.proof, block_el.timestamp) for block_el in BLOCKCHAIN]]
            file.write(json.dumps(saveable_chain))
            file.write('\n')
            saveable_tx = [tx.__dict__ for tx in OPEN_TRANSACTIONS]
            file.write(json.dumps(saveable_tx))
            # save_data = {
            #     'chain': blockchain,
            #     'ot': OPEN_TRANSACTIONS
            # }
            # file.write(pickle.dumps(save_data))
    except IOError:
        print('Saving failed!')


def proof_of_work():
    """Generate a proof of work for the open transactions, the hash of the
    previous block and a random number (which is guessed until it fits)."""
    last_block = BLOCKCHAIN[-1]
    last_hash = hash_block(last_block)
    nonce = 0
    verifier = Verification()
    while not verifier.valid_proof(OPEN_TRANSACTIONS, last_hash, nonce):
        nonce += 1
    return nonce


def get_balance(participant):
    """Calculate and return the balance for a participant.

    Arguments:
        :participant: The person for whom to calculate the balance.
    """
    # Nested list comprehension
    tx_sender = [[tx.amount for tx in block.transactions if tx.sender == participant]
                 for block in BLOCKCHAIN]
    open_tx_sender = [tx.amount
                      for tx in OPEN_TRANSACTIONS if tx.sender == participant]
    tx_sender.append(open_tx_sender)
    # Reducing list
    amount_sent = reduce(
        lambda tx_sum, tx_amt: tx_sum + sum(tx_amt) if len(tx_amt) > 0 else tx_sum + 0, tx_sender, 0)
    tx_recipient = [[tx.amount for tx in block.transactions if tx.recipient == participant]
                    for block in BLOCKCHAIN]
    # Reducing list
    amount_received = reduce(
        lambda tx_sum, tx_amt: tx_sum + sum(tx_amt) if len(tx_amt) > 0 else tx_sum + 0, tx_recipient, 0)
    return amount_received - amount_sent


def get_last_blockchain_value():
    """ Returns the last value of the current blockchain. """
    # if blockchain is empty
    if len(BLOCKCHAIN) < 1:
        return None
    return BLOCKCHAIN[-1]


def add_transaction(recipient, sender=OWNER, amount=1.0):
    """ Append a new value as well as the last blockchain value to the blockchain.

    Arguments:
        :sender: The sender of the coins.
        :recipient: The recipient of the coins.
        :amount: The amount of coins sent with the transaction (default = 1.0)
    """
    # Unordered simple dictionary
    # transaction = {
    #     'sender': sender,
    #     'recipient': recipient,
    #     'amount': amount
    # }
    transaction = Transaction(sender, recipient, amount)
    verifier = Verification()
    if verifier.verify_transaction(transaction, get_balance):
        OPEN_TRANSACTIONS.append(transaction)
        save_data()
        return True
    return False


def mine_block():
    """Create a new block and add open transactions to it."""
    last_block = BLOCKCHAIN[-1]
    # List comprehension
    hashed_block = hash_block(last_block)
    proof = proof_of_work()
    # Unordered simple dictionary
    # reward_transaction = {
    #     'sender': 'MINING',
    #     'recipient': OWNER,
    #     'amount': MINING_REWARD
    # }
    reward_transaction = Transaction('MINING', OWNER, MINING_REWARD)
    # Use the range selector with only ':' to create a copy of a list
    copied_transactions = OPEN_TRANSACTIONS[:]
    copied_transactions.append(reward_transaction)
    block = Block(len(BLOCKCHAIN), hashed_block, copied_transactions, proof)
    BLOCKCHAIN.append(block)
    return True


def get_transaction_value():
    """ Returns the input of the user (a new transaction amount) as a float. """
    tx_recipient = input('Enter the recipient of the transaction: ')
    tx_amount = float(input('Your transaction amount please: '))
    return (tx_recipient, tx_amount)


def get_user_choice():
    """Prompts the user for its choice and return it."""
    user_input = input('Your choice: ')
    return user_input


def print_blockchain_elements():
    """ Output all blocks of the blockchain. """
    for block in BLOCKCHAIN:
        print('Outputting block')
        print(block)
    else:
        print('-' * 20)


WAITING_FOR_INPUT = True

while WAITING_FOR_INPUT:
    print('Please choose')
    print('1: Add a new transaction value')
    print('2: Mine a new block')
    print('3: Output the blockchain blocks')
    print('4: Check transaction validity')
    print('q: Quit')
    user_choice = get_user_choice()
    if user_choice == '1':
        tx_data = get_transaction_value()
        # Pulls out data from tuple and store in variables
        recipient, amount = tx_data
        if add_transaction(recipient, amount=amount):
            print('Added transaction!')
        else:
            print('Transaction failed.')
    elif user_choice == '2':
        if mine_block():
            OPEN_TRANSACTIONS = []
            save_data()
    elif user_choice == '3':
        print_blockchain_elements()
    elif user_choice == '4':
        verifier = Verification()
        if verifier.verify_transactions(OPEN_TRANSACTIONS, get_balance):
            print('All transactions are valid')
        else:
            print('There are invalid transactions')
    elif user_choice == 'q':
        WAITING_FOR_INPUT = False
    else:
        print('Input was invalid, please pick a value from the list')
    verifier = Verification()
    if not verifier.verify_chain(BLOCKCHAIN):
        print_blockchain_elements()
        print('Invalid blockchain')
        break
    print('Balance of {}: {:6.2f}'.format('Federico', get_balance('Federico')))


print('Done')
