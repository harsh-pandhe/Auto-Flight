#!/usr/bin/env python3
"""
Livox UDP packet sniffer
Listens on a UDP port range and prints packet sizes + first bytes.
"""

import argparse
import binascii
import selectors
import socket
import subprocess
import time

BUFFER_SIZE = 65536


def hexdump(data, max_len):
    return binascii.hexlify(data[:max_len]).decode("ascii")


def print_local_ips():
    try:
        result = subprocess.run(
            ["ip", "-o", "-4", "addr", "show"],
            capture_output=True,
            text=True,
            check=False,
        )
        lines = [line.strip() for line in result.stdout.splitlines() if line.strip()]
        if lines:
            print("Local IPv4 addresses:")
            for line in lines:
                parts = line.split()
                if len(parts) >= 4:
                    print(f"  {parts[1]} -> {parts[3]}")
    except Exception:
        pass


def create_socket(bind_ip, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((bind_ip, port))
    sock.setblocking(False)
    return sock


def main():
    parser = argparse.ArgumentParser(description="Livox UDP packet sniffer")
    parser.add_argument("--bind", default="0.0.0.0", help="Bind IP (default 0.0.0.0)")
    parser.add_argument("--port-start", type=int, default=65000, help="Start UDP port")
    parser.add_argument("--port-end", type=int, default=65010, help="End UDP port")
    parser.add_argument("--dump-bytes", type=int, default=64, help="Hex dump length")
    parser.add_argument(
        "--probe-ip",
        default="",
        help="Optional Livox IP to send a UDP probe packet",
    )
    parser.add_argument(
        "--probe-port",
        type=int,
        default=65000,
        help="UDP port to probe on the device",
    )
    args = parser.parse_args()

    print("=" * 60)
    print("Livox UDP Packet Sniffer")
    print("=" * 60)
    print_local_ips()
    print(
        f"Listening on {args.bind}:{args.port_start}-{args.port_end} "
        f"dump={args.dump_bytes} bytes"
    )

    selector = selectors.DefaultSelector()
    sockets = []

    for port in range(args.port_start, args.port_end + 1):
        try:
            sock = create_socket(args.bind, port)
        except OSError as exc:
            print(f"Port {port} bind failed: {exc}")
            continue
        selector.register(sock, selectors.EVENT_READ, data=port)
        sockets.append(sock)

    if not sockets:
        print("No sockets available. Exiting.")
        return

    if args.probe_ip:
        try:
            probe = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            probe.sendto(b"\x00", (args.probe_ip, args.probe_port))
            probe.close()
            print(f"Probe sent to {args.probe_ip}:{args.probe_port}")
        except Exception as exc:
            print(f"Probe failed: {exc}")

    packet_count = 0
    last_print = time.time()

    try:
        while True:
            events = selector.select(timeout=1.0)
            if not events:
                if time.time() - last_print > 2.0:
                    print("No packets yet...")
                    last_print = time.time()
                continue

            for key, _ in events:
                sock = key.fileobj
                port = key.data
                data, addr = sock.recvfrom(BUFFER_SIZE)
                packet_count += 1
                print(
                    f"#{packet_count} from {addr[0]}:{addr[1]} "
                    f"to port {port} size={len(data)} bytes "
                    f"dump={hexdump(data, args.dump_bytes)}"
                )
                last_print = time.time()
    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        for sock in sockets:
            sock.close()


if __name__ == "__main__":
    main()
