import socket
import select
from struct import unpack
from tun import TunInterface
from aes import encrypt, decrypt
from users import load_users, check_pass
from rsa_gen import load_private_key, rsa_decrypt
from check_ip import IPAllocator

manager_ip = IPAllocator()

LISTEN_IP = '0.0.0.0'
LISTEN_PORT = 5555

users = load_users()
private_key = load_private_key()

authenticated_clients = set()
aes_initialized = {}
client_tun_queue = {}

tun = TunInterface(None, ip='100.20.10.1/24')
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((LISTEN_IP, LISTEN_PORT))

print("VPN serwer nasłuchuje...")

def is_allowed_packet(packet):
    if len(packet) < 20:
        return False  

    version = packet[0] >> 4
    if version != 4:
        return False 

    protocol = packet[9]
    ip_header_len = (packet[0] & 0x0F) * 4

    if protocol == 1:
        return True

    elif protocol == 6: 
        if len(packet) < ip_header_len + 4:
            return False
        dst_port = unpack('!H', packet[ip_header_len+2:ip_header_len+4])[0]
        return dst_port in (80, 3306,1080)

    return False

while True:
    r, _, _ = select.select([tun.fileno(), sock.fileno()], [], [])

    if sock.fileno() in r:
        data, addr = sock.recvfrom(4096)
        print(f"[DEBUG] Odebrano od {addr}: {data!r}", flush=True)

        if addr not in authenticated_clients:
            try:
                credentials = data.decode()
                print(f"[DEBUG] Odczytano login dane: {credentials!r}", flush=True)
                username, password = credentials.strip().split(":", 1)
                print(f"Próba logowania: {username} / {password} od {addr}",flush=True)
                if check_pass(username, password, users):
                    authenticated_clients.add(addr)
                    assigned_ip = manager_ip.assign(addr)
                    sock.sendto(f"OK:{assigned_ip}".encode(), addr)
                    print(f"Zalogowano użytkownika {username} z {addr}, przypisano IP {assigned_ip}",flush=True)
                else:
                    sock.sendto(b'ERROR', addr)
                    print(f"Błąd logowania od {addr}",flush=True)
            except Exception as e:
                print(f"[EXCEPTION] Wystąpił błąd: {e}", flush=True)
                sock.sendto(b'ERROR', addr)
            continue

        if addr in authenticated_clients and addr not in aes_initialized:
            try:
                aes_key = rsa_decrypt(private_key, data)
                aes_initialized[addr] = aes_key 
                client_tun_queue[addr] = []
                print(f"Odebrano i ustawiono klucz AES od {addr}")
            except Exception as e:
                print(f"Błąd przy dekodowaniu klucza AES od {addr}: {e}")
            continue


        try:
            packet = decrypt(data, key=aes_initialized[addr])
            if is_allowed_packet(packet):
                tun.write(packet)
            else:
                print("Zablokowano pakiet: niedozwolony port lub protokół",flush=True)
        except Exception as e:
            print(f"Błąd przy deszyfrowaniu pakietu od {addr}: {e}",flush=True)

    if tun.fileno() in r:
        packet = tun.read()
        for addr in authenticated_clients:
            if addr in aes_initialized:
                try:
                    encrypted_packet = encrypt(packet, key=aes_initialized[addr])
                    sock.sendto(encrypted_packet, addr)
                except Exception as e:
                    print(f"Błąd przy wysyłaniu pakietu do {addr}: {e}",flush=True)
