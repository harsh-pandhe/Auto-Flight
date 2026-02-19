#!/usr/bin/env python3
"""
Find Livox Mid 360 on network
Scans the local network for Livox devices
"""

import socket
import subprocess
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

def ping_host(host):
    """Check if a host is reachable"""
    try:
        result = subprocess.run(
            ['ping', '-c', '1', '-W', '100', host],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=1
        )
        return host if result.returncode == 0 else None
    except:
        return None

def check_livox_port(host, port=65000):
    """Check if Livox port is open on host"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(0.5)
        sock.sendto(b'\x00', (host, port))
        sock.close()
        return True
    except:
        return False

def scan_network(network_range="172.17"):
    """Scan network for Livox devices"""
    print(f"Scanning network range {network_range}.x.x for Livox...")
    print("This may take a minute...\n")
    
    # Generate IPs to scan
    ips = [f"{network_range}.{i}.{j}" for i in range(0, 256) for j in range(1, 256)]
    
    found_devices = []
    
    # Ping all hosts first
    print("Phase 1: Scanning for active hosts...")
    with ThreadPoolExecutor(max_workers=50) as executor:
        futures = {executor.submit(ping_host, ip): ip for ip in ips}
        
        for i, future in enumerate(as_completed(futures)):
            result = future.result()
            if result:
                found_devices.append(result)
                print(f"  Found: {result}")
            
            if (i + 1) % 256 == 0:
                print(f"  Progress: {i + 1}/{len(ips)}")
    
    if not found_devices:
        print("No active hosts found!")
        return None
    
    # Check for Livox port
    print(f"\nPhase 2: Checking {len(found_devices)} devices for Livox port 65000...")
    livox_found = []
    
    for device in found_devices:
        if check_livox_port(device):
            livox_found.append(device)
            print(f"  ✓ Livox found at: {device}:65000")
    
    if livox_found:
        print(f"\n✓ Found {len(livox_found)} Livox device(s)!")
        return livox_found[0]
    else:
        print("\n✗ No Livox devices found on port 65000")
        print("\nActive devices found:")
        for device in found_devices[:20]:
            print(f"  {device}")
        return None

if __name__ == "__main__":
    print("="*60)
    print("Livox Mid 360 Network Scanner")
    print("="*60)
    
    # Get network info
    try:
        # Try to get the current network range
        result = subprocess.run(
            ['ip', 'route', 'show'],
            capture_output=True,
            text=True
        )
        # Extract subnet (simplified)
        network_range = "172.17"  # Default for this network
        if "172.17" in result.stdout:
            network_range = "172.17"
        elif "192.168" in result.stdout:
            network_range = "192.168"
        elif "10.0" in result.stdout:
            network_range = "10.0"
        
        print(f"Detected network range: {network_range}.x.x")
        
    except Exception as e:
        print(f"Could not detect network, using default: 172.17.x.x")
        network_range = "172.17"
    
    livox_ip = scan_network(network_range)
    
    if livox_ip:
        print(f"\n{'='*60}")
        print(f"Update livox_3d_mapper.py line 10:")
        print(f'  LIVOX_IP = "{livox_ip}"')
        print(f"{'='*60}")
    else:
        print("\nTroubleshooting tips:")
        print("  1. Check if Livox is powered on and connected via Ethernet")
        print("  2. Verify network cable is properly connected")
        print("  3. Check your router for Livox DHCP assignment")
        print("  4. Try static IP: 192.168.1.102 (Livox default)")
