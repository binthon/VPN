from ipaddress import ip_address

class IPAllocator:
    def __init__(self, start_ip='100.20.10.2'):
        self.base_ip = ip_address(start_ip)
        self.allocated = {}
        self.last_ip = self.base_ip

    def assign(self, addr):
        if addr in self.allocated:
            return self.allocated[addr]
        self.last_ip = ip_address(int(self.last_ip) + 1)
        self.allocated[addr] = str(self.last_ip)
        return self.allocated[addr]

    def get_all_assignments(self):
        return self.allocated.copy()

    def release_ip(self, addr):
        if addr in self.allocated:
            del self.allocated[addr]
