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
    
    
    
        
    

