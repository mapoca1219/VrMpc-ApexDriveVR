import unreal
import math

def create_windowed_material(mat_name, base_color, win_color, emissive_scale, u_tile, v_tile, metallic=0.75, roughness=0.28):
    pkg_path = "/Game/LevelPrototyping/Materials"
    full_path = f"{pkg_path}/{mat_name}"
    
    if unreal.EditorAssetLibrary.does_asset_exist(full_path):
        mat = unreal.EditorAssetLibrary.load_asset(full_path)
    else:
        mat = unreal.AssetToolsHelpers.get_asset_tools().create_asset(mat_name, pkg_path, unreal.Material, unreal.MaterialFactoryNew())
    
    if not mat:
        print(f"Failed to load or create material: {mat_name}")
        return None
        
    try:
        unreal.MaterialEditingLibrary.delete_all_material_expressions(mat)
        
        # 1. Coordenadas de Mapeo UV (Tiling de Ventanas)
        tex_coord = unreal.MaterialEditingLibrary.create_material_expression(mat, unreal.MaterialExpressionTextureCoordinate, -800, 50)
        tex_coord.set_editor_property("utiling", float(u_tile))
        tex_coord.set_editor_property("vtiling", float(v_tile))
        
        # 2. Textura de rejilla arquitectónica (Marcos vs Paneles de Ventana)
        tex_sample = unreal.MaterialEditingLibrary.create_material_expression(mat, unreal.MaterialExpressionTextureSample, -580, 50)
        grid_tex = unreal.EditorAssetLibrary.load_asset("/Game/LevelPrototyping/Textures/T_GridChecker_A")
        tex_sample.set_editor_property("texture", grid_tex)
        unreal.MaterialEditingLibrary.connect_material_expressions(tex_coord, "", tex_sample, "UVs")
        
        # 3. Color Base de la Fachada (Concreto arquitectónico / Paneles oscuros)
        base_node = unreal.MaterialEditingLibrary.create_material_expression(mat, unreal.MaterialExpressionConstant3Vector, -580, -220)
        base_node.set_editor_property("constant", base_color)
        unreal.MaterialEditingLibrary.connect_material_property(base_node, "", unreal.MaterialProperty.MP_BASE_COLOR)
        
        # 4. Color y Resplandor de Ventanas Iluminadas
        win_color_node = unreal.MaterialEditingLibrary.create_material_expression(mat, unreal.MaterialExpressionConstant3Vector, -380, 180)
        win_color_node.set_editor_property("constant", win_color)
        
        mul_color = unreal.MaterialEditingLibrary.create_material_expression(mat, unreal.MaterialExpressionMultiply, -180, 100)
        unreal.MaterialEditingLibrary.connect_material_expressions(tex_sample, "R", mul_color, "A")
        unreal.MaterialEditingLibrary.connect_material_expressions(win_color_node, "", mul_color, "B")
        
        scale_node = unreal.MaterialEditingLibrary.create_material_expression(mat, unreal.MaterialExpressionConstant, -180, 240)
        scale_node.set_editor_property("r", float(emissive_scale))
        
        mul_emissive = unreal.MaterialEditingLibrary.create_material_expression(mat, unreal.MaterialExpressionMultiply, 20, 150)
        unreal.MaterialEditingLibrary.connect_material_expressions(mul_color, "", mul_emissive, "A")
        unreal.MaterialEditingLibrary.connect_material_expressions(scale_node, "", mul_emissive, "B")
        unreal.MaterialEditingLibrary.connect_material_property(mul_emissive, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
        
        # 5. Acabado Metálico y Rugosidad para Reflejos Elegantes de Atardecer
        metal_node = unreal.MaterialEditingLibrary.create_material_expression(mat, unreal.MaterialExpressionConstant, -180, -100)
        metal_node.set_editor_property("r", float(metallic))
        unreal.MaterialEditingLibrary.connect_material_property(metal_node, "", unreal.MaterialProperty.MP_METALLIC)
        
        rough_node = unreal.MaterialEditingLibrary.create_material_expression(mat, unreal.MaterialExpressionConstant, -180, -30)
        rough_node.set_editor_property("r", float(roughness))
        unreal.MaterialEditingLibrary.connect_material_property(rough_node, "", unreal.MaterialProperty.MP_ROUGHNESS)
        
        unreal.MaterialEditingLibrary.recompile_material(mat)
        unreal.EditorAssetLibrary.save_loaded_asset(mat)
        print(f">>> [MAT] Material de ventana creado con exito: {mat_name}")
    except Exception as e:
        print(f">>> [MAT] Error configurando {mat_name}: {e}")
        
    return mat

def create_solid_architectural_material(mat_name, base_color, roughness=0.8, metallic=0.0):
    pkg_path = "/Game/LevelPrototyping/Materials"
    full_path = f"{pkg_path}/{mat_name}"
    
    if unreal.EditorAssetLibrary.does_asset_exist(full_path):
        mat = unreal.EditorAssetLibrary.load_asset(full_path)
    else:
        mat = unreal.AssetToolsHelpers.get_asset_tools().create_asset(mat_name, pkg_path, unreal.Material, unreal.MaterialFactoryNew())
        
    if mat:
        try:
            unreal.MaterialEditingLibrary.delete_all_material_expressions(mat)
            
            base_node = unreal.MaterialEditingLibrary.create_material_expression(mat, unreal.MaterialExpressionConstant3Vector, -300, -100)
            base_node.set_editor_property("constant", base_color)
            unreal.MaterialEditingLibrary.connect_material_property(base_node, "", unreal.MaterialProperty.MP_BASE_COLOR)
            
            rough_node = unreal.MaterialEditingLibrary.create_material_expression(mat, unreal.MaterialExpressionConstant, -300, 50)
            rough_node.set_editor_property("r", float(roughness))
            unreal.MaterialEditingLibrary.connect_material_property(rough_node, "", unreal.MaterialProperty.MP_ROUGHNESS)
            
            metal_node = unreal.MaterialEditingLibrary.create_material_expression(mat, unreal.MaterialExpressionConstant, -300, 150)
            metal_node.set_editor_property("r", float(metallic))
            unreal.MaterialEditingLibrary.connect_material_property(metal_node, "", unreal.MaterialProperty.MP_METALLIC)
            
            unreal.MaterialEditingLibrary.recompile_material(mat)
            unreal.EditorAssetLibrary.save_loaded_asset(mat)
            print(f">>> [MAT] Material solido arquitectonico creado: {mat_name}")
        except Exception as e:
            print(f">>> [MAT] Error en {mat_name}: {e}")
            
    return mat

def run():
    print("==========================================================")
    print(">>> GENERANDO METROPOLIS URBANA CON CASAS Y RASCACIELOS <<<")
    print("==========================================================")
    
    # 1. Crear materiales de fachadas con ventanales iluminados
    mat_win_amber = create_windowed_material(
        "M_City_Window_WarmAmber",
        unreal.LinearColor(0.04, 0.042, 0.048, 1.0),
        unreal.LinearColor(1.0, 0.82, 0.42, 1.0),
        0.35, u_tile=8.0, v_tile=20.0, metallic=0.75, roughness=0.28
    )
    mat_win_cyan = create_windowed_material(
        "M_City_Window_CyberCyan",
        unreal.LinearColor(0.035, 0.04, 0.055, 1.0),
        unreal.LinearColor(0.20, 0.75, 1.0, 1.0),
        0.32, u_tile=10.0, v_tile=28.0, metallic=0.85, roughness=0.22
    )
    mat_win_white = create_windowed_material(
        "M_City_Window_ModernWhite",
        unreal.LinearColor(0.05, 0.05, 0.055, 1.0),
        unreal.LinearColor(0.92, 0.95, 1.0, 1.0),
        0.30, u_tile=6.0, v_tile=14.0, metallic=0.70, roughness=0.32
    )
    mat_win_res = create_windowed_material(
        "M_City_Window_ResidentialWarm",
        unreal.LinearColor(0.07, 0.06, 0.05, 1.0),
        unreal.LinearColor(1.0, 0.75, 0.38, 1.0),
        0.38, u_tile=4.0, v_tile=3.0, metallic=0.15, roughness=0.55
    )
    mat_roof = create_solid_architectural_material(
        "M_City_Roof_Shingle",
        unreal.LinearColor(0.09, 0.055, 0.045, 1.0),
        roughness=0.85, metallic=0.05
    )
    mat_pedestal = create_solid_architectural_material(
        "M_City_Concrete_Pedestal",
        unreal.LinearColor(0.055, 0.055, 0.06, 1.0),
        roughness=0.75, metallic=0.2
    )
    
    # 2. Cargar Mallas
    mesh_chamfer = unreal.EditorAssetLibrary.load_asset("/Game/LevelPrototyping/Meshes/SM_ChamferCube")
    mesh_ramp = unreal.EditorAssetLibrary.load_asset("/Game/LevelPrototyping/Meshes/SM_Ramp")
    mesh_cylinder = unreal.EditorAssetLibrary.load_asset("/Game/LevelPrototyping/Meshes/SM_Cylinder")
    mesh_cube = unreal.EditorAssetLibrary.load_asset("/Engine/BasicShapes/Cube")
    
    # Cargar nivel
    level_path = "/Game/Maps/L_RaceTrack_VR"
    unreal.EditorLevelLibrary.load_level(level_path)
    all_actors = unreal.EditorLevelLibrary.get_all_level_actors()
    
    # 3. Localizar la Pista (RaceTrackSpline)
    spline_comp = None
    for a in all_actors:
        lbl = a.get_actor_label()
        if "RaceTrackSpline" in a.get_class().get_name() or "RaceTrack_Circuit" in lbl:
            spline_comp = a.get_component_by_class(unreal.SplineComponent)
            break
            
    if not spline_comp:
        print(">>> ERROR: No se encontró el Spline de la pista!")
        return
        
    spline_len = spline_comp.get_spline_length()
    print(f">>> Longitud del circuito: {spline_len:.1f} unidades")
    
    # 4. Limpiar antiguos cubos y monolitos
    actors_to_remove = []
    for a in all_actors:
        lbl = a.get_actor_label()
        if any(lbl.startswith(prefix) for prefix in ["Skyline_Tower_", "City_Building_", "City_House_", "City_Skyscraper_"]):
            actors_to_remove.append(a)
            
    print(f">>> Eliminando {len(actors_to_remove)} monolitos y cubos antiguos...")
    for a in actors_to_remove:
        unreal.EditorLevelLibrary.destroy_actor(a)
        
    # Helper para posicionamiento en la pista
    def get_slot(dist, lat_offset, z_offset=0.0):
        d = dist % spline_len
        loc = spline_comp.get_location_at_distance_along_spline(d, unreal.SplineCoordinateSpace.WORLD)
        direction = spline_comp.get_direction_at_distance_along_spline(d, unreal.SplineCoordinateSpace.WORLD)
        right = spline_comp.get_right_vector_at_distance_along_spline(d, unreal.SplineCoordinateSpace.WORLD)
        pos = loc + (right * lat_offset) + unreal.Vector(0, 0, z_offset)
        yaw = math.degrees(math.atan2(direction.y, direction.x))
        rot = unreal.Rotator(pitch=0.0, yaw=yaw, roll=0.0)
        return pos, rot
        
    # 5. Generar 64 Estructuras Urbanas Variadas (Casas, Edificios Comerciales y Rascacielos)
    total_structures = 64
    spawned_count = 0
    
    for i in range(total_structures):
        fraction = i / float(total_structures)
        dist_along = fraction * spline_len
        side = 1.0 if (i % 2 == 0) else -1.0
        
        # Ciclo de tipologías:
        # i % 4 == 0 o 1: Casa Residencial (Cerca a la pista, tejado a dos aguas)
        # i % 4 == 2: Edificio Comercial / Oficinas (Distancia media, escalonado)
        # i % 4 == 3: Rascacielos / Megatorre (Fondo / Skyline alto)
        structure_type = i % 4
        
        if structure_type in [0, 1]:
            # === CASA RESIDENCIAL CON TEJADO ===
            lat_dist = side * (1900.0 + (i % 3) * 350.0)
            house_w = 11.0 + (i % 2) * 3.0  # 11m a 14m
            house_d = 12.0 + (i % 3) * 2.5  # 12m a 17m
            house_h = 7.0 + (i % 2) * 1.5   # 7m a 8.5m
            roof_h = 3.8
            
            # Base de la casa (Z de centro = house_h * 50)
            base_pos, rot = get_slot(dist_along, lat_dist, z_offset=(house_h * 50.0) - 40.0)
            base_actor = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.StaticMeshActor, base_pos, rot)
            if base_actor:
                base_actor.set_actor_label(f"City_House_{i:02d}_Base")
                sm = base_actor.get_component_by_class(unreal.StaticMeshComponent)
                if sm:
                    sm.set_editor_property("static_mesh", mesh_chamfer)
                    sm.set_world_scale3d(unreal.Vector(house_w, house_d, house_h))
                    sm.set_material(0, mat_win_res)
                    
            # Tejado de la casa (SM_Ramp colocado arriba)
            roof_pos, roof_rot = get_slot(dist_along, lat_dist, z_offset=(house_h * 100.0) + (roof_h * 50.0) - 40.0)
            roof_actor = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.StaticMeshActor, roof_pos, rot)
            if roof_actor:
                roof_actor.set_actor_label(f"City_House_{i:02d}_Roof")
                sm_roof = roof_actor.get_component_by_class(unreal.StaticMeshComponent)
                if sm_roof:
                    sm_roof.set_editor_property("static_mesh", mesh_ramp)
                    sm_roof.set_world_scale3d(unreal.Vector(house_w, house_d, roof_h))
                    sm_roof.set_material(0, mat_roof)
                    
            spawned_count += 2
            
        elif structure_type == 2:
            # === EDIFICIO COMERCIAL / OFICINAS (NIVEL MEDIO) ===
            lat_dist = side * (3800.0 + (i % 4) * 450.0)
            b_w = 20.0 + (i % 3) * 5.0
            b_d = 20.0 + (i % 2) * 6.0
            b_h = 38.0 + (i % 5) * 5.0  # 38m a 58m de altura
            
            base_pos, rot = get_slot(dist_along, lat_dist, z_offset=(b_h * 50.0) - 50.0)
            b_actor = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.StaticMeshActor, base_pos, rot)
            if b_actor:
                b_actor.set_actor_label(f"City_Commercial_{i:02d}")
                sm = b_actor.get_component_by_class(unreal.StaticMeshComponent)
                if sm:
                    sm.set_editor_property("static_mesh", mesh_chamfer)
                    sm.set_world_scale3d(unreal.Vector(b_w, b_d, b_h))
                    assigned_mat = mat_win_white if (i % 2 == 0) else mat_win_amber
                    sm.set_material(0, assigned_mat)
                    
            # Setback / Corona en la azotea (penthouse de oficinas)
            crown_w = b_w * 0.65
            crown_d = b_d * 0.65
            crown_h = 10.0
            crown_pos, crown_rot = get_slot(dist_along, lat_dist, z_offset=(b_h * 100.0) + (crown_h * 50.0) - 50.0)
            crown_actor = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.StaticMeshActor, crown_pos, rot)
            if crown_actor:
                crown_actor.set_actor_label(f"City_Commercial_{i:02d}_Crown")
                sm_crown = crown_actor.get_component_by_class(unreal.StaticMeshComponent)
                if sm_crown:
                    sm_crown.set_editor_property("static_mesh", mesh_chamfer)
                    sm_crown.set_world_scale3d(unreal.Vector(crown_w, crown_d, crown_h))
                    sm_crown.set_material(0, mat_pedestal)
                    
            spawned_count += 2
            
        else:
            # === RASCACIELOS / MEGATORRE (SKYLINE FONDO) ===
            lat_dist = side * (7500.0 + (i % 5) * 800.0)
            t_w = 28.0 + (i % 4) * 6.0
            t_d = 28.0 + (i % 3) * 8.0
            t_h = 75.0 + (i % 7) * 9.0  # 75m a 130m de altura
            
            t_pos, rot = get_slot(dist_along, lat_dist, z_offset=(t_h * 50.0) - 50.0)
            t_actor = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.StaticMeshActor, t_pos, rot)
            if t_actor:
                t_actor.set_actor_label(f"City_Skyscraper_{i:02d}")
                sm = t_actor.get_component_by_class(unreal.StaticMeshComponent)
                if sm:
                    sm.set_editor_property("static_mesh", mesh_chamfer)
                    sm.set_world_scale3d(unreal.Vector(t_w, t_d, t_h))
                    assigned_mat = mat_win_cyan if (i % 3 == 0) else (mat_win_amber if (i % 3 == 1) else mat_win_white)
                    sm.set_material(0, assigned_mat)
                    
            # Antena o mirador cilíndrico en la cima
            spire_h = 16.0
            spire_pos, _ = get_slot(dist_along, lat_dist, z_offset=(t_h * 100.0) + (spire_h * 50.0) - 50.0)
            spire_actor = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.StaticMeshActor, spire_pos, rot)
            if spire_actor:
                spire_actor.set_actor_label(f"City_Skyscraper_{i:02d}_Spire")
                sm_spire = spire_actor.get_component_by_class(unreal.StaticMeshComponent)
                if sm_spire:
                    sm_spire.set_editor_property("static_mesh", mesh_cylinder)
                    sm_spire.set_world_scale3d(unreal.Vector(8.0, 8.0, spire_h))
                    sm_spire.set_material(0, mat_pedestal)
                    
            spawned_count += 2
            
    print(f">>> [CITY] {spawned_count} elementos arquitectonicos generados y distribuidos a lo largo del circuito.")
    
    # 6. Guardar nivel
    unreal.EditorLevelLibrary.save_current_level()
    print(">>> [CITY] Nivel L_RaceTrack_VR guardado con exito!")

if __name__ == "__main__":
    run()
