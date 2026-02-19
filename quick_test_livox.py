#!/usr/bin/env python3
"""
Quick Livox connection test
Tests common Livox IP addresses and networks
"""

import socket
import sys

def test_connection(ip, port=65000):
    """Test if Livox is accessible at given IP"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(1)
        sock.sendto(b'\x00', (ip, port))
        sock.close()
        return True
    except:
        return False

# Common Livox IP patterns
ips_to_try = [
    "192.168.1.102",      # Livox default
    "192.168.1.103",
    "192.168.1.100",
    "172.17.0.102",       # Alternate pattern
    "172.17.255.102",
    "10.0.0.102",         # Another common pattern
    "10.0.0.100",
    "169.254.1.102",      # Link-local
]

print("Testing common Livox IP addresses...")
print("=" * 50)

found = False
for ip in ips_to_try:
    sys.stdout.write(f"Testing {ip:20} ... ")
    sys.stdout.flush()
    
    if test_connection(ip):
        print("✓ FOUND!")
        print(f"\nUpdate livox_3d_mapper.py line 10:")
        print(f'  LIVOX_IP = "{ip}"')
        found = True
        break
    else:
        print("✗")

if not found:
    print("\n" + "=" * 50)
    print("Livox not found at common IPs.")
    print("\nTroubleshooting:")
    print("1. Check Livox display/web interface for its IP")
    print("2. Check your router for connected devices")
    print("3. Ensure Ethernet cable is connected")
    print("4. Check if Livox is on a different network (edit ips_to_try)")
    print("\nAlternative: Use Livox official tool to find IP")
