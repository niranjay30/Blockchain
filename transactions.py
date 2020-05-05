#Transactions.py

import signatures

class transaction:
    input_addresses = None
    output_address = None
    signature = None
    required_addresses = None


    def __init__(self):
        self.input_addresses = []
        self.output_addresses = []
        self.signature = []
        self.required_addresses = []


    def add_input(self, from_address, amount):
        self.input_addresses.append((from_address, amount))

    
    def add_output(self, to_address, amount):
        self.output_addresses.append((to_address, amount))

    
    def add_required(self, address):
        self.required_addresses.append(address)

    
    def sign(self, private):
        message = self.__gather()
        new_signature = signatures.signature(message, private)
        self.signature.append(new_signature)
    
    
    def is_valid(self):
        total_in = 0
        total_out = 0
        message = self.__gather()
        for addr,amt in self.input_addresses:
            found = False
            for s in self.signature:
                if signatures.verify(message, s, addr):
                    found = True
            if amt < 0:
                return False
            if not found:
                return False
            total_in = total_in + amt
        for addr in self.required_addresses:
            found = False
            for s in self.signature:
                if signatures.verify(message, s, addr):
                    found = True
            if not found:
                return False
        for addr,amt in self.output_addresses:
            if amt < 0:
                return False
            total_out = total_out + amt
        #if total_out > total_in:
            #return False
        return True


    #private method: only used in this class therefore the double underscores "__" in prefix
    def __gather(self):
        data = []
        data.append(self.input_addresses)
        data.append(self.output_addresses)
        data.append(self.required_addresses)
        return data
    
    
    def __repr__(self):
		reprstr = "Inputs:\n"
		for addr, amt in self.inputs:
			reprstr = reprstr + str(amt) + " from " + str(addr) + "\n"
		reprstr = reprstr + "Outputs:\n"
		for addr, amt in self.outputs:
			reprstr = reprstr + str(amt) + " to " + str(addr) + "\n"
		reprstr = reprstr + "Required:\n"
		for r in self.required:
			reprstr = reprstr + str(r) + "\n"
		reprstr = reprstr + "Signatures:\n"
		for s in self.signatures:
			reprstr = reprstr + str(s) + "\n"
		reprstr = reprstr + "End \n"
		return reprstr
    

if __name__ == "__main__":
    pr1, pu1 = signatures.generate_keys()
    pr2, pu2 = signatures.generate_keys()
    pr3, pu3 = signatures.generate_keys()
    pr4, pu4 = signatures.generate_keys()

    # Checking correct signatures
    tx1 = transaction()
    tx1.add_input(pu1, 1)
    tx1.add_output(pu2, 1)
    tx1.sign(pr1)

    tx2 = transaction()
    tx2.add_input(pu1, 2)
    tx2.add_output(pu2, 1)
    tx2.add_output(pu3, 1)
    tx2.sign(pr1)

    tx3 = transaction()
    tx3.add_input(pu3, 1.2)
    tx3.add_output(pu1, 1.1)
    tx3.add_required(pu4)
    tx3.sign(pr3)
    tx3.sign(pr4)

    for t in [tx1, tx2, tx3]:
        if t.is_valid():
            print("Transaction is valid")
        else:
            print("Invalid Transaction")


    # Checking wrong signatures
    tx4 = transaction()
    tx4.add_input(pu1, 1)
    tx4.add_output(pu2, 1)
    tx4.sign(pr2)

    # Bad Escrow transaction (not signed by the arbiter)
    tx5 = transaction()
    tx5.add_input(pu3, 1.2)
    tx5.add_output(pu1, 1.1)
    tx5.add_required(pu4)
    tx5.sign(pr3)

    # Two input address but signed by one
    tx6 = transaction()
    tx6.add_input(pu3, 1)
    tx6.add_input(pu4, 0.1)
    tx6.add_output(pu1, 1.1)
    tx6.sign(pr3)

    # REMEMBER TO REMOVE THIS CONTRAIN AFTER MINING IMPLEMENTATION 
    # Output exceeds input
    tx7 = transaction()
    tx7.add_input(pu4, 1.2)
    tx7.add_output(pu1, 1)
    tx7.add_output(pu2, 2)
    tx7.sign(pr4)

    # Negative amount as input
    tx8 = transaction()
    tx8.add_input(pu2, -1)
    tx8.add_output(pu1, -1)
    tx8.sign(pr2)

    # Modified transaction
    tx9 = transaction()
    tx9.add_input(pu1, 1)
    tx9.add_output(pu2, 1)
    tx9.sign(pr1)
    # output = [(pu2,1)]
    # changed to = [(pu3,1)]
    tx9.output_addresses[0] = (pu3,1)
    
    for t in [tx4, tx5, tx6, tx7, tx8, tx9]:
        if t.is_valid():
            print("Error, incorrect/bad transaction not detected")
        else:
            print("Great, incorrect/bad transaction detected")
