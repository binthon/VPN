from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os

KEY = None 

def set_key(new_key: bytes):
    global KEY
    KEY = new_key

def encrypt(data):
    if KEY is None:
        raise ValueError("AES KEY is not set.")
    iv = os.urandom(16)
    cipher = Cipher(algorithms.AES(KEY), modes.CFB(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    ct = encryptor.update(data) + encryptor.finalize()
    return iv + ct

def decrypt(encrypted_data):
    if KEY is None:
        raise ValueError("AES KEY is not set.")
    iv = encrypted_data[:16]
    ct = encrypted_data[16:]
    cipher = Cipher(algorithms.AES(KEY), modes.CFB(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    return decryptor.update(ct) + decryptor.finalize()
