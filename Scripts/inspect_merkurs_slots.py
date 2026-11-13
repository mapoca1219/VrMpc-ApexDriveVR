import unreal

m = unreal.load_asset("/Game/Vehicles/Meshes/SM_Merkurs_Chassis")
unreal.log_warning(f"Merkurs sections: {m.get_num_sections(0)}")
for i in range(m.get_num_sections(0)):
    mat = m.get_material(i)
    mat_name = mat.get_name() if mat else "None"
    unreal.log_warning(f"  Slot {i}: {mat_name}")

