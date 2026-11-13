import unreal

def inspect_mesh_vertices():
    ioniq = unreal.load_asset("/Game/Vehicles/Meshes/SM_Hyundai_Ioniq5")
    merkurs = unreal.load_asset("/Game/Vehicles/Meshes/SM_Merkurs_Chassis")
    
    print("[INSPECT] Ioniq bounds:", ioniq.get_bounds())
    print("[INSPECT] Merkurs bounds:", merkurs.get_bounds())

inspect_mesh_vertices()

