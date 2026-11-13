import unreal

def recompile():
    bp_player = unreal.EditorAssetLibrary.load_asset("/Game/Blueprints/BP_VrVehiclePawn")
    if bp_player:
        unreal.KismetEditorUtilities.compile_blueprint(bp_player)
        unreal.EditorAssetLibrary.save_loaded_asset(bp_player)
        unreal.log_warning("BP_VrVehiclePawn recompilado y guardado con exito.")

    bp_police = unreal.EditorAssetLibrary.load_asset("/Game/Blueprints/BP_PoliceVehiclePawn")
    if bp_police:
        unreal.KismetEditorUtilities.compile_blueprint(bp_police)
        unreal.EditorAssetLibrary.save_loaded_asset(bp_police)
        unreal.log_warning("BP_PoliceVehiclePawn recompilado y guardado con exito.")

if __name__ == "__main__":
    recompile()

