import unreal

wheel = unreal.load_asset("/Game/Vehicles/Meshes/SM_Steering_Wheel_Centered")
chassis = unreal.load_asset("/Game/Vehicles/Meshes/SM_Merkurs_Chassis")
ioniq = unreal.load_asset("/Game/Vehicles/Meshes/SM_Hyundai_Ioniq5")

lines = []
lines.append("=== MESH DETAILS ===")
for name, m in [("Wheel", wheel), ("Chassis", chassis), ("Ioniq", ioniq)]:
    if not m:
        lines.append(f"{name}: NOT FOUND")
        continue
    bounds = m.get_bounds()
    num_lods = m.get_num_lods()
    num_sections = m.get_num_sections(0) if num_lods > 0 else 0
    lines.append(f"{name}: LODs={num_lods}, Sections(LOD0)={num_sections}, Bounds: Extent={bounds.box_extent}, Origin={bounds.origin}")
    for sec in range(min(num_sections, 5)):
        mat = m.get_material(sec)
        lines.append(f"  Sec {sec}: {mat.get_name() if mat else 'None'}")

with open("/Users/marcopolo/Documents/Unreal Projects/VrMpc/Scripts/mesh_details.txt", "w") as f:
    f.write("\n".join(lines))

