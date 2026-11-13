import unreal

def find_sounds():
    asset_reg = unreal.AssetRegistryHelpers.get_asset_registry()
    out = []
    
    classes_to_search = [
        unreal.TopLevelAssetPath("/Script/Engine", "SoundWave"),
        unreal.TopLevelAssetPath("/Script/Engine", "SoundCue"),
        unreal.TopLevelAssetPath("/Script/Engine", "SoundBase"),
        unreal.TopLevelAssetPath("/Script/MetaSoundEngine", "MetaSoundSource")
    ]

    for c in classes_to_search:
        assets = asset_reg.get_assets_by_class(c)
        out.append(f"Class {c.asset_name}: {len(assets)} assets found")
        for a in assets[:10]:
            out.append(f"   {a.package_name}")

    with open("/Users/marcopolo/Documents/Unreal Projects/VrMpc/Scripts/sounds_found.txt", "w") as f:
        f.write("\n".join(out))

if __name__ == "__main__":
    find_sounds()

