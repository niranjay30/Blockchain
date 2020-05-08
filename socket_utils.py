# Socket Utilities

import socket
import pickle
import select

tcp_port = 5005
buffer_size = 1024


def new_server_connection(ip_address, port = tcp_port):
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.bind((ip_address, port))
	s.listen()
	return s
	

def send_object(ip_address, obj, port = tcp_port):
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((ip_address, port))
	data = pickle.dumps(obj)
	s.send(data)
	s.close()
	return False
	

def recv_object(socket):
	inputs, outputs, errors = select.select([socket],[],[socket],6)
	if socket in inputs:
		new_sock, address = socket.accept()
		all_data = b''
		while True:
			data = new_sock.recv(buffer_size)
			if not data: break
			all_data = all_data + data
		return pickle.loads(all_data)
	return None


if __name__ == "__main__":
	server = new_server_connection('localhost')
	o = recv_object(server)
	print("Success!")	# If returns after time then successful.
#	print(o)
	server.close()

















