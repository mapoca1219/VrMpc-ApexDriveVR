import unreal

mesh = unreal.load_asset("/Game/Vehicles/Meshes/SM_Hyundai_Ioniq5")
# Let's inspect materials or sections
print("SM_Hyundai_Ioniq5 materials:", len(mesh.static_materials))
for i, m in enumerate(mesh.static_materials):
    unreal.log_warning(f"Slot {i}: {m.material_slot_name}")

