import json
import math
import socket

import omni.kit.app
import omni.usd
from pxr import UsdPhysics

JOINTS = ["shoulder_pan_joint", "shoulder_lift_joint", "elbow_joint",
            "wrist_1_joint", "wrist_2_joint", "wrist_3_joint"]

stage = omni.usd.get_context().get_stage()
drives = {}
for prim in stage.Traverse():
    if prim.GetName() in JOINTS and prim.HasAPI(UsdPhysics.DriveAPI, "angular"):
        drives[prim.GetName()] = UsdPhysics.DriveAPI(prim, "angular")
print(sorted(drives))  # Expect all six names.

def set_joints(q_deg):
    for name, value in zip(JOINTS, q_deg):
        drives[name].GetTargetPositionAttr().Set(float(value))

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("0.0.0.0", 5005))
sock.setblocking(False)

def on_update(event):
    latest = None
    while True:  # Drain the queue and keep only the newest message.
        try:
            latest, _ = sock.recvfrom(4096)
        except BlockingIOError:
            break
    if latest:
        q = json.loads(latest)["q"]  # Radians from the bridge.
        set_joints([math.degrees(a) for a in q])

sub = omni.kit.app.get_app().get_update_event_stream().create_subscription_to_pop(on_update)
print("Mirroring URSim. To stop, run: sub = None; sock.close()")
