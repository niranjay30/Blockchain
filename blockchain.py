# Blockchain

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes


class different_class:

    string = None
    num = 1999

    def __init__(self, mystring):
        self.string = mystring

    def __repr__(self):
        return self.string + ' ' + str(self.num)


class Block:

    data = None
    previous_hash = None
    previous_block = None

    def __init__(self, data, previous_block):
        self.data = data
        self.previous_block = previous_block
        if previous_block != None:
            self.previous_hash = previous_block.compute_hash()

    def compute_hash(self):
        digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
        digest.update(bytes(str(self.data), 'utf-8'))
        digest.update(bytes(str(self.previous_hash), 'utf8'))
        return digest.finalize()

    def is_valid(self):
        if self.previous_block == None:
        	return True
        return self.previous_block.compute_hash() == self.previous_hash


if __name__ == '__main__':
    root = Block('I am root', None)
    B1 = Block('I am a child.', root)
    B2 = Block('I am B1s brother', root)
    B3 = Block(12354, B1)
    B4 = Block(different_class('Hi there!'), B3)
    B5 = Block('Top block', B4)

    for b in [B1, B2, B3, B4, B5]:
        if b.previous_block.compute_hash() == b.previous_hash:
            print ('Success! Hash is good.')
        else:
            print ('Error! Hash is no good.')

    B3.data = 12345
    if B4.previous_block.compute_hash() == B4.previous_hash:
        print ("Error! Couldn't detect tampering.")
    else:
        print ('Success! Tampering detected.')

    print (B4.data)
    B4.data.num = 1988
    print (B4.data)
    if B5.previous_block.compute_hash() == B5.previous_hash:
        print ("Error! Couldn't detect tampering.")
    else:
        print ('Success! Tampering detected.')
