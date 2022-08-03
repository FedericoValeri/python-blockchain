"""Import reduce list function"""
from functools import reduce
import json

from hash_util import hash_block
from block import Block
from transaction import Transaction
from verification import Verification

# Global variables
MINING_REWARD = 10


class Blockchain:
    """Blockchain class"""

    def __init__(self, hosting_node_id):
        # Our starting block for the blockchain
        genesis_block = Block(0, '', [], 100, 0)
        # Initializing (empty) blockchain
        self.chain = [genesis_block]
        # Unhandled transactions
        self.open_transactions = []
        self.load_data()
        self.hosting_node = hosting_node_id

    def load_data(self):
        """Initialize blockchain + open transactions data from a file."""
        try:
            with open('blockchain.txt', mode='r', encoding="utf-8") as file:
                # file_content = pickle.loads(file.read())
                file_content = file.readlines()
                # BLOCKCHAIN = file_content['chain']
                # OPEN_TRANSACTIONS = file_content['ot']
                # Read the blockchain line without the '\n' special character
                blockchain = json.loads(file_content[0][:-1])
                updated_blockchain = []
                for block in blockchain:
                    coverted_tx = [Transaction(
                        tx['sender'], tx['recipient'],
                        tx['amount']) for tx in block['transactions']]
                    updated_block = Block(
                        block['index'], block['previous_hash'],
                        coverted_tx, block['proof'], block['timestamp'])
                    updated_blockchain.append(updated_block)
                self.chain = updated_blockchain
                open_transactions = json.loads(file_content[1])
                updated_transactions = []
                for tx in open_transactions:
                    updated_transaction = Transaction(
                        tx['sender'], tx['recipient'], tx['amount'])
                    updated_transactions.append(updated_transaction)
                self.open_transactions = updated_transactions
        except (IOError, IndexError):
            pass
        finally:
            print('Cleanup!')

    def save_data(self):
        """Save blockchain + open transactions snapshot to a file."""
        try:
            with open('blockchain.txt', mode='w', encoding="utf-8") as file:
                saveable_chain = [block.__dict__ for block in [Block(
                    block_el.index,
                    block_el.previous_hash,
                    [tx.__dict__ for tx in block_el.transactions],
                    block_el.proof, block_el.timestamp) for block_el in self.chain]]
                file.write(json.dumps(saveable_chain))
                file.write('\n')
                saveable_tx = [tx.__dict__ for tx in self.open_transactions]
                file.write(json.dumps(saveable_tx))
                # save_data = {
                #     'chain': blockchain,
                #     'ot': OPEN_TRANSACTIONS
                # }
                # file.write(pickle.dumps(save_data))
        except IOError:
            print('Saving failed!')

    def proof_of_work(self):
        """Generate a proof of work for the open transactions, the hash of the
        previous block and a random number (which is guessed until it fits)."""
        last_block = self.chain[-1]
        last_hash = hash_block(last_block)
        nonce = 0
        while not Verification.valid_proof(self.open_transactions, last_hash, nonce):
            nonce += 1
        return nonce

    def get_balance(self):
        """Calculate and return the balance for a participant."""
        participant = self.hosting_node
        # Nested list comprehension
        tx_sender = [[tx.amount for tx in block.transactions if tx.sender == participant]
                     for block in self.chain]
        open_tx_sender = [tx.amount
                          for tx in self.open_transactions if tx.sender == participant]
        tx_sender.append(open_tx_sender)
        # Reducing list
        amount_sent = reduce(
            lambda tx_sum, tx_amt: tx_sum + sum(tx_amt) if len(tx_amt) > 0 else tx_sum + 0, tx_sender, 0)
        tx_recipient = [[tx.amount for tx in block.transactions if tx.recipient == participant]
                        for block in self.chain]
        # Reducing list
        amount_received = reduce(
            lambda tx_sum, tx_amt: tx_sum + sum(tx_amt) if len(tx_amt) > 0 else tx_sum + 0, tx_recipient, 0)
        return amount_received - amount_sent

    def get_last_blockchain_value(self):
        """ Returns the last value of the current blockchain. """
        # if blockchain is empty
        if len(self.chain) < 1:
            return None
        return self.chain[-1]

    def add_transaction(self, recipient, sender, amount=1.0):
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
        if Verification.verify_transaction(transaction, self.get_balance):
            self.open_transactions.append(transaction)
            self.save_data()
            return True
        return False

    def mine_block(self):
        """Create a new block and add open transactions to it."""
        last_block = self.chain[-1]
        # List comprehension
        hashed_block = hash_block(last_block)
        proof = self.proof_of_work()
        # Unordered simple dictionary
        # reward_transaction = {
        #     'sender': 'MINING',
        #     'recipient': OWNER,
        #     'amount': MINING_REWARD
        # }
        reward_transaction = Transaction(
            'MINING', self.hosting_node, MINING_REWARD)
        # Use the range selector with only ':' to create a copy of a list
        copied_transactions = self.open_transactions[:]
        copied_transactions.append(reward_transaction)
        block = Block(len(self.chain), hashed_block,
                      copied_transactions, proof)
        self.chain.append(block)
        self.open_transactions = []
        self.save_data()
        return True
