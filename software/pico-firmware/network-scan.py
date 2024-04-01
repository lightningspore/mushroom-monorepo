import ipaddress
import socket

def scan_network(cidr, port=6969):
    # Generate list of IP addresses from the CIDR range
    network = ipaddress.ip_network(cidr)
    for ip in network.hosts():  # .hosts() excludes network and broadcast addresses
        try:
            # Attempt to connect to the specified port
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)  # Timeout for the connection attempt
                if s.connect_ex((str(ip), port)) == 0:
                    print(f"Webserver found at {ip}:{port}")
        except Exception as e:
            print(f"Error scanning {ip}:{port} - {e}")

# Start Scan
scan_network("192.168.1.0/24")  # Replace with your CIDR range