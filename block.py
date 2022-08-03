from time import time
from utility.printable import Printable


class Block(Printable):
    """A single block of our blockchain.

    Attributes:
        :index: the index of this block.
        :previous_hash: the hash of the previous block in the blockchain.
        :timestamp: the timestamp of the block
        :transactions: a list of transactions which are included in the block.
        :proof: the proof of work number that yielded this block.
    """

    def __init__(self, index, previous_hash, transactions, proof, timestamp=None):
        self.index = index
        self.previous_hash = previous_hash
        self.timestamp = time() if timestamp is None else timestamp
        self.transactions = transactions
        self.proof = proof
