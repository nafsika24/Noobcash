import base64

from Crypto.Hash import SHA
from Crypto.PublicKey import RSA

from Crypto.Signature import PKCS1_v1_5
import json

class Transaction:
    def __init__(self, sender, receiver, coins, inputs, outputs = []):
        # transactions info
        self.sender = sender
        self.receiver = receiver
        self.coins = coins
        self.inputs = inputs
        self.outputs = outputs
        self.signature = ''
        self.transaction_id = self.hashing().hexdigest()

    def convert_to_JSON(self):
        tr = {
            'sender': self.sender,
            'receiver': self.receiver,
            'coins': self.coins,
            'inputs': self.inputs,
            'outputs': self.outputs,
            'signature': self.signature
        }
        string = json.dumps(tr, sort_keys=True)
        return string

    def sign_transaction(self, private_key):
        hashed = SHA.new(str(self.convert_to_JSON()).encode())
        rsa = RSA.importKey(private_key)
        si = PKCS1_v1_5.new(rsa)
        self.transaction_id = hashed.hexdigest()
        self.signature = (base64.b64encode(si.sign(hashed)).decode())
        return

    def verify_signature(self, public_key):
        hashed = json.loads(self.convert_to_JSON())
        hashed['signature'] = ''
        hashed = json.dumps(hashed, sort_keys=True)
        hashed = SHA.new(str(hashed).encode())
        pup = RSA.importKey(public_key)
        verifier = PKCS1_v1_5.new(pup)
        return verifier.verify(hashed, base64.b64decode(self.signature))

    def hashing(self):
        string = self.convert_to_JSON()
        return SHA.new(string.encode())

