import unreal

mesh = unreal.EditorAssetLibrary.load_asset("/Game/Vehicles/Meshes/SM_Steering_Wheel_Centered")
if mesh:
    sub = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
    num = sub.get_number_materials(mesh) if sub else 0
    print(f"SM_Steering_Wheel_Centered has {num} materials:", flush=True)
    for i in range(num):
        mat = mesh.get_material(i)
        print(f"  Slot {i}: {mat.get_name() if mat else 'None'}", flush=True)
