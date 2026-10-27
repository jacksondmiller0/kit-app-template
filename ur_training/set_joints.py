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
	"""Set six joint targets in degrees, base to wrist 3."""
	for name, value in zip(JOINTS, q_deg):
		drives[name].GetTargetPositionAttr().Set(float(value))

set_joints([0, -90, 90, -90, -90, 0])