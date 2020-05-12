# Wallet

import socket_utils
import transactions
import transaction_block
import pickle

head_blocks = [None]
wallets = [('localhost', 5006)]
miners = [('localhost',5005)]
break_now = False
verbose = True

		
def stop_all():
	global break_now
	break_now = True
				

def wallet_server(my_address):
	global head_blocks
	head_blocks = [None]
	server = socket_utils.new_server_connection('localhost', 5006)
	while not break_now:
		new_block = socket_utils.recv_object(server)
		if isinstance(new_block, transaction_block.txn_block):
			if verbose:print("Received a block")
			# Add block to the blockchain
			for b in head_blocks:
				if b == None:
					if new_block.previous_hash == None:
						new_block.previous_block = b
						if not new_block.is_valid():
							print("Error! new_block is not valid")
						else:
							head_blocks.remove(b)
							head_blocks.append(new_block)
							if verbose:print("Added to head_blocks.")
				elif new_block.previous_hash == b.compute_hash():
					new_block.previous_block = b
					if not new_block.is_valid():
						print("Error! new_block is not valid")
					else:
						head_blocks.remove(b)
						head_blocks.append(new_block)
						if verbose:print("Added to head_blocks.")
	server.close()
	return True
			
		
def get_balance(pu_key):
	long_chain = transaction_block.find_longest_blockchain(head_blocks)
	this_block = long_chain
	bal = 0.0
	while this_block != None:
		for txn in this_block.data:
			for addr, amt in txn.inputs:
				if addr == pu_key:
					bal = bal - amt
			for addr, amt in txn.outputs:
				if addr == pu_key:
					bal = bal + amt
		this_block = this_block.previous_block
	return bal


def send_coins (pu_send, amt_send, pr_send, pu_recv, amt_recv, miner_list):
	new_txn = transactions.txn()
	new_txn.add_input(pu_send, amt_send)
	new_txn.add_output(pu_recv, amt_recv)
	new_txn.sign(pr_send)
	socket_utils.send_object('localhost', new_txn)	
	return True
	
	
def load_keys(pr_file, pu_file):
	return signatures.load_private(pr_file), signatures.load_public(pu_file)
	
	
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

		
if __name__ == "__main__":
	
	import time
	import miner
	import threading
	import signatures
	
	miner_pr, miner_pu = signatures.generate_keys()
	t1 = threading.Thread(target=miner.miner_server, args=(('localhost',5005),))
	t2 = threading.Thread(target=miner.nonce_finder, args=(wallets, miner_pu))
	t3 = threading.Thread(target=wallet_server, args=(('localhost',5006),))
	
	t1.start()
	t2.start()
	t3.start()
	
	pr1, pu1 = load_keys("private.key", "public.key")
	pr2, pu2 = signatures.generate_keys()
	pr3, pu3 = signatures.generate_keys()
	
	# Query Balance
	bal1 = get_balance(pu1)
	print("Balance 1 = " + str(bal1))
	bal2 = get_balance(pu2)
	print("Balance 2 = " + str(bal2))
	bal3 = get_balance(pu3)
	print("Balance 3 = " + str(bal3))

	# Send coins
	send_coins(pu1, 1.0, pr1, pu2, 1.0, miners)
	send_coins(pu1, 1.0, pr1, pu3, 0.8, miners)
	
	# a little buffer time to let the process complete
	time.sleep(30)
	
	# Save and Load all blocks
	save_blocks(head_blocks, "allBlocks.dat")
	head_blocks = load_blocks("allBlocks.dat")

	# Again query balance
	new_bal1 = get_balance(pu1)
	print("Balance 1 = " + str(new_bal1))
	new_bal2 = get_balance(pu2)
	print("Balance 2 = " + str(new_bal2))
	new_bal3 = get_balance(pu3)
	print("Balance 3 = " + str(new_bal3))
	
	# Verify balance
	if abs(new_bal1 - bal1 + 2.0) > 0.000000001:
		print("Error! Wrong balance for pu1.")
	else:
		print("Success! Good balance for pu1.")
	
	if abs(new_bal2 - bal2 - 1.0) > 0.000000001:
		print("Error! Wrong balance for pu2.")
	else:
		print("Success! Good balance for pu2.")
		
	if abs(new_bal3 - bal3 - 0.8) > 0.000000001:
		print("Error! Wrong balance for pu3.")
	else:
		print("Success! Good balance for pu3.")
	
	
	miner.stop_all()
	stop_all()
	
	t1.join()
	t2.join()
	t3.join()
	
	print("Exit successful.")



















