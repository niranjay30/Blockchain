#Blockchain.py

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes


class different_class:
    string = None
    num = 412412
    def __init__(self, my_string):
        self.string = my_string
    def __repr__(self):
# for data tampering detection, "ALL" the attributes must be
# returned
        return self.string + " " + str(self.num)


class block:

    data = None
    previous_block = None
    previous_hash = None
    

    def __init__(self, data, previous_block):
        self.data = data
        self.previous_block = previous_block
        if previous_block != None:
            self.previous_hash = previous_block.compute_hash()

        
    def compute_hash(self):
        digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
        digest.update(bytes(str(self.data), 'utf-8'))
        digest.update(bytes(str(self.previous_hash), 'utf-8'))
        hash = digest.finalize()
        return hash
    
    
    def is_valid(self):
        if self.previous_block == None:
        	return True
        return self.previous_block.compute_hash() == self.previous_hash


if __name__ == '__main__':

    # Typical blockchain
    
    root = block("I'm the starting node", None)
    b1 = block("I'm the child of root", root)
    b2 = block("I'm the brother of b1", root)
    b3 = block(512382, b1)
    b4 = block(different_class("I'm the child of b2"), b3)
    b5 = block("I'm the child of b4", b4)

    for b in [b1, b2, b3, b4, b5]:
        if b.previous_block.compute_hash() == b.previous_hash:
            print("Great! Hashes match.")
        else:
            print("Wait, the hashes do not match!")

            
    # To detect data tampering
    
    b3.data = 224141
    if b4.previous_block.compute_hash() == b4.previous_hash:
        print("Great! Hashes match. (Detection of data tampering unsuccessful)")
    else:
        print("Wait, tampering detected!")


    # To detect data tampering from some other class
    
    b4.data.num = 53242
    if b5.previous_block.compute_hash() == b5.previous_hash:
        print("Great! Hashes match. (Detection of data tampering unsuccessful)")
    else:
        print("Wait, tampering detected!")
    
