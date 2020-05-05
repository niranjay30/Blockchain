# Transaction_Block

from blockchain import Block
from signatures import generate_keys, sign, verify
from transactions import txn
import pickle
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
import random 
import time

reward = 25.0
leading_zeros = 3
next_char_limit = 20

class txn_block(Block):
    
    nonce = "AAAAAAA"

    def __init__(self, previous_block):
        super(txn_block, self).__init__([], previous_block)

    def add_txn(self, txn_in):
        self.data.append(txn_in)
        
    def __count_totals(self):
        total_in = 0
        total_out = 0
        for txn in self.data:
            for addr, amt in txn.inputs:
                total_in = total_in + amt
            for addr, amt in txn.outputs:
                total_out = total_out + amt
        return total_in, total_out

    def is_valid(self):
        if not super(txn_block, self).is_valid():
            return False
        for txn in self.data:
            if not txn.is_valid():
                return False
        total_in, total_out = self.__count_totals()
        if total_out - total_in - reward > 0.0000000000001:
            return False 
        return True

    def good_nonce(self):
        digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
        digest.update(bytes(str(self.data),'utf8'))
        digest.update(bytes(str(self.previous_hash),'utf8'))
        digest.update(bytes(str(self.nonce),'utf8'))
        this_hash = digest.finalize()
       
        if this_hash[:leading_zeros] != bytes(''.join([ '\x4f' for i in range(leading_zeros)]),'utf8'):
            return False
        return int(this_hash[leading_zeros]) < next_char_limit

    def find_nonce(self):
        for i in range(1000000):
            self.nonce = ''.join([ 
                   chr(random.randint(0,255)) for i in range(10*leading_zeros)])
            if self.good_nonce():
                return self.nonce  
        return None
        

if __name__ == '__main__':
    (pr1, pu1) = generate_keys()
    (pr2, pu2) = generate_keys()
    (pr3, pu3) = generate_keys()

    tx1 = txn()
    tx1.add_input(pu1, 1)
    tx1.add_output(pu2, 1)
    tx1.sign(pr1)

    if tx1.is_valid():
        print ('Success! Transaction is valid.')

    savefile = open('txn.dat', 'wb')
    pickle.dump(tx1, savefile)
    savefile.close()

    loadfile = open('txn.dat', 'rb')
    new_txn = pickle.load(loadfile)

    if new_txn.is_valid():
        print ('Success! Loaded Transaction is valid.')
    loadfile.close()

    
    root = txn_block(None)
    root.add_txn(tx1)

    tx2 = txn()
    tx2.add_input(pu2, 1.1)
    tx2.add_output(pu3, 1)
    tx2.sign(pr2)
    root.add_txn(tx2)

    B1 = txn_block(root)

    tx3 = txn()
    tx3.add_input(pu3, 1.1)
    tx3.add_output(pu1, 1)
    tx3.sign(pr3)
    B1.add_txn(tx3)

    tx4 = txn()
    tx4.add_input(pu1, 1)
    tx4.add_output(pu2, 1)
    tx4.add_required(pu3)
    tx4.sign(pr1)
    tx4.sign(pr3)
    B1.add_txn(tx4)
    
    start = time.time()
    print(B1.find_nonce())
    elapsed = time.time() - start
    print("Elapsed time : " + str(elapsed) + "s.")
    if elapsed < 60:
        print("Error! Mining is too fast.")
    if B1.good_nonce():
        print("Success! Nonce is good.")
    else:
        print("Error! Nonce is bad.")

    savefile = open('block.dat', 'wb')
    pickle.dump(B1, savefile)
    savefile.close()

    loadfile = open('block.dat', 'rb')
    load_B1 = pickle.load(loadfile)
    

    for b in [root, B1, load_B1, load_B1.previous_block]:
        if b.is_valid():
            print ('Success! Block is valid.')
        else:
            print ('Error! Block is invalid.')
            
    if B1.good_nonce():
        print("Success! Nonce is good after save and load.")
    else:
        print("Error! Nonce is bad after save and load.")
    
    B2 = txn_block(B1)
    tx5 = txn()
    tx5.add_input(pu3, 1)
    tx5.add_output(pu1, 100)
    tx5.sign(pr3)
    B2.add_txn(tx5)
    

    load_B1.previous_block.add_txn(tx4)

    for b in [B2, load_B1]:
        if b.is_valid():
            print ("Error! Invalid Block couldn't detect.")
        else:
            print ('Success! Invalid Block detected.')
            
    # Test Mining rewards and Transaction fees
    pr4, pu4 = generate_keys()
    B3 = txn_block(B2)
    B3.add_txn(tx2)
    B3.add_txn(tx3)
    B3.add_txn(tx4)
    tx6 = txn()
    tx6.add_output(pu4, 25)
    B3.add_txn(tx6)
    if B3.is_valid():
        print ("Success! Block reward successfully awarded.")
    else:
        print("Error! Block reward couldn't be awarded.")

    # Transaction fees
    B4 = txn_block(B3)
    B4.add_txn(tx2)
    B4.add_txn(tx3)
    B4.add_txn(tx4)
    tx7 = txn()
    tx7.add_output(pu4, 25.2)
    B4.add_txn(tx7)
    if B4.is_valid():
        print ("Success! Transaction fees succeeds.")
    else:
        print("Error! Transaction fees failed")

    # Greedy Miner
    B5 = txn_block(B4)
    B5.add_txn(tx2)
    B5.add_txn(tx3)
    B5.add_txn(tx4)
    tx8 = txn()
    tx8.add_output(pu4, 26.2)
    B5.add_txn(tx8)
    if not B5.is_valid():
        print ("Success! Greedy Miner detected.")
    else:
        print("Error! Greedy Miner couldn't be detected.")   
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
