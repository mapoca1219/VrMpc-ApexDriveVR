import unreal
import math

def setup_soft_building_material(mat_name, base_color, win_color, emissive_mult=0.28):
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

            # Fachada arquitectónica elegante y oscura (vidrio reflectante / concreto urbano)
            base_node = unreal.MaterialEditingLibrary.create_material_expression(mat, unreal.MaterialExpressionConstant3Vector, -350, -100)
            base_node.set_editor_property("constant", base_color)
            unreal.MaterialEditingLibrary.connect_material_property(base_node, "", unreal.MaterialProperty.MP_BASE_COLOR)

            # Acabado metálico arquitectónico
            metallic = unreal.MaterialEditingLibrary.create_material_expression(mat, unreal.MaterialExpressionConstant, -350, 0)
            metallic.set_editor_property("r", 0.75)
            unreal.MaterialEditingLibrary.connect_material_property(metallic, "", unreal.MaterialProperty.MP_METALLIC)

            # Rugosidad para reflejos nítidos de atardecer
            roughness = unreal.MaterialEditingLibrary.create_material_expression(mat, unreal.MaterialExpressionConstant, -350, 70)
            roughness.set_editor_property("r", 0.28)
            unreal.MaterialEditingLibrary.connect_material_property(roughness, "", unreal.MaterialProperty.MP_ROUGHNESS)

            # Ventanales con luz suave y agradable (0.25x a 0.35x: CERO fatiga visual, NO cegador)
            emissive = unreal.MaterialEditingLibrary.create_material_expression(mat, unreal.MaterialExpressionConstant3Vector, -350, 180)
            soft_glow = unreal.LinearColor(win_color.r * emissive_mult, win_color.g * emissive_mult, win_color.b * emissive_mult, 1.0)
            emissive.set_editor_property("constant", soft_glow)
            unreal.MaterialEditingLibrary.connect_material_property(emissive, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)

            unreal.MaterialEditingLibrary.recompile_material(mat)
            unreal.EditorAssetLibrary.save_loaded_asset(mat)
            print(f">>> [CITY] Material arquitectónico configurado: {mat_name}")
        except Exception as e:
            print(f">>> [CITY] Error en {mat_name}: {e}")

    return mat

def run():
    print(">>> ===================================================")
    print(">>> [CITY_UPDATE] CONFIGURANDO CIUDAD ELEGANTE Y CONFORTABLE")
    print(">>> ===================================================")

    # 1. Crear materiales de edificios y casas suaves (sin brillo excesivo)
    mat_tower_warm = setup_soft_building_material(
        "M_City_Tower_Amber",
        unreal.LinearColor(0.04, 0.045, 0.05, 1.0),
        unreal.LinearColor(1.0, 0.85, 0.55, 1.0),
        0.30
    )
    mat_tower_cyan = setup_soft_building_material(
        "M_City_Tower_CyberCyan",
        unreal.LinearColor(0.035, 0.04, 0.055, 1.0),
        unreal.LinearColor(0.25, 0.70, 0.95, 1.0),
        0.28
    )
    mat_tower_modern = setup_soft_building_material(
        "M_City_Tower_Modern",
        unreal.LinearColor(0.05, 0.05, 0.055, 1.0),
        unreal.LinearColor(0.85, 0.90, 1.0, 1.0),
        0.25
    )
    mat_tower_magenta = setup_soft_building_material(
        "M_City_Tower_Magenta",
        unreal.LinearColor(0.04, 0.035, 0.045, 1.0),
        unreal.LinearColor(0.95, 0.50, 0.75, 1.0),
        0.28
    )
    mat_house_warm = setup_soft_building_material(
        "M_City_Residential_Warm",
        unreal.LinearColor(0.08, 0.06, 0.05, 1.0),
        unreal.LinearColor(1.0, 0.75, 0.40, 1.0),
        0.22
    )
    mat_house_cool = setup_soft_building_material(
        "M_City_Residential_Cool",
        unreal.LinearColor(0.06, 0.07, 0.08, 1.0),
        unreal.LinearColor(0.70, 0.85, 1.0, 1.0),
        0.22
    )

    # Cargar materiales de pista y vehículos
    asphalt_mat = unreal.EditorAssetLibrary.load_asset("/Game/LevelPrototyping/Materials/M_City_Highway_Asphalt")
    guardrail_mat = unreal.EditorAssetLibrary.load_asset("/Game/LevelPrototyping/Materials/M_City_NeonCyan")
    cube_mesh = unreal.EditorAssetLibrary.load_asset("/Engine/BasicShapes/Cube")

    # Cargar nivel
    level_path = "/Game/Maps/L_RaceTrack_VR"
    unreal.EditorLevelLibrary.load_level(level_path)
    all_actors = unreal.EditorLevelLibrary.get_all_level_actors()

    # 2. Configurar Iluminación de Atardecer Relajante
    for a in all_actors:
        cls_name = a.get_class().get_name()
        lbl = a.get_actor_label()
        if "DirectionalLight" in cls_name or "Sun" in lbl:
            a.set_actor_rotation(unreal.Rotator(pitch=-24.0, yaw=42.0, roll=0.0), False)
            for c in a.get_components_by_class(unreal.DirectionalLightComponent):
                c.set_editor_property("intensity", 4.2)
                c.set_editor_property("light_color", unreal.Color(255, 215, 180, 255))
        elif "SkyLight" in cls_name or "Ambient" in lbl:
            for c in a.get_components_by_class(unreal.SkyLightComponent):
                c.set_editor_property("intensity", 1.2)
                c.set_editor_property("light_color", unreal.Color(165, 195, 240, 255))

    # 3. Configurar Autopista y Muros
    track_actor = None
    for a in all_actors:
        lbl = a.get_actor_label()
        if "RaceTrackSpline" in a.get_class().get_name() or "RaceTrack_Circuit" in lbl:
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
            print(">>> [CITY] Autopista y muros reconstruidos con asfalto y neón")
        except Exception as e:
            print(f">>> [CITY] Error configurando pista: {e}")

    # Helper de ubicación a lo largo de la pista
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

    # 4. Crear Ciudad Multi-Nivel con Casas y Rascacielos
    if cube_mesh and spline_comp:
        existing_buildings = [a for a in all_actors if "City_Skyscraper_" in a.get_actor_label() or "City_Building_" in a.get_actor_label()]
        spline_len = spline_comp.get_spline_length()
        total_structures = 44

        materials_palette = [
            mat_tower_warm,
            mat_tower_cyan,
            mat_tower_modern,
            mat_tower_magenta,
            mat_house_warm,
            mat_house_cool
        ]

        for i in range(total_structures):
            b_label = f"City_Building_{i:02d}"
            b_actor = None
            for ex in existing_buildings:
                if ex.get_actor_label() == b_label:
                    b_actor = ex
                    break

            if not b_actor and i < len(existing_buildings):
                b_actor = existing_buildings[i]

            if not b_actor:
                b_actor = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(0,0,0))
                if b_actor:
                    b_actor.set_actor_label(b_label)

            if not b_actor:
                continue

            # Distribución en 3 niveles de profundidad
            fraction = i / float(total_structures)
            dist_along = fraction * spline_len
            side = 1.0 if (i % 2 == 0) else -1.0
            tier = i % 3

            if tier == 0:
                # Nivel 1: Casas y comercios bajos (18m - 32m de alto, a 28m de la pista)
                lateral_offset = side * (1800.0 + (i % 4) * 250.0)
                width = 16.0 + (i % 3) * 4.0
                depth = 16.0 + (i % 2) * 5.0
                height = 18.0 + (i % 5) * 3.5
                assigned_mat = mat_house_warm if (i % 4 == 0) else mat_house_cool
            elif tier == 1:
                # Nivel 2: Edificios comerciales y torres medianas (45m - 75m de alto, a 55m de la pista)
                lateral_offset = side * (4200.0 + (i % 5) * 350.0)
                width = 24.0 + (i % 3) * 6.0
                depth = 24.0 + (i % 2) * 8.0
                height = 45.0 + (i % 7) * 4.5
                assigned_mat = mat_tower_warm if (i % 2 == 0) else mat_tower_modern
            else:
                # Nivel 3: Skyline de rascacielos iluminados (85m - 130m de alto, a 95m de la pista)
                lateral_offset = side * (8500.0 + (i % 6) * 500.0)
                width = 32.0 + (i % 4) * 8.0
                depth = 32.0 + (i % 3) * 10.0
                height = 85.0 + (i % 8) * 6.0
                assigned_mat = mat_tower_cyan if (i % 2 == 0) else mat_tower_magenta

            pos, rot = get_track_slot(dist_along, lateral_offset, height * 50.0 - 50.0)
            b_actor.set_actor_location_and_rotation(pos, rot, False, False)

            sm_comp = b_actor.get_component_by_class(unreal.StaticMeshComponent)
            if sm_comp:
                sm_comp.set_editor_property("static_mesh", cube_mesh)
                sm_comp.set_world_scale3d(unreal.Vector(width, depth, height))
                if assigned_mat:
                    sm_comp.set_material(0, assigned_mat)

        print(f">>> [CITY] 44 estructuras multi-nivel (casas y rascacielos) configuradas")

    # 5. Guardar nivel
    unreal.EditorLevelLibrary.save_current_level()
    print(">>> [CITY_UPDATE] Nivel L_RaceTrack_VR guardado con éxito")

if __name__ == "__main__":
    run()
