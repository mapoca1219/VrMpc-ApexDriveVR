import unreal

wheel = unreal.load_asset("/Game/Vehicles/Meshes/SM_Steering_Wheel_Centered")
chassis = unreal.load_asset("/Game/Vehicles/Meshes/SM_Merkurs_Chassis")
ioniq = unreal.load_asset("/Game/Vehicles/Meshes/SM_Hyundai_Ioniq5")

lines = []
for name, m in [("Wheel", wheel), ("Chassis", chassis), ("Ioniq", ioniq)]:
    if not m:
        lines.append(f"{name}: NOT FOUND")
        continue
    num_tris = m.get_num_triangles(0)
    num_verts = m.get_num_vertices(0)
    lines.append(f"{name}: Triangles={num_tris}, Vertices={num_verts}")

with open("/Users/marcopolo/Documents/Unreal Projects/VrMpc/Scripts/mesh_counts.txt", "w") as f:
    f.write("\n".join(lines))

