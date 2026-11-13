import unreal

def check_all():
    out = []
    def log(msg):
        unreal.log(f"[CHECK] {msg}")
        out.append(str(msg))

    level_path = "/Game/Maps/L_RaceTrack_VR"
    unreal.EditorLevelLibrary.load_level(level_path)

    log("=== CHECKING BLUEPRINTS ===")
    asset_reg = unreal.AssetRegistryHelpers.get_asset_registry()
    bp_assets = asset_reg.get_assets_by_path("/Game/Blueprints", recursive=True)
    for b in bp_assets:
        bp_obj = unreal.EditorAssetLibrary.load_asset(b.package_name)
        if bp_obj and isinstance(bp_obj, unreal.Blueprint):
            unreal.BlueprintEditorLibrary.compile_blueprint(bp_obj)
            # check status
            log(f"Blueprint: {b.asset_name} compiled.")

    # Check all assets in /Game/Vehicles
    log("=== CHECKING VEHICLE ASSETS ===")
    v_assets = asset_reg.get_assets_by_path("/Game/Vehicles", recursive=True)
    log(f"Total vehicle assets: {len(v_assets)}")

    # Check level actors
    actors = unreal.EditorLevelLibrary.get_all_level_actors()
    log(f"Total actors in level: {len(actors)}")

    with open("/Users/marcopolo/Documents/Unreal Projects/VrMpc/Scripts/map_check_output.txt", "w") as f:
        f.write("\n".join(out))

if __name__ == "__main__":
    check_all()

