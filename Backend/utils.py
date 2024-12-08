import psutil
import socket
import ipaddress


def get_active_interface():
    interfaces = psutil.net_if_addrs()
    for interface, addresses in interfaces.items():
        for addr in addresses:
            if addr.family == socket.AF_INET and addr.address != "127.0.0.1":
                return interface
    return None


class NetworkUtils:
    def __init__(self):
        self.my_network_ip, self.subnet_mask = self.get_local_ip_and_subnet()

    def is_local_ip(self, ip):
        """Check if a given IP address is in the same network as the local IP."""
        network = ipaddress.ip_network(
            f"{self.my_network_ip}/{self.subnet_mask}", strict=False
        )
        ip_obj = ipaddress.ip_address(ip)
        return ip_obj in network

    def get_local_ip_and_subnet(self):
        """Retrieve the local IP address and subnet mask of the active network interface."""
        for interface, addrs in psutil.net_if_addrs().items():
            for addr in addrs:
                if addr.family == socket.AF_INET and addr.address != "127.0.0.1":
                    return addr.address, addr.netmask
        raise RuntimeError("No active network interface found with an IPv4 address.")
