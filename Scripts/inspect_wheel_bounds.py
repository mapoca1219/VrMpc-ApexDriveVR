import unreal

wheel = unreal.load_asset("/Game/Vehicles/Meshes/SM_Steering_Wheel_Centered")
# Let's check the bounding box dimensions:
bounds = wheel.get_bounds()
print(f"Wheel Bounds: BoxExtent={bounds.box_extent}, Origin={bounds.origin}")
# BoxExtent: X=0.0737, Y=0.0689, Z=0.1609
# Full size: X=0.147, Y=0.138, Z=0.322

