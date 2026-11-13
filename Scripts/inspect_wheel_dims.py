import unreal

mesh = unreal.load_asset("/Game/Vehicles/Meshes/SM_Steering_Wheel_Centered")
# Let's inspect mesh bounds in detail
box = mesh.get_bounding_box()
unreal.log_warning(f"Steering Wheel Box Min: {box.min}, Max: {box.max}")
# Total dimensions:
dx = box.max.x - box.min.x
dy = box.max.y - box.min.y
dz = box.max.z - box.min.z
unreal.log_warning(f"Dimensions: X={dx:.5f}, Y={dy:.5f}, Z={dz:.5f}")

