# Client

import signatures
import transactions
import transaction_block
import pickle
import socket


tcp_port = 5005

def send_object(ip_address, obj):
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((ip_address, tcp_port))
	data = pickle.dumps(obj)
	s.send(data)
	s.close()
	return False
	
	
if __name__ == "__main__":
	pr1, pu1 = signatures.generate_keys()
	pr2, pu2 = signatures.generate_keys()
	pr3, pu3 = signatures.generate_keys()
	
	tx1 = transactions.txn()
	tx1.add_input(pu1, 2.3)
	tx1.add_output(pu2, 1.0)
	tx1.add_output(pu3, 1.1)
	tx1.sign(pr1)
	
	tx2 = transactions.txn()
	tx2.add_input(pu3, 2.3)
	tx2.add_input(pu2, 1.0)
	tx2.add_output(pu1, 3.1)
	tx2.sign(pr2)
	tx2.sign(pr3)
	
	B1 = transaction_block.txn_block(None)
	B1.add_txn(tx1)
	B1.add_txn(tx2)
	
	send_object('localhost', B1)
	send_object('localhost', tx2)
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	