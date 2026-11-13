import unreal

def check_mesh_orientation():
    ioniq = unreal.load_asset("/Game/Vehicles/Meshes/SM_Hyundai_Ioniq5")
    bounds = ioniq.get_bounds()
    # Let's inspect the bounding box:
    unreal.log_warning(f"[IONIQ_BOUNDS] Box Extent: {bounds.box_extent}, Origin: {bounds.origin}")

check_mesh_orientation()

