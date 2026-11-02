import json
import socket

import numpy as np
import omni.kit.app
from isaacsim.core.prims import SingleArticulation
from isaacsim.core.utils.types import ArticulationAction

ROOT = "/World/ur10e"
BRIDGE_ORDER = ["shoulder_pan_joint", "shoulder_lift_joint", "elbow_joint",
                "wrist_1_joint", "wrist_2_joint", "wrist_3_joint"]

arm = SingleArticulation(prim_path=ROOT)
arm.initialize()
idx = [arm.dof_names.index(n) for n in BRIDGE_ORDER]

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("0.0.0.0", 5005))
sock.setblocking(False)

def on_update(event):
    latest = None
    while True:  # Keep only the newest packet.
        try:
            latest, _ = sock.recvfrom(4096)
        except BlockingIOError:
            break
    if latest is None:
        return
    q = np.zeros(arm.num_dof, dtype=np.float32)
    q[idx] = json.loads(latest)["q"]
    arm.set_joint_positions(q)
    arm.apply_action(ArticulationAction(joint_positions=q))

sub = omni.kit.app.get_app().get_update_event_stream().create_subscription_to_pop(on_update)
print("Exact shadow running. To stop, run: sub = None; sock.close()")