import unreal

# Let's inspect SM_Steering_Wheel_Centered in detail
mesh = unreal.load_asset("/Game/Vehicles/Meshes/SM_Steering_Wheel_Centered")
# Let's check socket or bounds or collision
unreal.log_warning(f"Num sockets: {len(mesh.get_editor_property('sockets'))}")
# Let's check materials
for i in range(mesh.get_num_sections(0)):
    m = mesh.get_material(i)
    unreal.log_warning(f"Section {i} material: {m.get_name() if m else 'None'}")

