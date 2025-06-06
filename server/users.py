import json
import hashlib
import os

def load_users(filepath=None):
    if filepath is None:
        filepath = os.path.join(os.path.dirname(__file__), "users.json")
    with open(filepath, "r") as f:
        return json.load(f)

def check_pass(username, password, users):
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    print(f"[DEBUG] Hash użytkownika: {users.get(username)}", flush=True)
    print(f"[DEBUG] Obliczony hash z hasła: {password_hash}", flush=True)
    return users.get(username) == password_hash
