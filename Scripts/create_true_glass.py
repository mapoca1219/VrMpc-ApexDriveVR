import unreal

def create_glass():
    pkg_path = "/Game/Vehicles/Materials"
    mat_name = "M_TrueClearGlass"
    full_path = f"{pkg_path}/{mat_name}"

    mat = unreal.EditorAssetLibrary.load_asset(full_path)
    if not mat:
        asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
        mat_factory = unreal.MaterialFactoryNew()
        mat = asset_tools.create_asset(mat_name, pkg_path, unreal.Material, mat_factory)

    if mat:
        try:
            mat.set_editor_property("blend_mode", unreal.BlendMode.BLEND_TRANSLUCENT)
            mat.set_editor_property("shading_model", unreal.MaterialShadingModel.MSM_UNLIT)
            mat.set_editor_property("two_sided", True)

            # Usar MaterialEditingLibrary si está disponible
            try:
                unreal.MaterialEditingLibrary.delete_all_material_expressions(mat)
                
                # Expresión de Opacidad = 0.0 (100% transparente)
                opac_expr = unreal.MaterialEditingLibrary.create_material_expression(mat, unreal.MaterialExpressionConstant, -200, 100)
                opac_expr.set_editor_property("r", 0.0)
                unreal.MaterialEditingLibrary.connect_material_property(opac_expr, "", unreal.MaterialProperty.MP_OPACITY)

                # Color Emisivo muy sutil
                col_expr = unreal.MaterialEditingLibrary.create_material_expression(mat, unreal.MaterialExpressionConstant3Vector, -200, -100)
                col_expr.set_editor_property("constant", unreal.LinearColor(0.8, 0.95, 1.0, 1.0))
                unreal.MaterialEditingLibrary.connect_material_property(col_expr, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)

                unreal.MaterialEditingLibrary.recompile_material(mat)
                print(">>> [GLASS] Material M_TrueClearGlass creado y compilado con Opacity=0.0!")
            except Exception as e:
                print(f">>> [GLASS] Aviso configurando nodos con MaterialEditingLibrary: {e}")
        except Exception as e:
            print(f">>> [GLASS] Error configurando propiedades del material: {e}")

    return mat

if __name__ == "__main__":
    create_glass()

