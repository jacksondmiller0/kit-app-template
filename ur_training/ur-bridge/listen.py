"""Run on the host to check that bridge data arrives: python listen.py"""
import json
import math
import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("0.0.0.0", 5005))
print("Listening on UDP 5005...")
while True:
    data, _ = sock.recvfrom(4096)
    q = json.loads(data)["q"]
    print(" ".join(f"{math.degrees(a):7.1f}" for a in q))
