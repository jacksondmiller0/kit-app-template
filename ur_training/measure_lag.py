import json
import os
import socket
import time

import numpy as np
import omni.kit.app
from isaacsim.core.prims import SingleArticulation
from isaacsim.core.utils.types import ArticulationAction

MODE = "exact"          # "drive" (before) or "exact" (after)
ROOT = "/World/ur10e"   # Your articulation root path
N_SAMPLES = 900         # About 30 s at 30 Hz
OUT_DIR = r"C:\Omniverse_Training_Jackson\kit-app-template\ur_training\results"

BRIDGE_ORDER = ["shoulder_pan_joint", "shoulder_lift_joint", "elbow_joint",
                "wrist_1_joint", "wrist_2_joint", "wrist_3_joint"]

arm = SingleArticulation(prim_path=ROOT)
arm.initialize()
idx = [arm.dof_names.index(n) for n in BRIDGE_ORDER]  # Bridge order to sim order
print("DOF names:", arm.dof_names)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("0.0.0.0", 5005))
sock.setblocking(False)

last_q = None
rows = []

def on_update(event):
    global last_q, sub
    # 1. Compare the sim arm to the last reported angles.
    if last_q is not None:
        err = arm.get_joint_positions() - last_q
        rows.append([time.time(), last_age_ms] + list(np.degrees(err)))

    # 2. Read the newest packet.
    latest = None
    while True:
        try:
            latest, _ = sock.recvfrom(4096)
        except BlockingIOError:
            break
    if latest is None:
        return
    msg = json.loads(latest)
    q = np.zeros(arm.num_dof, dtype=np.float32)
    q[idx] = msg["q"]
    globals()["last_age_ms"] = (time.time() - msg["t"]) * 1000
    last_q = q

    # 3. Apply it.
    if MODE == "exact":
        arm.set_joint_positions(q)
    arm.apply_action(ArticulationAction(joint_positions=q))

    # 4. Save and stop after enough samples.
    if len(rows) >= N_SAMPLES:
        os.makedirs(OUT_DIR, exist_ok=True)
        path = os.path.join(OUT_DIR, f"lag_{MODE}.csv")
        header = "time,age_ms," + ",".join(f"err_{n}_deg" for n in BRIDGE_ORDER)
        np.savetxt(path, np.array(rows), delimiter=",", header=header, comments="")
        print("Saved", path)
        sub = None
        sock.close()

sub = omni.kit.app.get_app().get_update_event_stream().create_subscription_to_pop(on_update)
print(f"Recording {MODE} mode...")
