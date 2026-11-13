import unreal

chassis = unreal.EditorAssetLibrary.load_asset("/Game/Vehicles/Meshes/SM_Merkurs_Chassis")
if chassis:
    bounds = chassis.get_bounds()
    print(f"CHASSIS BOUNDS: origin={bounds.origin}, box_extent={bounds.box_extent}, sphere_radius={bounds.sphere_radius}")
    min_z = bounds.origin.z - bounds.box_extent.z
    print(f"CHASSIS MIN Z: {min_z}")
    
    sub = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
    num_mats = sub.get_number_materials(chassis)
    print(f"CHASSIS NUM MATS: {num_mats}")
    for i in range(num_mats):
        mat = chassis.get_material(i)
        mat_name = mat.get_name() if mat else "None"
        print(f"  Slot {i}: {mat_name}")
