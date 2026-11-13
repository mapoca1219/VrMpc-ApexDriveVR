import unreal

# Test rotation of SM_Steering_Wheel_Centered
wheel = unreal.load_asset("/Game/Vehicles/Meshes/SM_Steering_Wheel_Centered")
box = wheel.get_bounding_box()
unreal.log_warning(f"=== SM_Steering_Wheel_Centered Bounds ===")
unreal.log_warning(f"Min: {box.min}")
unreal.log_warning(f"Max: {box.max}")
# Let's check the center of mass or origin
bounds = wheel.get_bounds()
unreal.log_warning(f"Origin: {bounds.origin}")
unreal.log_warning(f"BoxExtent: {bounds.box_extent}")
unreal.log_warning(f"SphereRadius: {bounds.sphere_radius}")

