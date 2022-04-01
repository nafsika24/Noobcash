import json
import requests
from flask import Flask, jsonify, request, session, render_template
import sys
from src.node import Node, mine_not_active
from flask_cors import CORS


app = Flask(__name__)
CORS(app)
#app.debug = True

KEY_ID = '-'

if len(sys.argv) != 5:
    print("You should provide 5 parameters!")
    print("7 parameters [app.py, Port, IP, number of children, if bootstrap node or not]: Insert nodes at blockchain.")
    sys.exit(0)

start = Node(int(sys.argv[1]), sys.argv[2], int(sys.argv[3]), sys.argv[4])

#  bootstrap node registers child in the blockchain
@app.route('/bootstrap_register', methods=['POST'])
def register():
    pub_key = request.json['pub_key']
    addr = request.json['addrr']
    start.register_child(addr,pub_key)
    response = { 'message': 'Node registered.' }
    return jsonify(response),200

#  send all children info about the id, ring, public keys, genesis block
@app.route('/child_inform', methods=['POST'])
def info():
    res = request.get_json()
    start.child_response(res['id'], res['ring'], res['public_keys'], res['genesisblock'])
    response = {'message': 'Node Informed'}
    return jsonify(response), 200

@app.route('/broadcast', methods=['POST'])
def broadcast():
    res = request.get_json()
    start.buffer.append([res['sender'], res['receiver'], res['coins'], res['inputs'],  res['outputs'], res['signature'], res['trans_id']])
    response = {'message': 'Broadcast finished'}
    return jsonify(response), 200


@app.route('/mine', methods=['POST'])
def mining():
    res = request.get_json()
    if start.validate_block(res['lb'], res['mt']):
        mine_not_active.set()
        response = { 'message': 'Current block successfully inserted.' }
        return jsonify(response), 201
    else:
        mine_not_active.set()
        response = {'message': 'Current block was not inserted.' }
        return jsonify(response), 400


@app.route('/consensus', methods=['POST'])
def consensus():
    # consensus begin
    res = request.get_json()
    addrr = res['address']
    msg = {'pub_key': start.public_key, 'chain': start.chain.convert_b(), 'trans_dict': start.transactions_dictionary, 'utxos': start.unspent_coins}
    requests.post(addrr + '/all_nodes_consensus', json=msg,headers={'Content-type': 'application/json', 'Accept': 'text/plain'})
    response = {'message': 'Consensus done'}
    return jsonify(response), 200


@app.route('/all_nodes_consensus', methods=['POST'])
def cons_data():
    res = request.get_json()
    start.all_nodes_chains[res['pub_key']] = res['chain']
    start.all_nodes_transactions[res['pub_key']] = res['trans_dict']
    start.all_utxos[res['pub_key']] = res['utxos']

    print('NODE INFORMED: ', str(start.ID))
    response = {'message': 'Consensus Done'}
    return jsonify(response), 200

@app.route('/alltrans', methods=['POST'])
def cons():
    # consensus done, begin transactions from files
    #start.file_runs.set()
    response = {'message': 'File Transactions Completed'}
    print("COMPLETED ALL TRANSACTIONS")
    return jsonify(response), 200

@app.route('/create_transaction', methods=['POST'])
def newtrans():
    res = request.get_json()
    address = res['address']
    coins = res['coins']

    print ("Send coins at node: ",address)
    print("COINS = ", coins)

    if int(address) == start.ID:
        response = { 'message': 'You are not allowed to send coins to yourself! Try again.' }
        return jsonify(response), 400
    elif not address.isnumeric() or int(address) < 0 or int(address) > start.children:
        response = { 'message': 'Invalid ID. Provide and ID between 0 and ' + str(start.children) }
        return jsonify(response), 400

    elif not coins.isnumeric() or int(coins) <= 0:
        response = { 'message': "Invalid Amount Given." }
        return jsonify(response), 400

    elif int(coins) > start.wallet_balance():
        print(start.wallet_balance())
        response = { 'message': "You are out of coins" }
        return jsonify(response), 400

    else:
        if not mine_not_active.isSet():
            mine_not_active.wait()
        start.create_transaction(int(address), int(coins))

        response = { 'message': "Transaction Completed" }
    return jsonify(response), 200

#================== CLI COMMANDS ================

@app.route('/view_transactions', methods=['GET'])
def get_trans():
    print(len(start.chain.blocks_list))
    last_transactions = start.chain.blocks_list[-1].transactions
    response = { 'Transactions of the last block (verified)': last_transactions }
    return jsonify(response), 200


@app.route('/show_balance', methods=['GET'])
def get_bal():
    bal = start.wallet_balance()
    x = len(start.chain.blocks_list)
    y = len(start.buffer)
    print('The balance is: ',x,y)
    response = {
        'Current Balance': bal
    }
    return jsonify(response), 200

# ============ FRONTEND =============

# Home page
@app.route('/', methods=['GET'])
def home():
    # Keep track of current page
    #session['viewing'] = 'home'
    bal = start.wallet_balance()

    data = {
        'ADDRESS': 'http://' + str(start.ip) +':' + str(start.port) ,
        'NO_OF_NODES':  len(set(start.ring)),
        'ID': start.ID,
        'SENDER': start.public_key,
        'OTHERSK': start.public_keys,
        'KEY_ID': KEY_ID,
        'bal': bal,

    }
    return render_template('homepage.html', data=data)

# view latest transaction
@app.route('/view', methods=['GET'])
def viewpage():

    coins = []
    inputs = []
    outputs = []
    receiv = []
    sender = []
    bal = start.wallet_balance()
    # for tr in start.chain.blocks_list[-1].transactions:
    #
    #    if str(tr) == '{':
    #        data = {
    #            'ADDRESS': 'http://' + str(start.ip) + ':' + str(start.port),
    #            'NO_OF_NODES': len(set(start.ring)),
    #            'ID': start.ID,
    #            'SENDER': start.public_key,
    #            'OTHERSK': start.public_keys,
    #            'KEY_ID': KEY_ID,
    #            'bal': bal
    #
    #        }
    #        return  render_template('homepage.html',data = data)
    #    else:
    #        coins.append(tr['coins'])
    #        inputs.append(tr['inputs'])
    #        outputs.append(tr['outputs'])
    #        receiv.append(tr['receiver'])
    #        sender.append(tr['sender'])
    #
    #        data = {
    #              'coins': coins,
    #             'inputs': inputs,
    #             'outputs': outputs,
    #             'receiver': receiv,
    #             'sender': sender,}
    res1 = start.chain.blocks_list[-1].transactions
    return render_template('viewpage.html', data=start.chain.blocks_list[-1].transactions)

@app.route('/balance', methods=['GET'])
def balancepage():
    bal = start.wallet_balance()
    data = {
        'bal': bal,
        'id': str(start.ID)
    }
    return render_template('balancepage.html', data=data)

@app.route('/about', methods=['GET'])
def aboutpage():
    return render_template('about.html')

@app.route('/help', methods=['GET'])
def helppage():
    return render_template('help.html')

@app.route('/create_transaction_webapp', methods=['POST'])
def webapp_transaction():
    print("FRONTEND TRANSACTION")
    res = request.get_json()
    print(res)

    sender = res['sender']
    receiver = res['receiver']
    coins = res['amount']

    if not coins.isnumeric():
        response = 'You should provide a number for the coins.'
        return jsonify(response), 400
    elif sender == receiver:
        response = 'You can not send money to yourself.'
        return jsonify(response), 400

    elif start.ID != int(sender):
        response = 'This is not your ID.'
        return jsonify(response), 400

    elif int(sender) != start.ID:
        response = 'Your ID is not valid.'
        return jsonify(response), 400
    else:
        payload = {'address': receiver, 'coins': coins}
        payload = json.dumps(payload)
        print(payload)
        URL = 'http://' + str(start.ip) + ':' + str(start.port) + "/"
        response = requests.post(URL + "create_transaction", data=payload, headers={'Content-type': 'application/json', 'Accept': 'text/plain'})
        if response.status_code == 200:
            print('Transaction Done!')
        else:
            print(f'Error: {response.text}')
    response = {'message': 'OKEIII'}
    return jsonify(response), 200

# @app.route('/search_by_key', methods=['POST'])
# def search_by_key():
#     res = request.get_json()
#     key = res['key']
#     if('-----BEGIN PUBLIC KEY-----' in key and '-----END PUBLIC KEY-----' in key):
#         x = key.split('-----BEGIN PUBLIC KEY-----')[1]
#         x = x.split('-----END PUBLIC KEY-----')[0]
#         x = x.replace('\\n', '\n ')
#         x = x.replace(' ', '')
#         res = '-----BEGIN PUBLIC KEY-----' + x + '-----END PUBLIC KEY-----'
#         id = start.public_keys.index(res)
#         print(id)
#         KEY_ID = id
#         data = {
#             'ADDRESS': 'http://' + str(start.ip) + ':' + str(start.port),
#             'NO_OF_NODES': len(set(start.ring)),
#             'ID': start.ID,
#             'SENDER': start.public_key,
#             'OTHERSK': start.public_keys,
#             'KEY_ID': str(KEY_ID)
#         }
#         print(data)
#         return render_template('homepage.html', data=data)
#     else:
#         response = 'This is not a valid public key.'
#         return jsonify(response), 400



if __name__ == '__main__':
    app.run(host=sys.argv[2], port=int(sys.argv[1]))




