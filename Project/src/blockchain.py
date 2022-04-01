import json, requests, time
import src.node as node
from src.transaction import Transaction
from src.block import Block
import threading

CAPACITY = 2

class Blockchain:
    def __init__(self):
        self.transactions_list = []
        self.blocks_list = []
        self.new_mine_thread = threading.Event()

    def genesis_block_new(self, parts, nodem):
        address = nodem.public_key
        coins = 100 * (parts + 1)
        # first transaction for bootstrap node
        trans = Transaction('0', address, coins, [])
        trans_dict = json.loads(trans.convert_to_JSON())
        # set transaction id at 0 for bootstrap node
        trans_dict['trans_id'] = 0
        trans_dict = json.dumps(trans_dict)
        genesis = Block(0, trans_dict, 0, 1)  # create genesis block
        self.blocks_list.append(genesis)  # append 1st block

    def parameters_copy(self, addresses,identity):
        self.ID = identity
        self.ring = [adr for adr in addresses]
        return

    def put_transaction_inblock(self, trans):
        '''
            check if there is enough space for the transaction to insert in current block
            else mine
        '''
        self.transactions_list.append(trans)
        # mine needed
        if (CAPACITY == len(self.transactions_list)):
            print("MINE NEEDED")
            node.mine_not_active.clear()
            s = len(self.blocks_list)
            ALL_TRANSACTIONS = [json.loads(i.convert_to_JSON()) for i in self.transactions_list]

            previous = self.blocks_list[-1].current_hash  # hash of previous block -> current hash
            self.transactions_list = []  # reset
            # create new block
            NEO_BLOCK = Block(s, ALL_TRANSACTIONS, 0, previous)
            self.new_mine_thread.clear()
            mine = threading.Thread(name='mine', target=self.domine, args=(NEO_BLOCK,))
            mine.start()
            return

    def domine(self, neo_block):

        print('MINE JUST BEGUN')
        begin = time.time()

        # mine block function
        neo_block.mine_block(self.new_mine_thread)
        if not self.new_mine_thread.isSet() and node.consensus.isSet() is False:
            self.blocks_list.append(neo_block)
            fd = open('times/mining' + '.txt', 'a')
            fd.write(str(time.time() - float(begin)) + '\n')
            fd.close()
            start_time = time.time()

            node.mine_not_active.set()
            if node.consensus.isSet():
                node.consensus.wait()
            for ad in self.ring:
                if (ad != self.ring[self.ID]):
                    # send last block and mining time
                    mes = {'lb': self.blocks_list[-1].convert_block(), 'mt': start_time}
                    requests.post(ad + '/mine', json=mes,headers={'Content-type': 'application/json', 'Accept': 'text/plain'})
                    node.mine_not_active.set()  # stop mining
        return

    def convert_b(self):
        res = {}
        k = 0
        for i in self.blocks_list:
            res[k] = i.convert_block()
            k += 1
        return res


