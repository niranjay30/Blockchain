# Miner

import socket_utils
import transactions
import transaction_block
import pickle

wallets = [("localhost", 5006)]
txn_list = []
head_blocks = [None]
break_now = False
verbose = True


def stop_all():
	global break_now
	break_now = True


def miner_server(my_address):
	global txn_list
	global break_now
	my_ip, my_port = my_address
	server = socket_utils.new_server_connection(my_ip, my_port)
	# Get transactions from wallets
	while not break_now:
		new_txn = socket_utils.recv_object(server)
		if isinstance(new_txn, transactions.txn):
			txn_list.append(new_txn)
			if verbose:
				print("Received transaction!")
		#if len(txn_list) >= 2:
		#	break
	
	
def nonce_finder(wallet_list, miner_public):
	global break_now
	# Add those transactions into a new block
	while not break_now:	
		new_block = transaction_block.txn_block(transaction_block.find_longest_blockchain(head_blocks))
		for txn in txn_list:
			new_block.add_txn(txn)
			#new_block.add_txn(txn_list[1])
	
		# Compute and add mining reward
		total_in, total_out = new_block.count_totals()
		mine_reward = transactions.txn()
		mine_reward.add_output(miner_public, 25 + (total_in - total_out))
		new_block.add_txn(mine_reward)
		
		# Find the nonce
		if verbose:
			print("Finding nonce...")
		new_block.find_nonce(10000)	
			
		if new_block.good_nonce():
			if verbose:
				print("Good nonce found!")
			head_blocks.remove(new_block.previous_block)	
			head_blocks.append(new_block)
		
			# Send new block
			save_previous = new_block.previous_block
			new_block.previous_block = None
			for ip_addr, port in wallet_list:
				if verbose:
					print("Sending to " + ip_addr + ":" + str(port))
				socket_utils.send_object(ip_addr,new_block,5006)
			new_block.previous_block = save_previous
			for txn in new_block.data:
				if txn != mine_reward:
					txn_list.remove(txn)
	return True

		
def save_txn_list(the_list, filename):
	fp = open(filename, "wb")
	pickle.dump(the_list, fp)
	fp.close()
	return True

		
def load_txn_list(filename):
	fin = open(filename, "rb")
	ret = pickle.load(fin)
	fin.close()
	return ret
    
		
if __name__ == "__main__":
	
	import signatures
	import threading
	import time
	
	my_pr, my_pu = signatures.generate_keys()
	t1 = threading.Thread(target=miner_server, args=(('localhost',5005),))
	t2 = threading.Thread(target=nonce_finder, args=(wallets, my_pu))

	server = socket_utils.new_server_connection('localhost', 5006)
	
	t1.start()
	t2.start()
	
	pr1,pu1 = signatures.generate_keys()
	pr2,pu2 = signatures.generate_keys()
	pr3,pu3 = signatures.generate_keys()
	
	tx1 = transactions.txn()
	tx2 = transactions.txn()
	
	tx1.add_input(pu1, 4.0)
	tx1.add_input(pu2, 1.0)
	tx1.add_output(pu3, 4.8)
	tx2.add_input(pu3, 4.0)
	tx2.add_output(pu2, 4.0)
	tx2.add_required(pu1)
	
	tx1.sign(pr1)
	tx1.sign(pr2)
	tx2.sign(pr3)
	tx2.sign(pr1)
	
	#print(tx1.is_valid())
	#print(tx2.is_valid())
	
	new_tx_list = [tx1, tx2]
	save_txn_list(new_tx_list, "txns.dat")
	new_new_txn_list = load_txn_list("txns.dat")
    
	for txn in new_new_txn_list:	
		try:
			socket_utils.send_object('localhost', txn)
			print("Transaction sent.")
		except:
			print("Error! Connection unsuccessful")
	

	for i in range(40):
		new_block = socket_utils.recv_object(server)
		if new_block:
			break		
	
	if new_block.is_valid():
		print("Success! Block is valid.")
	if new_block.good_nonce():
		print("Success! Nonce is valid.")
	
	for txn in new_block.data:
		try:
			if txn.inputs[0][0] == pu1 and txn.inputs[0][1] == 4.0:
				print("tx1 is present")
		except:
			pass
		try:
			if txn.inputs[0][0] == pu3 and txn.inputs[0][1] == 4.0:
				print("tx2 is present")
		except:
			pass
			
	time.sleep(20)
	break_now = True
	time.sleep(2)
	server.close()
	
	t1.join()
	t2.join()
	
	print("Done!")
	
	



























	