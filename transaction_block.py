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
leading_zeros = 2
next_char_limit = 255
verbose = False

class txn_block(Block):
    
    nonce = "AAAAAAA"

    def __init__(self, previous_block):
        super(txn_block, self).__init__([], previous_block)

    def add_txn(self, txn_in):
        self.data.append(txn_in)
        
    
    def remove_txn(self, txn_in):
        try:
            self.data.remove(txn_in)
        except:
            return False
        return True
        #if txn_in in self.data:
#            self.data.remove(txn_in)
#            return True
#        return False
    
        
    def count_totals(self):
        total_in = 0
        total_out = 0
        for txn in self.data:
            for addr, amt, inx in txn.inputs:
                total_in = total_in + amt
            for addr, amt in txn.outputs:
                total_out = total_out + amt
        return total_in, total_out
        
    
    def check_size (self):
        save_previous = self.previous_block
        self.previous_block = None
        this_size = len(pickle.dumps(self))
        self.previous_block = save_previous
        if this_size > 10000:
            return False
        return True
        

    def is_valid(self):
        if not super(txn_block, self).is_valid():
            return False
        spendings = {}
        for txn in self.data:
            if not txn.is_valid():
                return False
            for addr, amt, inx in txn.inputs:
                if not addr in spendings:
                    spendings[addr] = amt
                else:
                    spendings[addr] = spendings[addr] + amt
                if not inx - 1 == get_last_txn_index(addr, self.previous_block):
                    found = False
                    count = 0
                    for tx2 in self.data:
                        for addr2, amt2, inx2 in tx2.inputs:
                            if addr == addr2 and inx2 == inx - 1:
                                found = True
                            if addr == addr2 and inx2 == inx and not txn is tx2:
                                count = count + 1
                                
                    if not found or count > 1:
                        return False
            for addr, amt in txn.outputs:
                if addr in spendings:
                    spendings[addr] = spendings[addr] - amt
                else:
                    spendings[addr] = -amt
        for this_addr in spendings:
            if verbose: print("Balance: " + str(get_balance(this_addr, self.previous_block)))
            if verbose: print("Spendings: " + str(spendings[this_addr]))
            if spendings[this_addr] - get_balance(this_addr, self.previous_block) > 0.000000001:
                return False
            
        
        total_in, total_out = self.count_totals()
        if total_out - total_in - reward > 0.0000000000001:
            return False
        if not self.check_size():
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

    def find_nonce(self, n_tries = 1000000):
        for i in range(n_tries):
            self.nonce = ''.join([ 
                   chr(random.randint(0,255)) for i in range(10*leading_zeros)])
            if self.good_nonce():
                return self.nonce  
        return None
        
        
def find_longest_blockchain(head_blocks):
    longest = -1
    long_head = None
    for b in head_blocks:
        current = b
        this_len = 0
        while current != None:
            this_len = this_len + 1
            current = current.previous_block
        if this_len > longest:
            long_head = b
            longest = this_len
    return long_head


def save_blocks(block_list, filename):
    fp = open(filename, "wb")
    pickle.dump(block_list, fp)
    fp.close()
    return True
	

def load_blocks(filename):
    fin = open(filename, "rb")
    ret = pickle.load(fin)
    fin.close()
    return ret
    
    
def get_balance (pu_key, last_block):
    this_block = last_block
    bal = 0.0
    while this_block != None:
        for txn in this_block.data:
            for addr, amt, inx in txn.inputs:
                if addr == pu_key:
                    bal = bal - amt
            for addr, amt in txn.outputs:
                if addr == pu_key:
                    bal = bal + amt
        this_block = this_block.previous_block
    return bal


def get_last_txn_index (pu_key, head_block):
    this_block = head_block
    index = -1
    while this_block != None:
        for txn in this_block.data:
            for addr, amt, inx in txn.inputs:
                if addr == pu_key and inx > index:
                    index = inx
        if index != -1:
            break
        this_block = this_block.previous_block
    return index
    
    
def process_new_block(new_block, head_blocks, verbose):
    if verbose: print("Recieved block")
    found = False
    for b in head_blocks:
        if b == None:
            if new_block.previous_hash == None:
                found = True
                new_block.previous_block = b
                if not new_block.is_valid():
                    print("Error! new_block is invalid.")
                else:
                    head_blocks.remove(b)
                    head_blocks.append(new_block)
                    if verbose: print("Added to head_blocks.")
                
        elif new_block.previous_hash == b.compute_hash():
            found = True
            new_block.previous_block = b
            if not new_block.is_valid():
                print("Error! new_block is invalid.")
            else:
                head_blocks.remove(b)
                head_blocks.append(new_block)
                if verbose: print("Added to head_blocks")
               
        else:
            this_block = b
            while this_block != None:
                if new_block.previous_hash == this_block.previous_hash:
                    found = True
                    new_block.previous_block = this_block.previous_block
                    if not new_block in head_blocks:
                        head_blocks.append(new_block)
                        if verbose: print("Added new sister block")

                this_block = this_block.previous_block
        if not found:
            print ("Error! Couldn't find a parent for new_block")
            

if __name__ == '__main__':
    (pr1, pu1) = generate_keys()
    (pr2, pu2) = generate_keys()
    (pr3, pu3) = generate_keys()
    
    pu_indeces = {}
    
    def indexed_input(txn_inout, public_key, amt, index_map):
        if not public_key in index_map:
            index_map[public_key] = 0
        txn_inout.add_input(public_key, amt, index_map[public_key])
        index_map[public_key] = index_map[public_key] + 1

    tx1 = txn()
    indexed_input(tx1, pu1, 1, pu_indeces)
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
    mine1 = txn()
    mine1.add_output(pu1,8.0)
    mine1.add_output(pu2,8.0)
    mine1.add_output(pu3,8.0)
    
    root.add_txn(tx1)
    root.add_txn(mine1)

    tx2 = txn()
    indexed_input(tx2, pu2, 1.1, pu_indeces)
    tx2.add_output(pu3, 1)
    tx2.sign(pr2)
    root.add_txn(tx2)

    B1 = txn_block(root)

    tx3 = txn()
    indexed_input(tx3, pu3, 1.1, pu_indeces)
    tx3.add_output(pu1, 1)
    tx3.sign(pr3)
    B1.add_txn(tx3)

    tx4 = txn()
    indexed_input(tx4, pu1, 1, pu_indeces)
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
        print (B1.nonce)
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
    indexed_input(tx5, pu3, 1, pu_indeces)
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
    
    tx2 = txn()
    indexed_input(tx2, pu2, 1.1, pu_indeces)
    tx2.add_output(pu3, 1)
    tx2.sign(pr2)
    
    tx3 = txn()
    indexed_input(tx3, pu3, 1.1, pu_indeces)
    tx3.add_output(pu1, 1)
    tx3.sign(pr3)
    
    tx4 = txn()
    indexed_input(tx4, pu1, 1, pu_indeces)
    tx4.add_output(pu2, 1)
    tx4.add_required(pu3)
    tx4.sign(pr1)
    tx4.sign(pr3)
    
    B3.add_txn(tx2)
    B3.add_txn(tx3)
    B3.add_txn(tx4)
    
    tx6 = txn()
    tx6.add_output(pu4,25)
    B3.add_txn(tx6)
    
    if B3.is_valid():
        print ("Success! Block reward successfully awarded.")
    else:
        print("Error! Block reward couldn't be awarded.")

    # Transaction fees
    B4 = txn_block(B3)
    
    tx2 = txn()
    indexed_input(tx2, pu2, 1.1, pu_indeces)
    tx2.add_output(pu3, 1)
    tx2.sign(pr2)
    
    tx3 = txn()
    indexed_input(tx3, pu3, 1.1, pu_indeces)
    tx3.add_output(pu1, 1)
    tx3.sign(pr3)
    
    tx4 = txn()
    indexed_input(tx4, pu1, 1, pu_indeces)
    tx4.add_output(pu2, 1)
    tx4.add_required(pu3)
    tx4.sign(pr1)
    tx4.sign(pr3)
    
    B4.add_txn(tx2)
    B4.add_txn(tx3)
    B4.add_txn(tx4)
    
    tx7 = txn()
    tx7.add_output(pu4,25.2)
    B4.add_txn(tx7)

    if B4.is_valid():
        print ("Success! Transaction fees succeeds.")
    else:
        print("Error! Transaction fees failed")

    # Greedy Miner
    B5 = txn_block(B4)
    
    tx2 = txn()
    indexed_input(tx2, pu2, 1.1, pu_indeces)
    tx2.add_output(pu3, 1)
    tx2.sign(pr2)
    
    tx3 = txn()
    indexed_input(tx3, pu3, 1.1, pu_indeces)
    tx3.add_output(pu1, 1)
    tx3.sign(pr3)
    
    tx4 = txn()
    indexed_input(tx4, pu1, 1, pu_indeces)
    tx4.add_output(pu2, 1)
    tx4.add_required(pu3)
    tx4.sign(pr1)
    tx4.sign(pr3)
    
    B5.add_txn(tx2)
    B5.add_txn(tx3)
    B5.add_txn(tx4)
    
    tx8 = txn()
    tx8.add_output(pu4,26.2)
    B5.add_txn(tx8)
    
    if not B5.is_valid():
        print ("Success! Greedy Miner detected.")
    else:
        print("Error! Greedy Miner couldn't be detected.")   
    
    print("pu4 bal:")
    print(get_balance(pu4,B5))
    
    B6 = txn_block(B4)
    last_pu, last_pr = pu4, pr4
    last_val = 3.789
    for i in range(30):
        new_txn = txn()
        new_pr, new_pu = generate_keys()
        indexed_input(new_txn, last_pu, last_val, pu_indeces)
        new_txn.add_output(new_pu, last_val - 0.02)
        new_txn.add_output(pu4,0.02)
        new_txn.sign(last_pr)
        B6.add_txn(new_txn)
        last_pu, last_pr = new_pu, new_pr
        save_previous = B6.previous_block
        B6.previous_block = None
        
        if len(pickle.dumps(B6)) > 10000:
            B6.previous_block = save_previous
            if B6.is_valid():
                print("Error! Big blocks are valid.")
        if len(pickle.dumps(B6)) <= 10000:
            B6.previous_block = save_previous
            if not B6.is_valid():
                print("Error! Small blocks are invalid.")
        B6.previous_block = save_previous
    pu_indeces[pu4] = pu_indeces[pu4] - 1
    
    
    print("pu1 bal:")
    print(get_balance(pu1,B5))
    
    B7 = txn_block(B5)
    
    tx9 = txn()
    indexed_input(tx9, pu1, 25, pu_indeces)
    indexed_input(tx9, pu1, 25, pu_indeces)
    indexed_input(tx9, pu1, 25, pu_indeces)
    indexed_input(tx9, pu1, 25, pu_indeces)
    indexed_input(tx9, pu1, 25, pu_indeces)
    indexed_input(tx9, pu1, 25, pu_indeces)
    tx9.sign(pr1)
    B7.add_txn(tx9)
    
    if not B7.is_valid():
        print ("Success! Overspend detected.")
    else:
        print("Error! Over-spend not detected.")
    
    print("pu1 bal:")
    print(get_balance(pu1,B5))
    pu_indeces[pu1] = pu_indeces[pu1] - 6
    
    B8 = txn_block(B5)
    
    tx9 = txn()
    indexed_input(tx9, pu1, 30, pu_indeces)
    tx9.add_output(pu2,30)
    tx9.sign(pr1)
    B8.add_txn(tx9)
    
    tx10 = txn()
    indexed_input(tx10, pu1, 30, pu_indeces)
    tx10.add_output(pu2,30)
    tx10.sign(pr1)
    B8.add_txn(tx10)
    
    tx11 = txn()
    indexed_input(tx11, pu1, 30, pu_indeces)
    tx11.add_output(pu2,30)
    tx11.sign(pr1)
    B8.add_txn(tx11)
    
    tx12 = txn()
    indexed_input(tx12, pu1, 30, pu_indeces)
    tx12.add_output(pu2,30)
    tx12.sign(pr1)
    B8.add_txn(tx12)
    
    if not B8.is_valid():
        print ("Success! Overspend detected.")
    else:
        print("Error! Over-spend not detected.")
    
    
    
    
    
    
    
    
    
    
