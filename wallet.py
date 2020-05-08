# Wallet

import socket_utils
import transactions
import signatures

head_blocks = [None]

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

try:
	socket_utils.send_object('localhost', tx1)
	print("Sent tx1.")
	socket_utils.send_object('localhost', tx2)
	print("Sent tx2.")
except:
	print("Error! Connection unsuccessful")

server = socket_utils.new_server_connection('localhost', 5006)
for i in range(40):
	new_block = socket_utils.recv_object(server)
	if new_block:
		break
server.close()
		

if new_block.is_valid():
	print("Success! Block is valid.")
if new_block.good_nonce():
	print("Success! Nonce is valid.")

for txn in new_block.data:
	if txn.inputs[0][0] == pu1 and txn.inputs[0][1] == 4.0:
		print("tx1 is present")
	if txn.inputs[0][0] == pu3 and txn.inputs[0][1] == 4.0:
		print("tx2 is present")
		
# Add block to the bblockchain
for b in head_blocks():
	if new_block.previous_hash = b.compute_hash():
		new_block.previous_block = b
		head_blocks.remove(b)
		head_blocks.append(new_block)




















