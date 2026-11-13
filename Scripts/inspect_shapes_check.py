import unreal

# We can inspect the mesh's static mesh editor subsystem or bounds
mesh = unreal.load_asset("/Game/Vehicles/Meshes/SM_Steering_Wheel_Centered")
unreal.log_warning(f"Steering Wheel LOD 0 vertices check:")
# Let's check with cylinder and torus
# What basic shapes exist?
for shape in ["Cube", "Cylinder", "Sphere", "Cone"]:
    s = unreal.load_asset(f"/Engine/BasicShapes/{shape}")
    if s:
        unreal.log_warning(f"BasicShape: {shape} exists")

