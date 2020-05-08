# Server

import transaction_block
import socket
import pickle


tcp_port = 5005
buffer_size = 1024


def new_connection(ip_address):
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.bind((ip_address, tcp_port))
	s.listen()
	return s
	
	
def recv_object(s):
	new_sock, address = s.accept()
	all_data = b''
	while True:
		data = new_sock.recv(buffer_size)
		if not data: break
		all_data = all_data + data
	return pickle.loads(all_data)

	
if __name__ == "__main__":
	s = new_connection('127.0.0.1')
	new_blk = recv_object(s)
	print(new_blk.data[0])
	print(new_blk.data[1])

	if new_blk.is_valid():
		print("Success! Transaction is valid.")
	else:
		print("Error! Transaction is invalid.")
		
	if new_blk.data[0].inputs[0][1] == 2.3:
		print("Success! Input value matches.")
	else:
		print("Error! Wrong input value for block B1, tx1")
		
	if new_blk.data[0].outputs[1][1] == 1.1:
		print("Success! Output value matches.")
	else:
		print("Error! Wrong output value for block B1, tx1")
	
	if new_blk.data[1].inputs[0][1] == 2.3:
		print ("Success! Input value matches")
	else:
		print ("Error! Wrong input value for block B1, tx2")
	if new_blk.data[1].inputs[1][1] == 1.0:
		print ("Success! Input value matches")
	else:
		print ("Error! Wrong input value for block B1, tx2")
        	
	if new_blk.data[1].outputs[0][1] == 3.1:
		print("Success! Output value matches.")
	else:
		print("Error! Wrong output value for block B1, tx2")


	new_txn = recv_object(s)
	print(new_txn)



















