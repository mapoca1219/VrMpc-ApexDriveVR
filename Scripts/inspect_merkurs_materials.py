import unreal

def inspect_merkurs_materials():
    mesh = unreal.EditorAssetLibrary.load_asset("/Game/Vehicles/Meshes/SM_Merkurs_Chassis")
    if not mesh:
        unreal.log_error("Mesh not found")
        return

    unreal.log_warning(f"SM_Merkurs_Chassis has {mesh.get_num_sections(0)} sections:")
    for i in range(mesh.get_num_sections(0)):
        mat = mesh.get_material(i)
        mname = mat.get_name() if mat else "None"
        unreal.log_warning(f"   Section {i}: Material = {mname}")

if __name__ == "__main__":
    inspect_merkurs_materials()

