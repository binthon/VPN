import os
import fcntl
import struct
import subprocess

TUNSETIFF = 0x400454ca
IFF_TUN   = 0x0001
IFF_NO_PI = 0x1000

class TunInterface:
    def __init__(self, name='tun0', ip=None):
        self.name = name
        self.fd = self._create_tun(name)
        if ip:
            self.configure_interface(ip)

    def _create_tun(self, name):
        tun = os.open('/dev/net/tun', os.O_RDWR)
        ifr = struct.pack('16sH', name.encode(), IFF_TUN | IFF_NO_PI)
        fcntl.ioctl(tun, TUNSETIFF, ifr)
        return tun

    def configure_interface(self, ip):
        subprocess.run(['ip', 'addr', 'add', ip, 'dev', self.name])
        subprocess.run(['ip', 'link', 'set', self.name, 'up'])

    def read(self, size=2048):
        return os.read(self.fd, size)

    def write(self, data):
        os.write(self.fd, data)

    def fileno(self):
        return self.fd

    def close(self):
        os.close(self.fd)
