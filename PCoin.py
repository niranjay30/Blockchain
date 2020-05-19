# PCoin

import time
import wallet
import miner
import threading
import signatures
import transaction_block

wallets = []
miners = []
my_ip = "localhost"
wallets.append((my_ip, 5006))
wallets.append((my_ip, 5007))
miners.append((my_ip, 5005))

tms = None
tnf = None
tws = None

def start_miner ():
	global tms, tnf
	try:
		my_pu = signatures.load_public("public.key")
	except:
		print("No public.key Need to generate?")
		pass
	tms = threading.Thread(target=miner.miner_server, args=((my_ip,5005),))
	tnf = threading.Thread(target=miner.nonce_finder, args=(wallets, my_pu))
	
	tms.start()
	tnf.start()
	return True
	

def start_wallet ():
	global tws
	wallet.my_private, wallet.my_public = signatures.load_keys("private.key","public.key")
	
	tws = threading.Thread(target=wallet.wallet_server, args=((my_ip,5006),))
	tws.start()
	return True
	
	
def stop_miner ():
	global tms, tnf
	miner.stop_all()
	if tms: tms.join()
	if tnf: tnf.join()
	tms = None
	tnf = None
	return True
	
	
def stop_wallet ():
	global tws
	wallet.stop_all()
	if tws: tws.join()
	tws = None
	return True
	

def get_balance (pu_key):
	if not tws:
		print("Start the server by calling start_wallet before checking balances.")
		return 0.0
	return wallet.get_balance(pu_key)
	

def send_coins (pu_recv, amt, txn_fee):
	wallet.send_coins(wallet.my_public, amt+txn_fee, wallet.my_private, pu_recv, amt)
	return True


def make_new_keys ():
	wallet.my_private, wallet.my_public = signatures.generate_keys()
	signatures.save_public(wallet.my_public, "public.key")
	signatures.save_private(wallet.my_private, "private.key")
	return None

if __name__ == "__main__":
	
	start_miner()
	start_wallet()
	
	other_public = b'-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAyktcnjtvqhAzXmfayJRX\nzXGDbeLLTOAchcCi6oo9Kirn24UasNdqUlY8uUIiEavVa+3Ih8qEMEtK68qF2Ngp\nafTCAR/uy0qyJu+VZD6uNGmA3dJKFsmMBspgCjbQChjZawXDLnN30y+VbzQX2x+U\nza30swLyuvMZgoMS9x9QSISQAg5v5HBuNiI8qBSAtASFgXR07QFcR41R3wWLqqSA\nvwEgKczPi5Ms2DTKDgouMnpUdbE3e+QCGIjXSiNL7dhdaJqSxlUT8yBVqZA4LrrV\nctM3o6gY6SkfKCg8yKBEGEPvmP1rIAhfdQKW9KHLncrwXdLGcLki5b7P6m9grGp4\nLQIDAQAB\n-----END PUBLIC KEY-----\n'
	
	time.sleep(2)
	print (get_balance(wallet.my_public))
	
	send_coins (other_public, 1.0 , 0.001)

	time.sleep(20)

	print(get_balance(other_public))
	print (get_balance(wallet.my_public))
	
	time.sleep(1)
	
	stop_wallet()
	stop_miner()
	
	
	print(ord(transaction_block.find_longest_blockchain(miner.head_blocks).previous_block.previous_block.nonce[0]))

	print(ord(transaction_block.find_longest_blockchain(miner.head_blocks).previous_block.nonce[0]))

	print(ord(transaction_block.find_longest_blockchain(miner.head_blocks).nonce[0]))




	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	