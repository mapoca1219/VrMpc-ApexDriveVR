import unreal

# Let's inspect SM_Steering_Wheel_Centered
m = unreal.load_asset("/Game/Vehicles/Meshes/SM_Steering_Wheel_Centered")
b = m.get_bounding_box()
unreal.log_warning(f"Steering Wheel Box: Min={b.min}, Max={b.max}")
unreal.log_warning(f"X range: {b.max.x - b.min.x}")
unreal.log_warning(f"Y range: {b.max.y - b.min.y}")
unreal.log_warning(f"Z range: {b.max.z - b.min.z}")

