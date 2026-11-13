import unreal

def inspect_pa_bodies():
    out = []
    if hasattr(unreal, "PhysicsAssetEditorLibrary"):
        out.append("PhysicsAssetEditorLibrary found")
        for m in dir(unreal.PhysicsAssetEditorLibrary):
            if not m.startswith("_"):
                out.append(m)
    else:
        out.append("No PhysicsAssetEditorLibrary")

    with open("/Users/marcopolo/Documents/Unreal Projects/VrMpc/Scripts/pa_inspect.txt", "w") as f:
        f.write("\n".join(out))

if __name__ == "__main__":
    inspect_pa_bodies()
