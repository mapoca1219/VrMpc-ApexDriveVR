import unreal

def convert_material(mat_path, base_color, win_color, emissive_mult=0.25):
    if not unreal.EditorAssetLibrary.does_asset_exist(mat_path):
        return
    mat = unreal.EditorAssetLibrary.load_asset(mat_path)
    if not mat or not isinstance(mat, unreal.Material):
        return
    try:
        mat.set_editor_property("blend_mode", unreal.BlendMode.BLEND_OPAQUE)
        mat.set_editor_property("shading_model", unreal.MaterialShadingModel.MSM_DEFAULT_LIT)
        unreal.MaterialEditingLibrary.delete_all_material_expressions(mat)

        base_node = unreal.MaterialEditingLibrary.create_material_expression(mat, unreal.MaterialExpressionConstant3Vector, -350, -100)
        base_node.set_editor_property("constant", base_color)
        unreal.MaterialEditingLibrary.connect_material_property(base_node, "", unreal.MaterialProperty.MP_BASE_COLOR)

        metallic = unreal.MaterialEditingLibrary.create_material_expression(mat, unreal.MaterialExpressionConstant, -350, 0)
        metallic.set_editor_property("r", 0.75)
        unreal.MaterialEditingLibrary.connect_material_property(metallic, "", unreal.MaterialProperty.MP_METALLIC)

        roughness = unreal.MaterialEditingLibrary.create_material_expression(mat, unreal.MaterialExpressionConstant, -350, 70)
        roughness.set_editor_property("r", 0.32)
        unreal.MaterialEditingLibrary.connect_material_property(roughness, "", unreal.MaterialProperty.MP_ROUGHNESS)

        emissive = unreal.MaterialEditingLibrary.create_material_expression(mat, unreal.MaterialExpressionConstant3Vector, -350, 180)
        soft_glow = unreal.LinearColor(win_color.r * emissive_mult, win_color.g * emissive_mult, win_color.b * emissive_mult, 1.0)
        emissive.set_editor_property("constant", soft_glow)
        unreal.MaterialEditingLibrary.connect_material_property(emissive, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)

        unreal.MaterialEditingLibrary.recompile_material(mat)
        unreal.EditorAssetLibrary.save_loaded_asset(mat)
    except Exception as e:
        print(f"Error {mat_path}: {e}")

def run():
    print(">>> [FIX] Neutralizando resplandor excesivo de edificios...", flush=True)
    convert_material("/Game/LevelPrototyping/Materials/M_City_NeonMagenta", unreal.LinearColor(0.04, 0.035, 0.045, 1.0), unreal.LinearColor(0.95, 0.50, 0.75, 1.0), 0.25)
    convert_material("/Game/LevelPrototyping/Materials/M_City_NeonCyan", unreal.LinearColor(0.035, 0.04, 0.055, 1.0), unreal.LinearColor(0.25, 0.70, 0.95, 1.0), 0.25)
    convert_material("/Game/LevelPrototyping/Materials/M_City_GoldenAmber", unreal.LinearColor(0.045, 0.04, 0.035, 1.0), unreal.LinearColor(1.0, 0.80, 0.45, 1.0), 0.25)
    convert_material("/Game/LevelPrototyping/Materials/M_City_EmeraldMatrix", unreal.LinearColor(0.035, 0.045, 0.04, 1.0), unreal.LinearColor(0.35, 0.90, 0.65, 1.0), 0.25)

    # Configurar el volante para que sea negro
    wheel_mesh = unreal.EditorAssetLibrary.load_asset("/Game/Vehicles/Meshes/SM_Steering_Wheel_Centered")
    black_trim = unreal.EditorAssetLibrary.load_asset("/Game/Vehicles/Materials/M_SteeringWheel_Alcantara")
    if wheel_mesh and black_trim:
        sub = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
        num_slots = sub.get_number_materials(wheel_mesh) if sub else 2
        for s in range(max(1, num_slots)):
            try:
                sub.set_material(wheel_mesh, s, black_trim)
            except:
                pass
        unreal.EditorAssetLibrary.save_loaded_asset(wheel_mesh)

    print(">>> [FIX] Recargando nivel L_RaceTrack_VR...", flush=True)
    unreal.EditorLevelLibrary.load_level("/Game/Maps/L_RaceTrack_VR")
    unreal.EditorLevelLibrary.save_current_level()
    print(">>> [FIX] ¡Nivel y materiales actualizados al 100%!", flush=True)

if __name__ == "__main__":
    run()
