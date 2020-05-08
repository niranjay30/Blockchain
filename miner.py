# Miner

import socket_utils
import transactions
import transaction_block
import signatures

wallets = ["localhost"]
txn_list = []
head_blocks[None]

def find_longest_blockchain():
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


def miner_server(my_ip, wallet_list, my_public):
	server = socket_utils.new_server_connection(my_ip)
	# Get 2 transactions from wallets
	for i in range(10):
		new_txn = socket_utils.recv_object(server)
		if isinstance(new_txn, transactions.txn):
			txn_list.append(new_txn)
			print("Received transaction!")
		if len(txn_list) >= 2:
			break
	
	# Add those transactions into a new block	
	new_block = transaction_block.txn_block(find_longest_blockchain())
	new_block.add_txn(txn_list[0])
	new_block.add_txn(txn_list[1])
	
	# Compute and add mining reward
	total_in, total_out = new_block.count_totals()
	mine_reward = transactions.txn()
	mine_reward.add_output(my_public, 25 + (total_in - total_out))
	new_block.add_txn(mine_reward)
	
	# Find the nonce
	for i in range(10):
		print("Finding nonce...")
		new_block.find_nonce()
		if new_block.good_nonce():
			print("Good nonce found!")
			break
	
	if not new_block.good_nonce():
		print("Error! Couldn't find nonce.")
		return False
	# Send new block
	for ip_addr in wallet_list:
		print("Sending to " + ip_addr)
		socket_utils.send_object(ip_addr,new_block,5006)
	head_blocks.remove(new_block.previous_block)
	head_blocks.append(new_block)
	return False
		
		
my_pr, my_pu = signatures.generate_keys()
miner_server('localhost', wallets, my_pu)
	
	



























	