import os
import fcntl
import struct
import subprocess

TUNSETIFF = 0x400454ca
IFF_TUN   = 0x0001
IFF_NO_PI = 0x1000

class TunInterface:
    def __init__(self, name=None, ip=None):
        self.name = name
        self.fd = self._create_tun(name)
        if ip:
            self.configure_interface(ip)

    def _create_tun(self, name=None):
        tun = os.open('/dev/net/tun', os.O_RDWR)

        if name is not None:
            ifr = struct.pack('16sH', name.encode(), IFF_TUN | IFF_NO_PI)
            fcntl.ioctl(tun, TUNSETIFF, ifr)
            self.name = name
            return tun

        for i in range(256):
            try_name = f"tun{i}"
            try:
                ifr = struct.pack('16sH', try_name.encode(), IFF_TUN | IFF_NO_PI)
                fcntl.ioctl(tun, TUNSETIFF, ifr)
                self.name = try_name
                print(f"Przydzielono interfejs TUN: {self.name}", flush=True)
                return tun
            except OSError:
                continue

        raise RuntimeError("Nie udało się przydzielić interfejsu TUN (tun0–tun255)")

    def configure_interface(self, ip):
        subprocess.run(['ip', 'addr', 'add', ip, 'dev', self.name], check=True)
        subprocess.run(['ip', 'link', 'set', self.name, 'up'], check=True)

    def read(self, size=2048):
        return os.read(self.fd, size)

    def write(self, data):
        os.write(self.fd, data)

    def fileno(self):
        return self.fd

    def close(self):
        os.close(self.fd)
