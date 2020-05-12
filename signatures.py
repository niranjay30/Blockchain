#Signatures.py
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization

def generate_keys():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )    
    public_key = private_key.public_key()
    # Serialization of public_key 
    public_key_ser = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )    
    return private_key, public_key_ser
    

def sign(message, private_key):
    message = bytes(str(message), 'utf-8')
    signature = private_key.sign(
        message,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    return signature 
    

def verify(message, signature, public_key_ser):
	# Unserialization of public_key 
    public = serialization.load_pem_public_key(
        public_key_ser,
        backend=default_backend()
    )
    
    message = bytes(str(message), 'utf-8')
    try:
        public.verify(
            signature,
            message,
            padding.PSS(
              mgf=padding.MGF1(hashes.SHA256()),
              salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return True
    except InvalidSignature:
        return False
    except:
        print("Error executing public_key.verify")
        return False
        
        
def save_private(pr_key, filename):
    pem = pr_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    )
    fp = open(filename, "wb")
    fp.write(pem)
    fp.close()
    return
    
   
def load_private(filename):
    fin = open(filename, "rb")
    pr_key = serialization.load_pem_private_key(
        fin.read(),
        password=None,
        backend=default_backend()
    )
    fin.close()
    return pr_key
    

def save_public(pu_key, filename):
    fp = open(filename, "wb")
    fp.write(pu_key)
    fp.close()
    return True
    

def load_public(filename):
    fin = open(filename, "rb")
    pu_key = fin.read()
    fin.close()
    return pu_key
    

if __name__ == '__main__':
    pr, pu = generate_keys()
    #print(pr)
    #print(pu)
    message = "This is a secret message"
    sig = sign(message, pr)
    #print(sig)
    correct = verify(message, sig, pu)
    #print(correct)

    if correct:
        print("Success! Signature is valid.")
    else:
        print ("Error! Signature is invalid.")

    pr2, pu2 = generate_keys()

    sig2 = sign(message, pr2)

    correct= verify(message, sig2, pu)
    if correct:
        print("Error! Bad signature not detected.")
    else:
        print("Success! Bad signature detected.")

    badmess = message + "Q"
    correct= verify(badmess, sig, pu)
    if correct:
        print("Error! Tampering not detected.")
    else:
        print("Success! Tampering detected")
    
    
    save_private(pr2, "private.key")
    pr_load = load_private("private.key")
    sig3 = sign(message, pr_load)
    correct = verify(message, sig3, pu2)
    
    if correct:
        print("Success! Loaded private key is good.")
    else:
        print ("Error! Loaded private key is bad.")

    save_public(pu2, "public.key")
    pu_load = load_public("public.key")
    correct = verify(message, sig3, pu_load)
    
    if correct:
        print("Success! Loaded public key is good.")
    else:
        print ("Error! Loaded public key is bad.")
    
        
    

