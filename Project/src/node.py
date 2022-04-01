from Crypto.PublicKey import RSA
import threading

from src.block import Block
from src.blockchain import Blockchain
import json
import requests
import time

from src.transaction import Transaction

mine_not_active = threading.Event()
mine_not_active.set()

consensus = threading.Event()  # if set then do consensus
consensus.clear()

class Node:

    # constructor
    def __init__(self, port, IP, children, bootstrap):
        '''
            here the most paarmeters of the system are initialized
        '''
        self.port = port
        self.ip = IP
        self.children = children

        # generate public and private key
        self.public_key, self.private_key = self.generate_wallet()
        bootstrap_ip = 'http://127.0.0.1:'
        #bootstrap_ip = 'http://192.168.0.1:'
        self.all_nodes_chains = {}
        self.all_nodes_transactions = {}
        self.all_utxos = {}

        # contains each node address
        self.ring = [bootstrap_ip + str(5000)]
        self.public_keys = []  # all public keys from the other participants
        self.unspent_coins = []  # list of rest of coins to spend
        self.transactions_dictionary = {}  # save othes' remain coins
        self.buffer = []

        # initialize blockchain
        self.chain = Blockchain()

        self.repeat = threading.Event()
        self.repeat.clear()
        threadone = threading.Thread(target=self.threadone_wait)
        threadone.start()

        # target to auto run transaction tests (5nodes and 10 nodes)
        self.file_runs = threading.Event()
        self.file_runs.clear()
        thread3 = threading.Thread(target=self.all_files_nodes)
        thread3.start()

        # if node is bootstrap
        if bootstrap == "true":
            self.ID = 0
            self.nodes_part = 0  # we count how many nodes are inside
            self.public_keys = [self.public_key]
            self.chain.genesis_block_new(children, self)  # create genesis block
            self.unspent_coins.append(json.loads(self.chain.blocks_list[0].transactions))
            # create thread for bootstrap node to wait until all the nodes have joined
            self.bootstr = threading.Event()
            # set flag of thread to false
            self.bootstr.clear()
            thread = threading.Thread(target=self.cont)
            thread.start()

        else:
            print("child joining")
            # register other nodes in bootstrap
            res = {'addrr': "http://" + self.ip + ":" + str(self.port), 'pub_key': self.public_key}
            # convert object to json
            res = json.dumps(res)
            requests.post(self.ring[0] + "/bootstrap_register", data=res, headers={'Content-type': 'application/json', 'Accept': 'text/plain'})

    @staticmethod
    # generate a public and a private key
    def generate_wallet():
        pair = RSA.generate(2048)
        priv = pair.exportKey('PEM').decode()
        pub = pair.publickey().exportKey('PEM').decode()
        return (pub, priv)

    def cont(self):
        '''
        wait until all children have joined
        then, begin to give to each one of them 100 NBCs
        '''
        self.bootstr.wait()
        print("Everyone has joined!")
        time.sleep(2)

        # continue after thread is set
        for ids, ring in enumerate(self.ring[1:]):
            ids += 1
            g = self.chain.blocks_list[0].convert_block()
            res = {
                'id': ids,
                'ring': self.ring,
                'public_keys': self.public_keys,
                'genesisblock': g  # get genesis block in string format
            }
            res = json.dumps(res)
            requests.post(ring + '/child_inform', data=res,headers={'Content-type': 'application/json', 'Accept': 'text/plain'})


        self.chain.parameters_copy(self.ring, self.ID)

        time.sleep(2)
        # add all unspent transactions to compute balance
        balance = 0
        for trans in self.unspent_coins:
            balance += int(trans['coins'])

        self.transactions_dictionary = {}
        for public_key in self.public_keys:
            self.transactions_dictionary[public_key] = []
     # father sends 100 NBC to each child, if no mining is active
        for c, ring in enumerate(self.ring[1:]):
            if not mine_not_active.isSet():
                mine_not_active.wait()
            t = 1 + c
            self.create_transaction(t, 100)
        self.repeat.set()  # father activate his buffer

    # after all the children have joined, boostrap node will send them unique IDs 1,2,3... # nodes

    def register_child(self, addr, pub_key):
        '''
            add at ring and public keys list the new child's info
        '''
        self.ring.append(addr)
        self.public_keys.append(pub_key)
        # counter for nodes that have joined till now
        self.nodes_part = self.nodes_part + 1
        if self.children == self.nodes_part:
            self.bootstr.set()
        return

    def child_response(self, ID, ring, pub_keys, genesisblock):
        '''
            child's response after the bootstrap node informs it
        '''
        genesisblock = json.loads(genesisblock)

        # parameters from the function call
        self.ID = ID
        self.ring = ring.copy()
        self.chain.parameters_copy(self.ring, self.ID)
        #
        # self.chain.ring = self.ring
        # self.chain.ID = self.ID
        self.public_keys = pub_keys.copy()

        # Initialize dictionary of transactions
        self.transactions_dictionary = {}
        for public_key in self.public_keys:
            self.transactions_dictionary[public_key] = []

        # insert current block at Blockchain
        current_block = Block(genesisblock['index'], genesisblock['transactions'],genesisblock['nonce'], genesisblock['previous_hash'], genesisblock['timestamp'])
        self.chain.blocks_list.append(current_block)
        # get the transactions from genesis block
        transactions = json.loads(genesisblock['transactions'])
        transactions2 = transactions
        final = {
            'trans_id': transactions2['trans_id'],
            'coins': transactions2['coins'],
            'receiver': transactions2['receiver']
        }
        # add bootstrap transaction (nbcs send) at the transactions dictionary
        self.transactions_dictionary[self.public_keys[0]].append(final)

        # the dictionary now has the father's 300 NBCs and the public keys of the rest of the children but with no transactions

        # the child now activates the buffer to receive money
        self.repeat.set()
        return

    def create_transaction(self, children_idnumber, coins):
        print(" CREATE TRANSACTION ")
        insert_outputs = dict()
        outputs= []

        node_id = children_idnumber
        totals = 0
        test = -1
        inpts = []
        for i, unspent_tr in enumerate(self.unspent_coins):
            totals += unspent_tr['coins']
            inpts.append(unspent_tr['trans_id'])
            if totals >= coins:
                result = totals - coins
                test = i
                break
        if totals < coins:
            print("Not enough coins left!")
            return

        node_id = self.public_keys[node_id]
        # create new transaction
        fd = open('times/transactions_t' + str(self.ID) +  '.txt', 'a')
        start_time = time.time()
        NEA_SINALLAGI = Transaction(self.public_key, node_id, coins, inpts)

        insert_outputs["trans_id"] = NEA_SINALLAGI.transaction_id
        insert_outputs["recipient"] = NEA_SINALLAGI.receiver
        insert_outputs["coins"] = NEA_SINALLAGI.coins
        outputs.append(insert_outputs)
        insert_outputs = insert_outputs.copy()
        insert_outputs["trans_id"] = NEA_SINALLAGI.transaction_id
        insert_outputs["sender"] = NEA_SINALLAGI.sender
        insert_outputs["coins"] = result
        # add outputs list
        outputs.append(insert_outputs)
        if test == len(self.unspent_coins) - 1:
            self.unspent_coins = [outputs[1]]
        else:
            self.unspent_coins = self.unspent_coins[test + 1:]
            self.unspent_coins.append(outputs[1])

        NEA_SINALLAGI.outputs = outputs
        self.transactions_dictionary[self.public_key] = self.unspent_coins.copy()
        self.transactions_dictionary[node_id].append(outputs[0])

        # sign transaction
        NEA_SINALLAGI.sign_transaction(self.private_key)
        # broadcast
        self.broadcast_transaction(NEA_SINALLAGI)
        # Add new transaction in the block
        self.chain.put_transaction_inblock(NEA_SINALLAGI)
        fd.write(str(time.time() - start_time) + '\n')  # save time of the transaction to complete
        fd.close()

        return

    def broadcast_transaction(self, NEO):
        # Broadcast transaction
        print("BROADCAST Transaction")
        res = json.loads(NEO.convert_to_JSON())
        res['trans_id'] = NEO.transaction_id
        for ring in self.ring:
            if not (ring == self.ring[self.ID]):
                requests.post(ring + "/broadcast", json=res,headers={'Content-type': 'application/json', 'Accept': 'text/plain'})
        return

    def threadone_wait(self):
        self.repeat.wait()
        print("REPEAT MODE")
        rep = 1
        while (True):
            if not mine_not_active.isSet():
                mine_not_active.wait()
            if consensus.isSet():
                consensus.wait()

            if (len(self.buffer) != 0 and mine_not_active.isSet() and consensus.isSet() is False):
                buffer_item = self.buffer.pop(0)
                # transaction process start
                thesender = buffer_item[0]
                thereceiver = buffer_item[1]
                coins = buffer_item[2]
                inputs = buffer_item[3]
                outputs = buffer_item[4]
                signature = buffer_item[5]
                idd = buffer_item[6]

                Tr = Transaction(thesender, thereceiver, coins, inputs, outputs)
                Tr.signature = signature
                Tr.transaction_id = idd

                # Find sender_id and receiver_id from public keys
                for i in range(len(self.public_keys)):
                    if self.public_keys[i] == thesender:
                        sender_id = i

                    elif self.public_keys[i] == thereceiver:
                        receiver_id = i

                # Check if the broadcasted transaction is valid
                if self.validate_transaction(Tr, sender_id):
                    # Update block
                    self.chain.put_transaction_inblock(Tr)
                    # Update corresponding trans_dict values
                    for inputs in Tr.inputs:
                        for idx, unspent_id in enumerate(self.transactions_dictionary[thesender]):
                            if inputs == unspent_id['trans_id']:
                                self.transactions_dictionary[thesender].remove(self.transactions_dictionary[thesender][idx])

                    self.transactions_dictionary[thereceiver].append(Tr.outputs[0])
                    self.transactions_dictionary[thesender].append(Tr.outputs[1])

                    if thereceiver == self.public_key:
                        self.unspent_coins.append(Tr.outputs[0])
                # transaction process end
                time.sleep(1)
                if rep == 1:
                    if self.ID == self.children:
                        for ring in self.ring:
                            requests.post(ring + "/alltrans",headers={'Content-type': 'application/json', 'Accept': 'text/plain'})
                        rep = 23
        return




    def wallet_balance(self):
      balance = 0
      for TRANS in self.unspent_coins:
        balance += int(TRANS['coins'])
      return balance

    def validate_block(self, BLOCK, mine_time):
        if consensus.isSet():
            consensus.wait()
        fd = open('times/ValidateTime' + '.txt', 'a')  # file for mine times for each node

        BLOCK = json.loads(BLOCK)
        #fd = open('times/mining' + '.txt', 'a')
        trans = [i for i in BLOCK['transactions']]

        # invalid chain length
        if not BLOCK['previous_hash'] == self.chain.blocks_list[-1].current_hash:
            self.chain.new_mine_thread.set()
            consensus.set()
            for ring in self.ring:
                if not (ring == self.ring[self.ID]):
                    requests.post(ring + "/consensus", json = {'address': self.ring[self.ID]}, headers={'Content-type': 'application/json', 'Accept': 'text/plain'})
            print('ALERT! WE START CONSENSUS!')
            self.chain.blocks_list = self.resolve_conflict()
            fd.write(str(time.time() - float(mine_time)) + '\n')  # write mine time in file and close
            fd.close()
            consensus.clear()
            print('CONSENSUS DONE', consensus.isSet(), len(self.buffer))
            return False

        bb = Block(int(BLOCK['index']), trans, int(BLOCK['nonce']), BLOCK['previous_hash'], float(BLOCK['timestamp']))
        if bb.hashing() == BLOCK['current_hash']:
            self.chain.new_mine_thread.set()
            bb.current_hash = BLOCK['current_hash']
            self.chain.blocks_list.append(bb)
            fd.write(str(time.time() - float(mine_time)) + '\n')
            fd.close()
            return True
        return False

    def resolve_conflict(self):
        print("RESOLVE CONFLICT")
        all_nodes_chains, all_nodes_transactions, all_utxos = self.all_nodes_chains, self.all_nodes_transactions, self.all_utxos
        while True:
            if len(all_nodes_chains) == self.children and len(all_utxos) == self.children:  # if all go in
                new_chain = max(all_nodes_chains.values(),
                                key=lambda x: len(x))  # check length of all chain and pick the greater
                break
        self.all_nodes_chains = {}
        self.all_nodes_transactions = {}  # reset dicts again
        self.all_utxos = {}

        new_blocks = []
        for i in new_chain.values():
            b = json.loads(i)
            trans = [i for i in b['transactions']]
            block = Block(int(b['index']), trans, int(b['nonce']), b['previous_hash'], float(b['timestamp']))
            new_blocks.append(block)
        return new_blocks  # return results

    def all_files_nodes(self):
        # wait to run all transactions from files
        self.file_runs.wait()
        time.sleep(5)
        if not mine_not_active.isSet():
            mine_not_active.wait()
        print('START FILE TRANSACTIONS')
        with open('5nodes/transactions' + str(self.ID) + '.txt', 'r') as fd:
            for line in fd:
                rec, coins = (line.strip('\n')).split(' ')
                url = 'http://' + str(self.ip) + ':' + str(self.port) + "/create_transaction"
                payload = {'address': rec[2], 'coins': coins}
                payload = json.dumps(payload)
                requests.post(url, data=payload, headers={'Content-type': 'application/json','Accept': 'text/plain'})
                time.sleep(1)
        return

    def validate_transaction(self, trans, sender_id):
        print("VALIDATE")
        validate_signature = trans.verify_signature(self.public_keys[sender_id])
        local_ids = [i['trans_id'] for i in self.transactions_dictionary[self.public_keys[sender_id]]]
        return all([i in local_ids for i in trans.inputs]) and validate_signature



