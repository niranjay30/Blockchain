#Transactions

import signatures

class txn:
	inputs = None
	outputs = None
	signatures = None
	required = None 
	
	def __init__(self):
		self.inputs = []
		self.outputs = []
		self.signatures = []
		self.required = []
	
	def add_input(self, from_address, amount):
		self.inputs.append((from_address, amount))
		
	def add_output(self, to_address, amount):
		self.outputs.append((to_address, amount))
		
	def add_required(self, address):
		self.required.append(address)
		
	def sign(self, private_key):
		message = self.__gather()
		new_signature = signatures.sign(message, private_key)
		self.signatures.append(new_signature)
		
	def is_valid(self):
		total_in = 0
		total_out = 0
		message = self.__gather()
		for address, amount in self.inputs:
			found = False
			for s in self.signatures:
				if signatures.verify(message, s, address):
					found = True 
			if not found:
				return False
			if amount < 0:
				return False
			total_in = total_in + amount 
		for address in self.required:
			found = False
			for s in self.signatures:
				if signatures.verify(message, s, address):
					found = True 
			if not found:
				return False 
		for address, amount in self.outputs:
			if amount < 0:
				return False
			total_out = total_out + amount 
			
		#if total_in < total_out:
#			return False 
		
		return True
		
	def __gather(self):
		data = []
		data.append(self.inputs)
		data.append(self.outputs)
		data.append(self.required)
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
	    
if __name__ == '__main__':
	pr1, pu1 = signatures.generate_keys()
	pr2, pu2 = signatures.generate_keys()
	pr3, pu3 = signatures.generate_keys()
	pr4, pu4 = signatures.generate_keys()
	
	# Regular Transaction 
	tx1 = txn()
	tx1.add_input(pu1, 1)
	tx1.add_output(pu2, 1)
	tx1.sign(pr1)

	# Transaction with 2 outputs 
	tx2 = txn()
	tx2.add_input(pu1, 2)
	tx2.add_output(pu2, 1)
	tx2.add_output(pu3, 1)
	tx2.sign(pr1)
	
	
	# Escrow Transaction  with input greater than output i.e transaction fee included 
	tx3 = txn()
	tx3.add_input(pu1, 1.2)
	tx3.add_output(pu2, 1)
	tx3.add_required(pu3)
	tx3.sign(pr1)
	tx3.sign(pr3) 
	
	# Checking for valid transactions 
	for t in [tx1, tx2, tx3]:
		if t.is_valid():
			print("Success! Transaction is valid.")
		else:
			print("Error! Transaction is invalid.")
			
			
	# Transaction with wrong signature
	tx4 = txn()
	tx4.add_input(pu1, 1)
	tx4.add_output(pu2, 1)
	tx4.sign(pr2)
	
	# Escrow Transaction not signed by the arbiter
	tx5 = txn()
	tx5.add_input(pu1, 1.2)
	tx5.add_output(pu2, 1.1)
	tx5.add_required(pu4)
	tx5.sign(pr1)
	
	# Two input addresses but signed only by one
	tx6 = txn()
	tx6.add_input(pu3, 1)
	tx6.add_input(pu4, 0.1)
	tx6.add_output(pu2, 1.1)
	tx6.sign(pr3)
	
	# Output exceeds the input : only for now but change this after implementing mining
	tx7 = txn()
	tx7.add_input(pu4, 1.2)
	tx7.add_output(pu2, 1)
	tx7.add_output(pu1, 2)
	tx7.sign(pr4) 
	
	# Negative amount 
	tx8 = txn()
	tx8.add_input(pu1, -1)
	tx8.add_output(pu2, -1)
	tx8.sign(pr1)
	
	# Modified Transaction 
	tx9 = txn()
	tx9.add_input(pu1, 1)
	tx9.add_output(pu2, 1)
	tx9.sign(pr1)
	tx9.outputs[0] = (pu3, 1)
	
			
	# Checking for Bad transactions 
	for t in [tx4 ,tx5, tx6, tx7, tx8, tx9]:
		if t.is_valid():
			print("Error! Bad Transaction couldn't detect.")
		else:
			print("Success! Bad Transaction detected")










