import json
import hashlib
def load_users(filepath='users.json'):
    with open(filepath, 'r') as f:
        return json.load(f)

def check_pass(username, password, users):
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    return users.get(username) == password_hash