import unreal

mesh = unreal.EditorAssetLibrary.load_asset("/Game/Vehicles/Meshes/SM_Merkurs_Chassis")
materials = mesh.get_editor_property("static_materials")

out = []
for i, sm in enumerate(materials):
    slot_name = sm.material_slot_name
    mat = sm.material_interface
    mname = mat.get_name() if mat else "None"
    out.append(f"Slot {i:02d} ({slot_name}): {mname}")

with open("/Users/marcopolo/Documents/Unreal Projects/VrMpc/Scripts/slots_detailed.txt", "w") as f:
    f.write("\n".join(out))
