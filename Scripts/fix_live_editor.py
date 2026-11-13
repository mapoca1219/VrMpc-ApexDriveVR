import unreal
import math
import sys
import os

def create_true_clear_glass():
    pkg_path = "/Game/Vehicles/Materials"
    mat_name = "M_TrueClearGlass"
    full_path = f"{pkg_path}/{mat_name}"

    if unreal.EditorAssetLibrary.does_asset_exist(full_path):
        return unreal.EditorAssetLibrary.load_asset(full_path)

    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    mat_factory = unreal.MaterialFactoryNew()
    mat = asset_tools.create_asset(mat_name, pkg_path, unreal.Material, mat_factory)

    if mat:
        try:
            mat.set_editor_property("blend_mode", unreal.BlendMode.BLEND_TRANSLUCENT)
            mat.set_editor_property("shading_model", unreal.MaterialShadingModel.MSM_UNLIT)
            mat.set_editor_property("two_sided", True)
            unreal.MaterialEditingLibrary.delete_all_material_expressions(mat)
            opac_expr = unreal.MaterialEditingLibrary.create_material_expression(mat, unreal.MaterialExpressionConstant, -200, 100)
            opac_expr.set_editor_property("r", 0.0)
            unreal.MaterialEditingLibrary.connect_material_property(opac_expr, "", unreal.MaterialProperty.MP_OPACITY)
            unreal.MaterialEditingLibrary.recompile_material(mat)
            unreal.EditorAssetLibrary.save_loaded_asset(mat)
            print(">>> [FIX_LIVE] M_TrueClearGlass creado.")
        except Exception as e:
            print(f">>> [FIX_LIVE] Error M_TrueClearGlass: {e}")

    return mat

def create_colored_car_paint(r, g, b, mat_name):
    pkg_path = "/Game/Vehicles/Materials"
    full_path = f"{pkg_path}/{mat_name}"

    if unreal.EditorAssetLibrary.does_asset_exist(full_path):
        mat = unreal.EditorAssetLibrary.load_asset(full_path)
    else:
        asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
        mat_factory = unreal.MaterialFactoryNew()
        mat = asset_tools.create_asset(mat_name, pkg_path, unreal.Material, mat_factory)

    if mat:
        try:
            unreal.MaterialEditingLibrary.delete_all_material_expressions(mat)
            
            # Base Color
            base_col = unreal.MaterialEditingLibrary.create_material_expression(mat, unreal.MaterialExpressionVectorParameter, -250, -100)
            base_col.set_editor_property("parameter_name", "PaintColor")
            base_col.set_editor_property("default_value", unreal.LinearColor(r, g, b, 1.0))
            unreal.MaterialEditingLibrary.connect_material_property(base_col, "", unreal.MaterialProperty.MP_BASE_COLOR)

            # Metallic (High Gloss Exotic Finish)
            metallic = unreal.MaterialEditingLibrary.create_material_expression(mat, unreal.MaterialExpressionConstant, -250, 100)
            metallic.set_editor_property("r", 0.90)
            unreal.MaterialEditingLibrary.connect_material_property(metallic, "", unreal.MaterialProperty.MP_METALLIC)

            # Roughness (Glossy Clearcoat)
            roughness = unreal.MaterialEditingLibrary.create_material_expression(mat, unreal.MaterialExpressionConstant, -250, 200)
            roughness.set_editor_property("r", 0.12)
            unreal.MaterialEditingLibrary.connect_material_property(roughness, "", unreal.MaterialProperty.MP_ROUGHNESS)

            unreal.MaterialEditingLibrary.recompile_material(mat)
            unreal.EditorAssetLibrary.save_loaded_asset(mat)
        except Exception as e:
            print(f">>> [FIX_LIVE] Aviso {mat_name}: {e}")

    return mat

def create_balanced_architectural_material(base_r, base_g, base_b, win_r, win_g, win_b, emissive_mult, mat_name):
    """
    Crea materiales arquitectónicos equilibrados: fachada sólida elegante (vidrio/hormigón)
    con ventanas iluminadas suaves sin resplandor cegador que canse la vista en VR.
    """
    pkg_path = "/Game/LevelPrototyping/Materials"
    full_path = f"{pkg_path}/{mat_name}"

    if unreal.EditorAssetLibrary.does_asset_exist(full_path):
        mat = unreal.EditorAssetLibrary.load_asset(full_path)
    else:
        asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
        mat_factory = unreal.MaterialFactoryNew()
        mat = asset_tools.create_asset(mat_name, pkg_path, unreal.Material, mat_factory)

    if mat:
        try:
            unreal.MaterialEditingLibrary.delete_all_material_expressions(mat)

            # Base Color: Fachada arquitectónica realista
            base_col = unreal.MaterialEditingLibrary.create_material_expression(mat, unreal.MaterialExpressionConstant3Vector, -350, -150)
            base_col.set_editor_property("constant", unreal.LinearColor(base_r, base_g, base_b, 1.0))
            unreal.MaterialEditingLibrary.connect_material_property(base_col, "", unreal.MaterialProperty.MP_BASE_COLOR)

            # Metallic
            metallic = unreal.MaterialEditingLibrary.create_material_expression(mat, unreal.MaterialExpressionConstant, -350, -50)
            metallic.set_editor_property("r", 0.85)
            unreal.MaterialEditingLibrary.connect_material_property(metallic, "", unreal.MaterialProperty.MP_METALLIC)

            # Roughness
            roughness = unreal.MaterialEditingLibrary.create_material_expression(mat, unreal.MaterialExpressionConstant, -350, 50)
            roughness.set_editor_property("r", 0.22)
            unreal.MaterialEditingLibrary.connect_material_property(roughness, "", unreal.MaterialProperty.MP_ROUGHNESS)

            # Iluminación de ventanales suave y elegante (0.75x a 0.95x, NUNCA 5.0x cegador)
            emissive = unreal.MaterialEditingLibrary.create_material_expression(mat, unreal.MaterialExpressionConstant3Vector, -350, 180)
            emissive.set_editor_property("constant", unreal.LinearColor(win_r * emissive_mult, win_g * emissive_mult, win_b * emissive_mult, 1.0))
            unreal.MaterialEditingLibrary.connect_material_property(emissive, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)

            unreal.MaterialEditingLibrary.recompile_material(mat)
            unreal.EditorAssetLibrary.save_loaded_asset(mat)
        except Exception as e:
            print(f">>> [FIX_LIVE] Aviso {mat_name}: {e}")

    return mat

def create_highway_asphalt():
    pkg_path = "/Game/LevelPrototyping/Materials"
    mat_name = "M_City_Highway_Asphalt"
    full_path = f"{pkg_path}/{mat_name}"

    if unreal.EditorAssetLibrary.does_asset_exist(full_path):
        mat = unreal.EditorAssetLibrary.load_asset(full_path)
    else:
        asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
        mat_factory = unreal.MaterialFactoryNew()
        mat = asset_tools.create_asset(mat_name, pkg_path, unreal.Material, mat_factory)

    if mat:
        try:
            unreal.MaterialEditingLibrary.delete_all_material_expressions(mat)
            
            # Asfalto de carretera oscuro con grano suave
            base_col = unreal.MaterialEditingLibrary.create_material_expression(mat, unreal.MaterialExpressionConstant3Vector, -250, -100)
            base_col.set_editor_property("constant", unreal.LinearColor(0.045, 0.045, 0.050, 1.0))
            unreal.MaterialEditingLibrary.connect_material_property(base_col, "", unreal.MaterialProperty.MP_BASE_COLOR)

            roughness = unreal.MaterialEditingLibrary.create_material_expression(mat, unreal.MaterialExpressionConstant, -250, 100)
            roughness.set_editor_property("r", 0.72)
            unreal.MaterialEditingLibrary.connect_material_property(roughness, "", unreal.MaterialProperty.MP_ROUGHNESS)

            unreal.MaterialEditingLibrary.recompile_material(mat)
            unreal.EditorAssetLibrary.save_loaded_asset(mat)
        except Exception as e:
            print(f">>> [FIX_LIVE] Aviso M_City_Highway_Asphalt: {e}")

    return mat

def create_neon_guardrail():
    pkg_path = "/Game/LevelPrototyping/Materials"
    mat_name = "M_City_Neon_Guardrail"
    full_path = f"{pkg_path}/{mat_name}"

    if unreal.EditorAssetLibrary.does_asset_exist(full_path):
        mat = unreal.EditorAssetLibrary.load_asset(full_path)
    else:
        asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
        mat_factory = unreal.MaterialFactoryNew()
        mat = asset_tools.create_asset(mat_name, pkg_path, unreal.Material, mat_factory)

    if mat:
        try:
            unreal.MaterialEditingLibrary.delete_all_material_expressions(mat)
            
            base_col = unreal.MaterialEditingLibrary.create_material_expression(mat, unreal.MaterialExpressionConstant3Vector, -250, -100)
            base_col.set_editor_property("constant", unreal.LinearColor(0.05, 0.05, 0.06, 1.0))
            unreal.MaterialEditingLibrary.connect_material_property(base_col, "", unreal.MaterialProperty.MP_BASE_COLOR)

            metallic = unreal.MaterialEditingLibrary.create_material_expression(mat, unreal.MaterialExpressionConstant, -250, 0)
            metallic.set_editor_property("r", 0.90)
            unreal.MaterialEditingLibrary.connect_material_property(metallic, "", unreal.MaterialProperty.MP_METALLIC)

            # Guía neón sutil y nítida (1.2x, agradable a la vista)
            emissive = unreal.MaterialEditingLibrary.create_material_expression(mat, unreal.MaterialExpressionConstant3Vector, -250, 150)
            emissive.set_editor_property("constant", unreal.LinearColor(0.0, 0.65, 0.90, 1.0) * 1.2)
            unreal.MaterialEditingLibrary.connect_material_property(emissive, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)

            unreal.MaterialEditingLibrary.recompile_material(mat)
            unreal.EditorAssetLibrary.save_loaded_asset(mat)
        except Exception as e:
            print(f">>> [FIX_LIVE] Aviso M_City_Neon_Guardrail: {e}")

    return mat

def fix():
    try:
        current_world = unreal.EditorLevelLibrary.get_editor_world()
        if not current_world or "L_RaceTrack_VR" not in current_world.get_path_name():
            unreal.EditorLevelLibrary.load_level("/Game/Maps/L_RaceTrack_VR")
    except Exception as e:
        print(f">>> [FIX_LIVE] Info nivel: {e}")

    print(">>> [FIX_LIVE] Iniciando configuración de Ciudad Completa, Tablero Elevado, 3-2-1 GO y Carril Suave...")

    # 1. Crear Materiales Esenciales
    true_glass = create_true_clear_glass()
    if not true_glass:
        true_glass = unreal.load_asset("/Game/Vehicles/Glass_-_Clear_001")

    # Hypercar Paints
    paint_gold   = create_colored_car_paint(1.00, 0.78, 0.02, "M_Paint_Gold_Hypercar")
    paint_cyan   = create_colored_car_paint(0.00, 0.85, 1.00, "M_Paint_Cyan_Electric")
    paint_lime   = create_colored_car_paint(0.12, 0.98, 0.12, "M_Paint_Lime_Sport")
    paint_orange = create_colored_car_paint(1.00, 0.35, 0.00, "M_Paint_Flame_Orange")
    paint_purple = create_colored_car_paint(0.70, 0.05, 0.98, "M_Paint_Cyber_Purple")
    paint_red    = create_colored_car_paint(0.95, 0.02, 0.02, "M_Paint_Rosso_Corsa")

    # City Balanced Architectural Materials (Elegantes, sin resplandor cegador)
    mat_tw_modern   = create_balanced_architectural_material(0.02, 0.03, 0.04, 0.90, 0.80, 0.60, 0.85, "M_City_Tower_Modern")
    mat_tw_cyan     = create_balanced_architectural_material(0.01, 0.03, 0.06, 0.10, 0.75, 0.95, 0.90, "M_City_Tower_CyberCyan")
    mat_tw_amber    = create_balanced_architectural_material(0.05, 0.03, 0.01, 0.95, 0.65, 0.15, 0.85, "M_City_Tower_Amber")
    mat_tw_magenta  = create_balanced_architectural_material(0.04, 0.01, 0.04, 0.85, 0.15, 0.70, 0.80, "M_City_Tower_Magenta")
    mat_res_warm    = create_balanced_architectural_material(0.09, 0.06, 0.05, 0.90, 0.82, 0.50, 0.75, "M_City_Residential_Warm")
    mat_res_cool    = create_balanced_architectural_material(0.08, 0.09, 0.11, 0.40, 0.75, 0.95, 0.75, "M_City_Residential_Cool")

    city_palette = [mat_tw_modern, mat_tw_cyan, mat_tw_amber, mat_tw_magenta, mat_res_warm, mat_res_cool]

    # Road & Barrier Materials
    asphalt_mat   = create_highway_asphalt()
    guardrail_mat = create_neon_guardrail()

    # Pre-existing mesh & material assets
    tire_mat      = unreal.load_asset("/Game/Vehicles/Tire")
    chrome_mat    = unreal.load_asset("/Game/Vehicles/Metal_-_Chrome")
    black_trim    = unreal.load_asset("/Game/Vehicles/Metal_-_Black_-_Rough_0_2")
    red_brake     = unreal.load_asset("/Game/Vehicles/Glass_-_Red")
    headlight     = unreal.load_asset("/Game/Vehicles/Glass_-_Clear_001")
    siren_red     = unreal.load_asset("/Game/Vehicles/Materials/M_Siren_Red")
    siren_blue    = unreal.load_asset("/Game/Vehicles/Materials/M_Siren_Blue")
    wheel_mesh    = unreal.load_asset("/Game/Vehicles/Meshes/SM_Steering_Wheel_Centered")
    wheel_mat     = unreal.load_asset("/Game/Vehicles/Materials/M_SteeringWheel_Alcantara")
    cube_mesh     = unreal.load_asset("/Engine/BasicShapes/Cube")
    plane_mesh    = unreal.load_asset("/Engine/BasicShapes/Plane")
    cylinder_mesh = unreal.load_asset("/Engine/BasicShapes/Cylinder")
    chassis_mesh  = unreal.load_asset("/Game/Vehicles/Meshes/SM_Merkurs_Chassis")

    # 2. Configurar el Asset Base SM_Merkurs_Chassis
    if chassis_mesh:
        try:
            for slot in [1, 16, 18, 19, 32, 42, 43]:
                if true_glass:
                    chassis_mesh.set_material(slot, true_glass)
            for decal_slot in [3, 5, 29, 44, 45]:
                if true_glass:
                    chassis_mesh.set_material(decal_slot, true_glass)
            if tire_mat:
                chassis_mesh.set_material(23, tire_mat)
            if chrome_mat:
                chassis_mesh.set_material(20, chrome_mat)
                chassis_mesh.set_material(24, chrome_mat)
                chassis_mesh.set_material(0, chrome_mat)
                chassis_mesh.set_material(12, chrome_mat)
            if red_brake:
                chassis_mesh.set_material(15, red_brake)
            if headlight:
                chassis_mesh.set_material(34, headlight)
            if black_trim:
                for b_slot in [4, 21, 26, 30, 40]:
                    chassis_mesh.set_material(b_slot, black_trim)
            if wheel_mat:
                for int_slot in [2, 7, 11, 39]:
                    chassis_mesh.set_material(int_slot, wheel_mat)

            unreal.EditorAssetLibrary.save_loaded_asset(chassis_mesh)
        except Exception as e:
            print(f">>> [FIX_LIVE] Aviso configurando SM_Merkurs_Chassis: {e}")

    all_actors = unreal.EditorLevelLibrary.get_all_level_actors()

    # 3. Iluminación Escénica de Atardecer / Noche Urbana (Cálida y Agradable para VR)
    sun_actor = None
    skylight_actor = None
    for a in all_actors:
        cls_name = a.get_class().get_name()
        lbl = a.get_actor_label()
        if "DirectionalLight" in cls_name or "Sun" in lbl:
            sun_actor = a
        elif "SkyLight" in cls_name or "Ambient" in lbl:
            skylight_actor = a

    if sun_actor:
        sun_actor.set_actor_rotation(unreal.Rotator(pitch=-24.0, yaw=42.0, roll=0.0), False)
        for c in sun_actor.get_components_by_class(unreal.DirectionalLightComponent):
            c.set_editor_property("intensity", 4.5)
            c.set_editor_property("light_color", unreal.Color(255, 210, 175, 255))
            c.set_editor_property("cast_shadows", True)

    if skylight_actor:
        for c in skylight_actor.get_components_by_class(unreal.SkyLightComponent):
            c.set_editor_property("intensity", 1.2)
            c.set_editor_property("light_color", unreal.Color(160, 190, 240, 255))

    # 4. Configurar Autopista Urbana y Muros Neón
    track_actor = None
    for a in all_actors:
        cls_name = a.get_class().get_name()
        lbl = a.get_actor_label()
        if "RaceTrackSpline" in cls_name or "RaceTrack_Circuit" in lbl:
            track_actor = a
            break

    spline_comp = None
    if track_actor:
        spline_comp = track_actor.get_component_by_class(unreal.SplineComponent)
        try:
            track_actor.set_editor_property("TrackWidth", 1400.0)
            track_actor.set_editor_property("WallHeight", 75.0)
            track_actor.set_editor_property("WallThickness", 35.0)
            track_actor.set_editor_property("SliceLength", 600.0)
            track_actor.set_editor_property("bGenerateGuardrails", True)
            track_actor.set_editor_property("bIsClosedLoop", True)
            if cube_mesh:
                track_actor.set_editor_property("RoadStaticMesh", cube_mesh)
                track_actor.set_editor_property("WallStaticMesh", cube_mesh)
            if asphalt_mat:
                track_actor.set_editor_property("RoadMaterial", asphalt_mat)
            if guardrail_mat:
                track_actor.set_editor_property("WallMaterial", guardrail_mat)
            track_actor.rerun_construction_scripts()
        except Exception as e:
            print(f">>> [FIX_LIVE] Aviso configurando pista: {e}")

    # Helper de posicionamiento sobre la pista
    def get_track_slot(dist_along, lateral_offset, height_above_track=0.0):
        if not spline_comp:
            return unreal.Vector(0,0,0), unreal.Rotator(0,0,0)
        spline_len = spline_comp.get_spline_length()
        d = dist_along % spline_len
        if d < 0:
            d += spline_len
        loc = spline_comp.get_location_at_distance_along_spline(d, unreal.SplineCoordinateSpace.WORLD)
        direction = spline_comp.get_direction_at_distance_along_spline(d, unreal.SplineCoordinateSpace.WORLD)
        right = spline_comp.get_right_vector_at_distance_along_spline(d, unreal.SplineCoordinateSpace.WORLD)
        target_pos = loc + (right * lateral_offset) + unreal.Vector(0, 0, height_above_track)
        yaw = math.degrees(math.atan2(direction.y, direction.x))
        pitch = math.degrees(math.atan2(direction.z, math.sqrt(direction.x**2 + direction.y**2)))
        target_rot = unreal.Rotator(pitch=pitch, yaw=yaw, roll=0.0)
        return target_pos, target_rot

    # 5. Generar Entorno Urbano Denso (46 Edificios y Casas en 3 Niveles de Profundidad)
    if cube_mesh and spline_comp:
        existing_buildings = [a for a in all_actors if "City_Skyscraper_" in a.get_actor_label() or "City_Building_" in a.get_actor_label()]
        spline_len = spline_comp.get_spline_length()
        total_structures = 44

        # Estructura urbana en 3 capas:
        # Capa 1 (Inmediata a la autopista): Casas y edificios comerciales medianos (25m - 45m de altura)
        # Capa 2 (Avenidas intermedias): Torres residenciales y oficinas (50m - 80m de altura)
        # Capa 3 (Skyline lejano): Rascacielos iluminados (90m - 140m de altura)
        for i in range(total_structures):
            b_label = f"City_Building_{i:02d}"
            b_actor = None
            for ex in existing_buildings:
                if ex.get_actor_label() == b_label:
                    b_actor = ex
                    break

            if not b_actor and i < len(existing_buildings):
                b_actor = existing_buildings[i]
                b_actor.set_actor_label(b_label)

            if not b_actor:
                b_actor = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(0,0,0))
                if b_actor:
                    b_actor.set_actor_label(b_label)

            if b_actor:
                tier = i % 3
                dist_pos = (i * (spline_len / float(total_structures))) + 600.0

                if tier == 0:
                    # Nivel 1: Casas / Bloques residenciales cercanos (a 26 metros de la autopista)
                    lat_side = 2600.0 if (i % 2 == 0) else -2600.0
                    h_scale = 30.0 + ((i * 7) % 25) # 30m a 55m de alto
                    w_x = 16.0 + ((i * 3) % 12)
                    w_y = 18.0 + ((i * 5) % 14)
                    mat = mat_res_warm if (i % 2 == 0) else mat_res_cool
                elif tier == 1:
                    # Nivel 2: Edificios comerciales medianos (a 52 metros de la autopista)
                    lat_side = 5200.0 if (i % 2 == 0) else -5200.0
                    h_scale = 60.0 + ((i * 11) % 35) # 60m a 95m de alto
                    w_x = 22.0 + ((i * 4) % 14)
                    w_y = 26.0 + ((i * 6) % 16)
                    mat = mat_tw_amber if (i % 2 == 0) else mat_tw_magenta
                else:
                    # Nivel 3: Rascacielos del skyline metropolitano (a 90 metros de la autopista)
                    lat_side = 9000.0 if (i % 2 == 0) else -9000.0
                    h_scale = 100.0 + ((i * 13) % 45) # 100m a 145m de alto
                    w_x = 28.0 + ((i * 5) % 15)
                    w_y = 32.0 + ((i * 7) % 18)
                    mat = mat_tw_modern if (i % 2 == 0) else mat_tw_cyan

                b_pos, b_rot = get_track_slot(dist_pos, lat_side, (h_scale * 50.0) - 25.0)
                b_actor.set_actor_location_and_rotation(b_pos, b_rot, False, False)

                for sm in b_actor.get_components_by_class(unreal.StaticMeshComponent):
                    sm.set_editor_property("static_mesh", cube_mesh)
                    sm.set_world_scale3d(unreal.Vector(w_x, w_y, h_scale))
                    if mat:
                        sm.set_material(0, mat)

        print(">>> [FIX_LIVE] Entorno urbano multicapa generado con 44 edificios y casas de variada altura.")

    # 6. Grilla de Vehículos Hipercar y Patrullas
    racer_grid = {
        "Player_VrVehicle":             {"dist": 1200.0, "offset": -160.0, "color": paint_red},
        "Rival_Racer_5":                {"dist": 1800.0, "offset": 160.0,  "color": paint_purple, "speed": 135.0},
        "Rival_Racer_4":                {"dist": 2300.0, "offset": -160.0, "color": paint_orange, "speed": 145.0},
        "Rival_Racer_3":                {"dist": 2900.0, "offset": 160.0,  "color": paint_lime,   "speed": 155.0},
        "Rival_Racer_2":                {"dist": 3400.0, "offset": -160.0, "color": paint_cyan,   "speed": 165.0},
        "Rival_Racer_1":                {"dist": 4000.0, "offset": 160.0,  "color": paint_gold,   "speed": 175.0},
        # Patrullas Parqueadas en la Banquina:
        "Police_Pursuit_Interceptor_1": {"dist": 18000.0, "offset": 540.0,  "is_parked": True},
        "Police_Pursuit_Interceptor_2": {"dist": 38000.0, "offset": -540.0, "is_parked": True},
        "Police_Pursuit_Interceptor_3": {"dist": 62000.0, "offset": 540.0,  "is_parked": True},
    }

    def apply_hypercar_livery(comp, body_paint):
        if not comp:
            return
        if chassis_mesh:
            comp.set_editor_property("static_mesh", chassis_mesh)
            comp.set_relative_location(unreal.Vector(0.0, 0.0, 0.0), False, False)
            comp.set_relative_rotation(unreal.Rotator(pitch=0.0, yaw=180.0, roll=0.0), False, False)
            comp.set_relative_scale3d(unreal.Vector(1.0, 1.0, 1.0))

        if body_paint:
            comp.set_material(17, body_paint)
            comp.set_material(27, body_paint)
            comp.set_material(41, body_paint)
        
        if true_glass:
            for ds in [3, 5, 29, 44, 45, 1, 16, 18, 19, 32, 42, 43]:
                try:
                    comp.set_material(ds, true_glass)
                except:
                    pass
        if tire_mat:
            comp.set_material(23, tire_mat)
        if chrome_mat:
            comp.set_material(20, chrome_mat)
            comp.set_material(24, chrome_mat)
        if red_brake:
            comp.set_material(15, red_brake)
        if headlight:
            comp.set_material(34, headlight)
        if black_trim:
            for bs in [4, 21, 26, 30, 40]:
                try:
                    comp.set_material(bs, black_trim)
                except:
                    pass

    # 7. Configuración de Actores del Nivel
    all_actors = unreal.EditorLevelLibrary.get_all_level_actors()
    for a in all_actors:
        lbl = a.get_actor_label()
        cls = a.get_class().get_name()

        if lbl in racer_grid:
            grid_info = racer_grid[lbl]
            new_loc, new_rot = get_track_slot(grid_info["dist"], grid_info["offset"], 0.0)
            a.set_actor_location_and_rotation(new_loc, new_rot, False, False)

        if "Rival" in lbl and lbl in racer_grid:
            paint = racer_grid[lbl].get("color", paint_gold)
            for c in a.get_components_by_class(unreal.StaticMeshComponent):
                if "ChassisMeshComponent" in c.get_name():
                    apply_hypercar_livery(c, paint)

        elif "Police" in lbl:
            try:
                a.set_editor_property("bIsParkedAmbush", True)
                a.set_editor_property("AmbushTriggerDistance", 3500.0)
            except:
                pass

            for c in a.get_components_by_class(unreal.StaticMeshComponent):
                c_name = c.get_name()
                if "ChassisMeshComponent" in c_name:
                    apply_hypercar_livery(c, black_trim)
                    if chrome_mat:
                        c.set_material(27, chrome_mat)
                elif "RedSirenMesh" in c_name:
                    c.set_relative_location(unreal.Vector(0.0, -25.0, 128.0), False, False)
                    if siren_red:
                        c.set_material(0, siren_red)
                elif "BlueSirenMesh" in c_name:
                    c.set_relative_location(unreal.Vector(0.0, 25.0, 128.0), False, False)
                    if siren_blue:
                        c.set_material(0, siren_blue)

        elif lbl == "Player_VrVehicle" or ("BP_VrVehiclePawn" in cls and "Rival" not in lbl):
            a.set_editor_property("auto_possess_player", unreal.AutoReceiveInput.PLAYER0)
            try:
                a.set_editor_property("BustedTimeLimit", 20.0)
            except:
                pass

            # Chasis y Componentes Físicos del Cockpit
            for c in a.get_components_by_class(unreal.StaticMeshComponent):
                c_name = c.get_name()
                if "ChassisMeshComponent" in c_name:
                    apply_hypercar_livery(c, paint_red)

                # Tablero elevado por encima del capó
                elif "DashboardBackplateMesh" in c_name:
                    c.set_relative_location(unreal.Vector(42.0, 0.0, -2.5), False, False)
                    c.set_relative_rotation(unreal.Rotator(pitch=-15.0, yaw=0.0, roll=0.0), False, False)
                    c.set_relative_scale3d(unreal.Vector(0.015, 0.40, 0.14))
                    if wheel_mat:
                        c.set_material(0, wheel_mat)

                elif "DashboardWoodTrimMesh" in c_name:
                    c.set_relative_location(unreal.Vector(44.0, 18.0, -1.0), False, False)
                    c.set_relative_rotation(unreal.Rotator(pitch=-12.0, yaw=0.0, roll=0.0), False, False)
                    c.set_relative_scale3d(unreal.Vector(0.06, 1.10, 0.035))
                    if wheel_mat:
                        c.set_material(0, wheel_mat)

                elif "AmbientLightStripMesh" in c_name:
                    c.set_relative_location(unreal.Vector(43.2, 18.0, -2.8), False, False)
                    c.set_relative_rotation(unreal.Rotator(pitch=-12.0, yaw=0.0, roll=0.0), False, False)
                    c.set_relative_scale3d(unreal.Vector(0.012, 1.10, 0.012))
                    if siren_red:
                        c.set_material(0, siren_red)

                elif "CentralTouchscreenMesh" in c_name:
                    c.set_relative_location(unreal.Vector(0.0, 0.0, 0.0), False, False)
                    c.set_relative_rotation(unreal.Rotator(pitch=0.0, yaw=0.0, roll=0.0), False, False)
                    c.set_relative_scale3d(unreal.Vector(0.012, 0.28, 0.16))
                    if wheel_mat:
                        c.set_material(0, wheel_mat)

                elif "SteeringWheelVisualMesh" in c_name:
                    c.set_relative_location(unreal.Vector(0.0, 0.0, 0.0), False, False)
                    c.set_relative_rotation(unreal.Rotator(pitch=0.0, yaw=0.0, roll=0.0), False, False)
                    c.set_relative_scale3d(unreal.Vector(95.0, 95.0, 95.0))
                    if wheel_mesh:
                        c.set_editor_property("static_mesh", wheel_mesh)
                    if wheel_mat:
                        c.set_material(0, wheel_mat)

            # Posición de Cámara y Anclajes del Cockpit
            for c in a.get_components_by_class(unreal.SceneComponent):
                c_name = c.get_name()
                if "CockpitRoot" in c_name:
                    c.set_relative_location(unreal.Vector(42.0, -36.0, 120.0), False, False)
                    c.set_relative_rotation(unreal.Rotator(pitch=-11.0, yaw=0.0, roll=0.0), False, False)
                elif "CentralDisplayAnchor" in c_name:
                    c.set_relative_location(unreal.Vector(48.0, 32.0, -36.0), False, False)
                    c.set_relative_rotation(unreal.Rotator(pitch=-15.0, yaw=-22.0, roll=0.0), False, False)
                elif "SteeringWheelComponent" in c_name and not isinstance(c, unreal.StaticMeshComponent):
                    c.set_relative_location(unreal.Vector(34.0, 0.0, -12.0), False, False)
                    c.set_relative_rotation(unreal.Rotator(pitch=-18.0, yaw=0.0, roll=0.0), False, False)

            # Textos Digitales del Tablero ELEVADOS Y 100% VISIBLES
            for c in a.get_components_by_class(unreal.TextRenderComponent):
                c_name = c.get_name()
                if "SpeedTextRender" in c_name:
                    c.set_relative_location(unreal.Vector(40.5, 0.0, -2.5), False, False)
                    c.set_relative_rotation(unreal.Rotator(pitch=-15.0, yaw=180.0, roll=0.0), False, False)
                    c.set_text(unreal.Text("0 KM/H"))
                    c.set_world_size(3.6)
                    c.set_text_render_color(unreal.Color(0, 245, 255, 255))
                elif "GearTextRender" in c_name:
                    c.set_relative_location(unreal.Vector(40.5, 10.0, 1.8), False, False)
                    c.set_relative_rotation(unreal.Rotator(pitch=-15.0, yaw=180.0, roll=0.0), False, False)
                    c.set_text(unreal.Text("GEAR: 1"))
                    c.set_world_size(2.2)
                    c.set_text_render_color(unreal.Color(255, 140, 0, 255))
                elif "PositionTextRender" in c_name:
                    c.set_relative_location(unreal.Vector(40.5, -10.0, 1.8), False, False)
                    c.set_relative_rotation(unreal.Rotator(pitch=-15.0, yaw=180.0, roll=0.0), False, False)
                    c.set_text(unreal.Text("POS: P4/7"))
                    c.set_world_size(2.2)
                    c.set_text_render_color(unreal.Color(255, 215, 0, 255))
                elif "PoliceAlertTextRender" in c_name:
                    c.set_relative_location(unreal.Vector(40.5, 0.0, -6.8), False, False)
                    c.set_relative_rotation(unreal.Rotator(pitch=-15.0, yaw=180.0, roll=0.0), False, False)
                    c.set_text(unreal.Text("/// PREPARADO ///"))
                    c.set_world_size(1.8)
                    c.set_text_render_color(unreal.Color(0, 255, 128, 255))

    # 8. Guardar Nivel
    try:
        unreal.EditorLevelLibrary.save_current_level()
        print(">>> [FIX_LIVE] Nivel guardado con éxito. Ciudad completa y tablero visible.")
    except Exception as e:
        print(f">>> [FIX_LIVE] Error guardando nivel: {e}")

if __name__ == "__main__":
    fix()
