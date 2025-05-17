import socket
import threading

ALLOWED_PORTS = {3306}

def handle_client(client_socket):
    try:
 
        header = client_socket.recv(2)
        if len(header) < 2 or header[0] != 5:
            raise ValueError("Nieprawidłowy handshake SOCKS5")
        n_methods = header[1]
        client_socket.recv(n_methods)
        client_socket.sendall(b"\x05\x00")  

   
        req = client_socket.recv(4)
        if len(req) < 4 or req[1] != 1:
            raise ValueError("Nieprawidłowy request lub nie CONNECT")

        addr_type = req[3]


        if addr_type == 1:  
            addr = socket.inet_ntoa(client_socket.recv(4))
        elif addr_type == 3:  
            length = client_socket.recv(1)[0]
            addr = client_socket.recv(length).decode()
        elif addr_type == 4:  
            addr = socket.inet_ntop(socket.AF_INET6, client_socket.recv(16))
        else:
            raise ValueError(f"Nieobsługiwany typ adresu: {addr_type}")

        port_bytes = client_socket.recv(2)
        if len(port_bytes) < 2:
            raise ValueError("Brak portu")
        port = int.from_bytes(port_bytes, 'big')

        if port not in ALLOWED_PORTS:
            print(f"❌ SOCKS5: Odrzucono dostęp do {addr}:{port}")
            client_socket.close()
            return

        remote = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        remote.connect((addr, port))
        client_socket.sendall(
            b"\x05\x00\x00\x01" + socket.inet_aton("0.0.0.0") + b"\x00\x00"
        )

        print(f"✅ SOCKS5: Połączono z {addr}:{port}")

        def forward(src, dst):
            try:
                while True:
                    data = src.recv(4096)
                    if not data:
                        break
                    dst.sendall(data)
            except:
                pass
            src.close()
            dst.close()

        threading.Thread(target=forward, args=(client_socket, remote), daemon=True).start()
        threading.Thread(target=forward, args=(remote, client_socket), daemon=True).start()

    except Exception as e:
        print(f"⚠️ Błąd SOCKS5: {e}")
        client_socket.close()



def main():
    bind_ip = "100.20.10.1"
    bind_port = 1080

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((bind_ip, bind_port))
    server.listen(5)
    print(f"SOCKS5 działa na {bind_ip}:{bind_port}")

    while True:
        client, _ = server.accept()
        threading.Thread(target=handle_client, args=(client,), daemon=True).start()

if __name__ == "__main__":
    main()
