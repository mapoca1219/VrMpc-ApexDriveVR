import unreal

def inspect_skel():
    path = "/Game/Vehicles/mercedes-benz+AMG+GT-R"
    mesh = unreal.EditorAssetLibrary.load_asset(path)
    print(f"Asset at {path}: {mesh} (Class: {mesh.get_class().get_name() if mesh else None})")
    if mesh and isinstance(mesh, unreal.SkeletalMesh):
        skel = mesh.get_editor_property("skeleton")
        pa = mesh.get_editor_property("physics_asset")
        print(f"Skeleton: {skel}")
        print(f"PhysicsAsset: {pa}")

if __name__ == "__main__":
    inspect_skel()

