import unreal

eal = unreal.EditorAssetLibrary
assets = eal.list_assets("/Game/Vehicles")
for a in assets:
    unreal.log_warning(f"VEHICLE ASSET: {a}")

