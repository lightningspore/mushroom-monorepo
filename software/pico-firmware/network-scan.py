import ipaddress
import socket

# def scan_network(cidr, port=6969):
#     # Generate list of IP addresses from the CIDR range
#     network = ipaddress.ip_network(cidr)
#     for ip in network.hosts():  # .hosts() excludes network and broadcast addresses
#         try:
#             # Attempt to connect to the specified port
#             with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
#                 s.settimeout(1)  # Timeout for the connection attempt
#                 if s.connect_ex((str(ip), port)) == 0:
#                     print(f"Webserver found at {ip}:{port}")
#         except Exception as e:
#             print(f"Error scanning {ip}:{port} - {e}")

# # Start Scan
# scan_network("192.168.1.0/24")  # Replace with your CIDR range



import asyncio

async def scan_network_parallel(cidr, port=6969):
    # Generate list of IP addresses from the CIDR range
    network = ipaddress.ip_network(cidr)
    tasks = [scan_ip(ip, port) for ip in network.hosts()]  # .hosts() excludes network and broadcast addresses
    results = await asyncio.gather(*tasks)
    return [ip for ip, result in zip(network.hosts(), results) if result]

async def scan_ip(ip, port):
    try:
        print("Pinging IP: ", ip)
        # Attempt to connect to the specified port
        await asyncio.wait_for(asyncio.open_connection(str(ip), port), timeout=5)
        print(f"Webserver found at {ip}:{port}")
        return ip
    except (asyncio.TimeoutError, Exception) as e:
        print(f"Error scanning {ip}:{port} - {e}")

# replace with your cidr range
# cidr_block = "192.168.1.0/24"
cidr_block = "10.0.0.0/24"

print(f"Scanning {cidr_block} for web servers on port 6969")
web_servers = asyncio.run(scan_network_parallel(cidr_block))
print("Web servers found: ", web_servers)
