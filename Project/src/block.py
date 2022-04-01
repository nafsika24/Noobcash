import hashlib as hasher
import time
import json
DIFFICULTY = 4
class Block:

    def __init__(self, index, transactions, nonce, previous_hash, timestamp=time.time()):
        # blocks's info
        self.index = index
        self.transactions = transactions
        # proof of work solution
        self.nonce = nonce
        self.previous_hash = previous_hash
        self.timestamp = timestamp
        self.current_hash = -1


    def insertdif(self, dif):
        self.dif = dif

    def convert_block(self):
        res = json.dumps(dict(index = self.index, timestamp = self.timestamp.__str__(), transactions = self.transactions,nonce = self.nonce, current_hash = self.current_hash,previous_hash=self.previous_hash ), sort_keys=True)
        return (res)

    # =================== Mining Process =================

    def hashing(self):
        '''
        :return: current block's hash
        '''
        x = json.loads(self.convert_block())
        del x['current_hash']
        res = hasher.sha256(self.convert_block().encode()).hexdigest()
        return res

    def mine_block(self, temp):
        while self.hashing()[:DIFFICULTY] == '0' * DIFFICULTY is False and not temp.isSet():
            self.nonce += 1
        self.current_hash = self.hashing()
        return self






