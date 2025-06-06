import socket
import select
from tun import TunInterface
from aes import encrypt, decrypt, set_key, generate_key
from rsa_gen import load_public_key, rsa_encrypt
import getpass

SERVER_IP = '192.168.1.30'
SERVER_PORT = 5555

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


username = input("Login: ")
password = getpass.getpass("Hasło: ")
credentials = f"{username}:{password}".encode()
sock.sendto(credentials, (SERVER_IP, SERVER_PORT))

resp, _ = sock.recvfrom(1024)
if not resp.startswith(b'OK:'):
    print("Logowanie nieudane")
    exit(1)


assigned_ip = resp.decode().split(':', 1)[1].strip()
print(f"Zalogowano – przypisany adres IP: {assigned_ip}")

tun = TunInterface('tun0', ip=f"{assigned_ip}/24")

print("Wysyłam klucz AES do serwera...")
aes_key = generate_key()
set_key(aes_key)

public_key = load_public_key('public.pem')
encrypted_aes_key = rsa_encrypt(public_key, aes_key)
sock.sendto(encrypted_aes_key, (SERVER_IP, SERVER_PORT))

print("Klucz AES wysłany – tunel aktywny")


while True:
    r, _, _ = select.select([tun.fileno(), sock.fileno()], [], [])

    if tun.fileno() in r:
        packet = tun.read()
        encrypted_packet = encrypt(packet)
        sock.sendto(encrypted_packet, (SERVER_IP, SERVER_PORT))

    if sock.fileno() in r:
        encrypted_data, _ = sock.recvfrom(2048)
        packet = decrypt(encrypted_data)
        tun.write(packet)
