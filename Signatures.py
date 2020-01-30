#Signatures.py

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.exceptions import InvalidSignature


def generate_keys():
    private_key = rsa.generate_private_key(
        public_exponent = 65537,
        key_size = 2048,
        backend = default_backend()
    )
    public_key = private_key.public_key()
    return private_key, public_key


def signature(message, private_key):
    message = bytes(str(message), 'utf-8')
    sign = private_key.sign(
            message,
            padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    return sign


def verify(message, signature, public_key):
    message = bytes(str(message), 'utf-8')
    try:
        public_key.verify(
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
    # Testing the general idea of generating keys, generating signature and verification
    pr, pu = generate_keys()
    print(pr)
    print(pu)
    
    message = "This is a secret message"
    
    sign = signature(message, pr)
    print(sign)
    
    validity = verify(message, sign, pu)

    if validity:
        print("Cool! Verified Signature.")
    else:
        print("Error! Bad Signature.")

    # Testing message copying i.e., someone pretending to be you
    pr2, pu2 = generate_keys()

    sig2 = signature(message, pr2)

    validity = verify(message, sig2, pu)

    if validity:
        print("Sorry! We've failed!")
    else:
        print("Success! Message copying identified")

    # Testing message tampering i.e., someone trying to be change the message that you sent
    tampered_message = message + "N"
    validity = verify(tampered_message, sig2, pu)

    if validity:
        print("Sorry! The tamperer has been successful.")
    else:
        print("Success! Message tampering detected.")
