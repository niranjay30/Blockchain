# Second Miner

import threading
import miner
import signatures
import time
import transaction_block

my_ip = 'localhost'

wallets=[(my_ip, 5005),(my_ip, 5006)]

my_pr, my_pu = signatures.load_keys("private.key","public.key")
t1 = threading.Thread(target=miner.miner_server, args=(('localhost',5007),))
t2 = threading.Thread(target=miner.nonce_finder, args=(wallets, my_pu))
t1.start()
t2.start()
time.sleep(25)
miner.stop_all()
t1.join()
t2.join()


print(ord(transaction_block.find_longest_blockchain(miner.head_blocks).previous_block.previous_block.nonce[0]))

print(ord(transaction_block.find_longest_blockchain(miner.head_blocks).previous_block.nonce[0]))

print(ord(transaction_block.find_longest_blockchain(miner.head_blocks).nonce[0]))













