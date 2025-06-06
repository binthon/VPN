from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding

def load_public_key(path='public.pem'):
    with open(path, 'rb') as f:
        return serialization.load_pem_public_key(f.read())

def rsa_encrypt(public_key, data: bytes):
    return public_key.encrypt(
        data,
        padding.OAEP(
            mgf=padding.MGF1(hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
