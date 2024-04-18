import ipaddress
import socket
import json
import asyncio
import os

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

def output_webservers_to_file(webservers, filename="/tmp/sensors.json"):
    # Assuming all webservers are in a 'dev' environment for simplicity
    # This can be adjusted as needed
    data = [
        {
            "targets": webservers,
        }
    ]

    with open(filename, 'w') as file:
        json.dump(data, file, indent=2)


default_cidr_block = "10.0.0.0/24"
cidr_block = os.getenv("CIDR_BLOCK", default_cidr_block)

print(f"Scanning {cidr_block} for web servers on port 6969")
web_servers = asyncio.run(scan_network_parallel(cidr_block))
print("Web servers found: ", web_servers)

outfile = "/tmp/sensors.json"
print(f"Outputting web servers to file: {outfile}")

listening_sensors = [f"{str(server)}:6969" for server in web_servers]
output_webservers_to_file(listening_sensors, outfile)
