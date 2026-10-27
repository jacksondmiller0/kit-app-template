"""Read-only UR bridge: reads joint positions over RTDE and sends them as UDP JSON."""
import json
import os
import socket
import time

from rtde_receive import RTDEReceiveInterface

ROBOT_IP = os.environ["ROBOT_IP"]
TARGET = (os.environ.get("TARGET_HOST", "127.0.0.1"), int(os.environ.get("TARGET_PORT", "5005")))
PERIOD = 1.0 / float(os.environ.get("RATE_HZ", "30"))


def connect():
    while True:
        try:
            print(f"Connecting to {ROBOT_IP}...")
            return RTDEReceiveInterface(ROBOT_IP)
        except RuntimeError as err:
            print(f"Connection failed ({err}). Retrying in 5 s.")
            time.sleep(5)


def main():
    rtde = connect()
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print(f"Sending joints to {TARGET[0]}:{TARGET[1]} at {1/PERIOD:.0f} Hz")
    while True:
        start = time.time()
        if not rtde.isConnected():
            rtde = connect()
        # Joint positions in radians, base to wrist 3.
        msg = {"t": start, "q": rtde.getActualQ()}
        sock.sendto(json.dumps(msg).encode(), TARGET)
        time.sleep(max(0.0, PERIOD - (time.time() - start)))


if __name__ == "__main__":
    main()
