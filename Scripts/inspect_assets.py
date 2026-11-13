import unreal

out_lines = []

def log_msg(msg):
    unreal.log_warning(f"[INSPECT] {msg}")
    out_lines.append(msg)

def inspect_asset(path):
    obj = unreal.load_asset(path)
    if not obj:
        log_msg(f"Asset NOT FOUND: {path}")
        return
    log_msg(f"=== Asset: {path} ({obj.get_class().get_name()}) ===")
    if isinstance(obj, unreal.StaticMesh):
        bounds = obj.get_bounds()
        log_msg(f"  Box Extent: {bounds.box_extent}, Origin: {bounds.origin}")
        log_msg(f"  Materials count: {len(obj.static_materials)}")
        for i, m in enumerate(obj.static_materials):
            mat_name = m.material_interface.get_name() if m.material_interface else "None"
            log_msg(f"    Slot {i} ({m.material_slot_name}): {mat_name}")
    elif isinstance(obj, unreal.SoundWave):
        log_msg(f"  SoundWave loaded successfully: {obj.get_name()}")

inspect_asset("/Game/Vehicles/Meshes/SM_Steering_Wheel_Centered")
inspect_asset("/Game/Vehicles/Meshes/SM_Merkurs_Chassis")
inspect_asset("/Game/Vehicles/Meshes/SM_Hyundai_Ioniq5")
inspect_asset("/Game/Audio/SW_Engine_Loop")
inspect_asset("/Game/Audio/SW_Police_Siren")
inspect_asset("/Game/Audio/SW_Copilot_Radio")

with open("/Users/marcopolo/Documents/Unreal Projects/VrMpc/Scripts/inspect_results.txt", "w") as f:
    f.write("\n".join(out_lines))

log_msg("Saved results to inspect_results.txt")
