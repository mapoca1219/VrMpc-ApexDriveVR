import unreal

# In UE 5.8:
class_path = unreal.TopLevelAssetPath("/Script/Engine", "StaticMesh")
assets = unreal.AssetRegistryHelpers.get_asset_registry().get_assets_by_class(class_path)
for a in assets:
    p = str(a.package_name)
    if "Wheel" in p or "wheel" in p or "Steer" in p or "steer" in p or "Dash" in p or "dash" in p:
        unreal.log_warning(f"MATCH: {p}")

