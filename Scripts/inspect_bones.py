import unreal

def inspect_bones():
    path = "/Game/Vehicles/mercedes-benz+AMG+GT-R"
    mesh = unreal.EditorAssetLibrary.load_asset(path)
    lines = []
    lines.append(f"Mesh: {mesh}")
    
    skel = mesh.get_editor_property("skeleton")
    lines.append(f"Skeleton: {skel}")
    pa = mesh.get_editor_property("physics_asset")
    lines.append(f"PhysicsAsset: {pa}")

    # Inspect bones via python if possible
    # We can inspect bone count and names
    try:
        ref_skeleton = mesh.get_editor_property("ref_skeleton")
    except:
        ref_skeleton = None

    lines.append(f"RefSkeleton: {ref_skeleton}")

    # Let's inspect all StaticMeshes and SkeletalMeshes in /Game/Vehicles
    asset_reg = unreal.AssetRegistryHelpers.get_asset_registry()
    assets = asset_reg.get_assets_by_path("/Game/Vehicles", recursive=True)
    lines.append(f"Total assets in /Game/Vehicles: {len(assets)}")
    for a in assets:
        cname = str(a.asset_class_path.asset_name)
        if any(k in cname.lower() for k in ["mesh", "wheel", "skeleton", "physics", "vehicle"]):
            lines.append(f"  {a.asset_name} ({cname})")

    with open("/Users/marcopolo/Documents/Unreal Projects/VrMpc/Scripts/skel_bones.txt", "w") as f:
        f.write("\n".join(lines))

if __name__ == "__main__":
    inspect_bones()

