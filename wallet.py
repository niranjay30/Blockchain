#Wallet
import socket_utils
import transactions
import transaction_block
import pickle
import signatures


head_blocks = [None]
wallets = [('localhost',5006)]
miners = [('localhost',5005), ('localhost', 5007)]
miners = [('localhost',5005)]
break_now = False
verbose = True
my_public,my_private = signatures.generate_keys()
txn_index = {}

def thief(my_addr):
    my_ip, my_port = my_addr
    server = socket_utils.new_server_connection(my_ip,my_port)
    # Get Txs from wallets
    while not break_now:
        new_txn = socket_utils.recv_object(server)
        if isinstance(new_txn,transactions.txn):
            for ip,port in miners:
                if not (ip == my_ip and port == my_port):
                    socket_utils.send_object(ip,new_txn,port)


def stop_all():
    global break_now
    break_now = True


def wallet_server(my_addr):
    global head_blocks
    global txn_index
    try:
        head_blocks = transaction_block.load_blocks("AllBlocks.dat")
    except:
        print("WS:No previous blocks found. Starting fresh.")
        head_blocks = transaction_block.load_blocks("Genesis.dat")
    try:
        fp = open("txn_index.dat","rb")
        txn_index = pickle.load(fp)
        fp.close()
    except:
        txn_index = {}
    server = socket_utils.new_server_connection('localhost',5006)
    while not break_now:
        new_block = socket_utils.recv_object(server)
        if isinstance(new_block,transaction_block.txn_block):
            transaction_block.process_new_block(new_block, head_blocks, True)

    server.close()
    transaction_block.save_blocks(head_blocks,"AllBlocks.dat")
    fp = open("txn_index.dat", "wb")
    pickle.dump(txn_index, fp)
    fp.close()
    return True
        
def get_balance(pu_key):
    long_chain = transaction_block.find_longest_blockchain(head_blocks)
    return transaction_block.get_balance(pu_key,long_chain)


def send_coins(pu_send, amt_send, pr_send, pu_recv, amt_recv):
    global txn_index
    new_txn = transactions.txn()
    if not pu_send in txn_index:
        txn_index[pu_send] = 0
    new_txn.add_input(pu_send, amt_send, txn_index[pu_send])
    new_txn.add_output(pu_recv, amt_recv)
    new_txn.sign(pr_send)
    # Sending to all the miners
    for ip,port in miners:   
        socket_utils.send_object(ip,new_txn,port)
    txn_index[pu_send] = txn_index[pu_send] + 1
    return True

def load_keys(pr_file, pu_file):
    return signatures.load_private(pr_file), signatures.load_public(pu_file)


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
    t3.start()

    pr1,pu1 = load_keys("private.key","public.key")
    pr2,pu2 = signatures.generate_keys()
    pr3,pu3 = signatures.generate_keys()

    #Query balances
    bal1 = get_balance(pu1)
    print("Balance1: " + str(bal1))
    bal2 = get_balance(pu2)
    print("Balance1: " + str(bal2))
    bal3 = get_balance(pu3)
    print("Balance1: " + str(bal3))

    send_coins(pu1, 0.1, pr1, pu2, 0.1)
    send_coins(pu1, 0.1, pr1, pu2, 0.1)
    send_coins(pu1, 0.1, pr1, pu2, 0.1)
    send_coins(pu1, 0.1, pr1, pu2, 0.1)
    send_coins(pu1, 0.1, pr1, pu2, 0.1)
    send_coins(pu1, 0.1, pr1, pu2, 0.1)
    send_coins(pu1, 0.1, pr1, pu2, 0.1)
    send_coins(pu1, 0.1, pr1, pu2, 0.1)
    send_coins(pu1, 0.1, pr1, pu2, 0.1)
    send_coins(pu1, 0.1, pr1, pu2, 0.1)
    send_coins(pu1, 0.1, pr1, pu3, 0.03)
    send_coins(pu1, 0.1, pr1, pu3, 0.03)
    send_coins(pu1, 0.1, pr1, pu3, 0.03)
    send_coins(pu1, 0.1, pr1, pu3, 0.03)
    send_coins(pu1, 0.1, pr1, pu3, 0.03)
    send_coins(pu1, 0.1, pr1, pu3, 0.03)
    send_coins(pu1, 0.1, pr1, pu3, 0.03)
    send_coins(pu1, 0.1, pr1, pu3, 0.03)
    send_coins(pu1, 0.1, pr1, pu3, 0.03)
    send_coins(pu1, 0.1, pr1, pu3, 0.03)

    t2.start()
    time.sleep(60)

    #Save/Load all blocks
    transaction_block.save_blocks(head_blocks, "AllBlocks.dat")
    head_blocks = transaction_block.load_blocks("AllBlocks.dat")

    #Query balances
    new1 = get_balance(pu1)
    print("Balance1: " + str(new1))
    new2 = get_balance(pu2)
    print("Balance2: " + str(new2))
    new3 = get_balance(pu3)
    print("Balance3: " + str(new3))

    #Verify balances
    if abs(new1-bal1+2.0) > 0.00000001:
        print("Error! Wrong balance for pu1")
    else:
        print("Success. Good balance for pu1")
    if abs(new2-bal2-1.0) > 0.00000001:
        print("Error! Wrong balance for pu2")
    else:
        print("Success. Good balance for pu2")
    if abs(new3-bal3-0.3) > 0.00000001:
        print("Error! Wrong balance for pu3")
    else:
        print("Success. Good balance for pu3")

    #Thief will try to duplicate transactions
    miners.append(('localhost',5007))
    t4 = threading.Thread(target=thief, args=(('localhost',5007),))
    t4.start()
    send_coins(pu2, 0.2, pr2, pu1, 0.2)
    time.sleep(60)
    newnew1 = get_balance(pu1)
    print(newnew1)
    if abs(newnew1 - new1 - 0.2) > 0.000000001:
        print("Error! Duplicate transactions accepted.")
    else:
        print("Success! Duplicate transactions rejected.")

    miner.stop_all()
    
    num_heads = len(head_blocks)
    sister = transaction_block.txn_block(head_blocks[0].previous_block.previous_block)
    sister.previous_block = None
    socket_utils.send_object('localhost',sister,5006)
    time.sleep(10)
    if (len(head_blocks) == num_heads + 1):
        print ("Success! New head_block created")
    else:
        print("Error! Failed to add sister block")
        
    
    stop_all()
    
    t1.join()
    t2.join()
    t3.join()

    print ("Exit successful.")
                
    



