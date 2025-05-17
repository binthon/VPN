from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding

def load_private_key(path='private.pem'):
    with open(path, 'rb') as f:
        return serialization.load_pem_private_key(f.read(), password=None)

def rsa_decrypt(private_key, encrypted_data: bytes):
    return private_key.decrypt(
        encrypted_data,
        padding.OAEP(
            mgf=padding.MGF1(hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
