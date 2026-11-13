import unreal

def inspect_ref():
    mesh = unreal.EditorAssetLibrary.load_asset("/Game/Vehicles/mercedes-benz+AMG+GT-R")
    skel = mesh.get_editor_property("skeleton")
    ref = skel.get_reference_pose()
    out = []
    out.append(f"Ref pose: {ref}")
    for a in dir(ref):
        if not a.startswith("_"):
            out.append(a)
    
    # Try getting bone names
    try:
        raw_names = ref.get_bone_names()
        out.append(f"Bone names count: {len(raw_names)}")
        for n in raw_names:
            out.append(f"  {n}")
    except Exception as e:
        out.append(f"Error raw_names: {e}")

    with open("/Users/marcopolo/Documents/Unreal Projects/VrMpc/Scripts/skel_deep.txt", "w") as f:
        f.write("\n".join(out))

if __name__ == "__main__":
    inspect_ref()
