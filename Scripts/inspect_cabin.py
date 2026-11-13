import unreal

merkurs = unreal.load_asset("/Game/Vehicles/Meshes/SM_Merkurs_Chassis")
box = merkurs.get_bounding_box()
unreal.log_warning(f"SM_Merkurs_Chassis Min: {box.min}")
unreal.log_warning(f"SM_Merkurs_Chassis Max: {box.max}")
# Total length is X: -250.2 to +250.2 (5 meters)
# Total width is Y: -120.9 to +120.9 (2.4 meters)
# Total height is Z: -0.3 to +123.65 (1.24 meters)

