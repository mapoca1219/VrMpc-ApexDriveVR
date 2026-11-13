#!/usr/bin/env python3
# ==============================================================================
# DEPLOY_GRAND_PRIX_VR.PY
# Configuración Definitiva de Carreras VR, Cabina OLED, Volante, Rivales y Policías
# ==============================================================================
import unreal

def log(msg):
    unreal.log_warning(f"[GRAND_PRIX_VR] >>> {msg} <<<")

def get_track_point(spline_comp, distance, lateral_offset=0.0, height_offset=0.0):
    spline_len = spline_comp.get_spline_length()
    wrapped_dist = distance % spline_len
    if wrapped_dist < 0.0:
        wrapped_dist += spline_len

    center_loc = spline_comp.get_location_at_distance_along_spline(wrapped_dist, unreal.SplineCoordinateSpace.WORLD)
    rot = spline_comp.get_rotation_at_distance_along_spline(wrapped_dist, unreal.SplineCoordinateSpace.WORLD)
    right_vec = spline_comp.get_right_vector_at_distance_along_spline(wrapped_dist, unreal.SplineCoordinateSpace.WORLD)
    
    final_loc = unreal.Vector(
        center_loc.x + (right_vec.x * lateral_offset),
        center_loc.y + (right_vec.y * lateral_offset),
        center_loc.z + height_offset
    )
    return final_loc, rot

def setup():
    log("Iniciando despliegue definitivo de la parrilla de carreras VR...")

    level_path = "/Game/Maps/L_RaceTrack_VR"
    unreal.EditorLevelLibrary.load_level(level_path)

    # 1. Cargar Assets Críticos y Materiales Automotrices AAA
    clear_glass = unreal.load_asset("/Game/Vehicles/Materials/M_TrueClearGlass")
    if not clear_glass:
        clear_glass = unreal.load_asset("/Game/Vehicles/Glass_-_Clear_001")
    red_glass = unreal.load_asset("/Game/Vehicles/Glass_-_Red")
    wheel_mesh = unreal.load_asset("/Game/Vehicles/Meshes/SM_Steering_Wheel_Centered")
    wheel_mat = unreal.load_asset("/Game/Vehicles/Materials/M_SteeringWheel_Alcantara")
    cube_mesh = unreal.load_asset("/Engine/BasicShapes/Cube")
    cylinder_mesh = unreal.load_asset("/Engine/BasicShapes/Cylinder")
    sphere_mesh = unreal.load_asset("/Engine/BasicShapes/Sphere")
    ioniq_mesh = unreal.load_asset("/Game/Vehicles/Meshes/SM_Hyundai_Ioniq5")
    merkurs_mesh = unreal.load_asset("/Game/Vehicles/Meshes/SM_Merkurs_Chassis")
    engine_sound = unreal.load_asset("/Game/Audio/SW_Engine_Loop")
    siren_sound = unreal.load_asset("/Game/Audio/SW_Police_Siren")
    torque_curve = unreal.load_asset("/Game/Blueprints/Curve_Torque")

    # Materiales automotrices
    paint_red = unreal.load_asset("/Game/Vehicles/Car_Paint_-_Red_002")
    paint_black = unreal.load_asset("/Game/Vehicles/Car_Paint_-_Black")
    paint_gray = unreal.load_asset("/Game/Vehicles/Car_Paint_-_gray")
    chrome_mat = unreal.load_asset("/Game/Vehicles/Metal_-_Chrome")
    rough_black_mat = unreal.load_asset("/Game/Vehicles/Metal_-_Black_-_Rough_0_2")
    tire_mat = unreal.load_asset("/Game/Vehicles/Tire")
    road_mat = unreal.load_asset("/Game/LevelPrototyping/Materials/MI_PrototypeGrid_TopDark")

    # 2. Configurar Materiales en SM_Merkurs_Chassis para eliminar checkerboard dev
    if merkurs_mesh:
        material_mapping = {
            0: chrome_mat,          # Licence_plate_metal
            1: clear_glass,         # Vehicles_Decals_Exterior (Transparente para no tapar el parabrisas)
            2: wheel_mat,           # alcantara
            4: rough_black_mat,     # Black_001
            7: wheel_mat,           # Stepped_Leather
            8: chrome_mat,          # Specmap_Steel
            11: wheel_mat,          # Leather02_W
            12: chrome_mat,         # Chrome
            13: red_glass,          # Brake_Light
            14: red_glass,          # Common_Light_Details_Red
            15: paint_red,          # Vehicle_Primary_Paint
            16: clear_glass,        # Glass (Parabrisas y ventanas 100% transparentes)
            17: paint_red,          # Vehicle_Primary_Paint
            18: clear_glass,        # Glass secundario
            19: clear_glass,        # Reverse_Light
            20: chrome_mat,         # Rim_BL
            21: rough_black_mat,    # Break_Cover
            23: tire_mat,           # Tire_Sport_Type
            24: chrome_mat,         # Rim_BL_Badge
            26: rough_black_mat,    # Black
            27: paint_black,        # Vehicle_Third_Paint
            30: rough_black_mat,    # Grate_05
            32: clear_glass,        # Headlight glass
            34: clear_glass,        # Headlight
            39: wheel_mat,          # Carpet_004_White
            40: rough_black_mat,    # Seatbelt_003
            41: paint_black,        # Vehicle_Secondary_Paint
            42: clear_glass,        # Exterior_Decals_White (Transparente)
            43: clear_glass,        # X453MA_Decal_01 (Transparente)
        }
        for slot_idx, mat in material_mapping.items():
            if mat:
                try:
                    merkurs_mesh.set_material(slot_idx, mat)
                except Exception as e:
                    pass
        log("Materiales automotrices GT3 asignados en SM_Merkurs_Chassis (Pintura roja metalizada, rines cromados, neumáticos y lunas limpias).")

    # 3. Configurar Blueprints de Peones
    player_bp = unreal.load_class(None, "/Game/Blueprints/BP_VrVehiclePawn.BP_VrVehiclePawn_C")
    police_bp = unreal.load_class(None, "/Game/Blueprints/BP_PoliceVehiclePawn.BP_PoliceVehiclePawn_C")

    if not player_bp or not police_bp:
        log("ERROR: No se pudieron cargar los Blueprints de vehículos.")
        return

    # CDO de BP_VrVehiclePawn
    player_cdo = unreal.get_default_object(player_bp)
    if player_cdo:
        try:
            movement = player_cdo.get_component_by_class(unreal.ChaosWheeledVehicleMovementComponent)
            if movement and torque_curve:
                engine_setup = movement.get_editor_property("engine_setup")
                engine_setup.torque_curve.external_curve = torque_curve
                movement.set_editor_property("engine_setup", engine_setup)
        except Exception as e:
            log(f"Aviso en CDO de Player: {e}")

    # CDO de BP_PoliceVehiclePawn
    police_cdo = unreal.get_default_object(police_bp)
    if police_cdo:
        try:
            movement = police_cdo.get_component_by_class(unreal.ChaosWheeledVehicleMovementComponent)
            if movement and torque_curve:
                engine_setup = movement.get_editor_property("engine_setup")
                engine_setup.torque_curve.external_curve = torque_curve
                movement.set_editor_property("engine_setup", engine_setup)
        except Exception as e:
            log(f"Aviso en CDO de Police: {e}")

    # 4. Localizar y reconfigurar la pista (ARaceTrackSpline)
    track_actor = None
    existing_actors_to_delete = []

    for a in unreal.EditorLevelLibrary.get_all_level_actors():
        cls_name = a.get_class().get_name()
        label = a.get_actor_label()
        if "RaceTrackSpline" in cls_name or "RaceTrack_Circuit" in label:
            track_actor = a
        elif any(k in cls_name or k in label for k in ["BP_VrVehiclePawn", "Player", "Police", "Rival", "PlayerStart"]):
            existing_actors_to_delete.append(a)

    if not track_actor:
        log("ERROR: No se encontró RaceTrack_Circuit en el mapa.")
        return

    log(f"Limpiando {len(existing_actors_to_delete)} actores residuales...")
    for act in existing_actors_to_delete:
        unreal.EditorLevelLibrary.destroy_actor(act)

    # Configurar dimensiones visuales y de protección: 14m de ancho y barreras bajas GT3 de 65cm con metal cromado
    track_actor.set_editor_property("TrackWidth", 1400.0)
    track_actor.set_editor_property("WallHeight", 65.0)
    track_actor.set_editor_property("WallThickness", 35.0)
    track_actor.set_editor_property("bGenerateGuardrails", True)
    if road_mat:
        track_actor.set_editor_property("RoadMaterial", road_mat)
    if chrome_mat:
        track_actor.set_editor_property("WallMaterial", chrome_mat)

    # Forzar regeneración de mallas procedimentales
    curr_loc = track_actor.get_actor_location()
    track_actor.set_actor_location(curr_loc, False, False)
    log("Pista ARaceTrackSpline configurada con asfalto oscuro y barreras GT3 panorámicas bajas.")

    spline_comp = track_actor.get_component_by_class(unreal.SplineComponent)
    if not spline_comp:
        log("ERROR: No se encontró SplineComponent en la pista.")
        return

    circuit_len = spline_comp.get_spline_length()
    log(f"Longitud total del circuito: {circuit_len/100.0:.1f} metros.")

    # 5. Iluminación Cinematográfica Golden-Hour & Post-Processing
    sun_actor = None
    sky_light = None
    fog_actor = None
    pp_actor = None

    for a in unreal.EditorLevelLibrary.get_all_level_actors():
        cls_name = a.get_class().get_name()
        label = a.get_actor_label()
        if "DirectionalLight" in cls_name or "Sun" in label:
            sun_actor = a
        elif "SkyLight" in cls_name or "Ambient" in label:
            sky_light = a
        elif "ExponentialHeightFog" in cls_name or "Fog" in label:
            fog_actor = a
        elif "PostProcessVolume" in cls_name or "PostProcess" in label:
            pp_actor = a

    # Configurar Sol Diurno Natural y Cielo Claro
    if sun_actor:
        try:
            sun_actor.set_actor_rotation(unreal.Rotator(pitch=-35.0, yaw=65.0, roll=0.0), False)
            for c in sun_actor.get_components_by_class(unreal.DirectionalLightComponent):
                c.set_editor_property("intensity", 10.0) # Luz diurna clara
                c.set_editor_property("light_color", unreal.Color(255, 248, 238, 255))
                c.set_editor_property("cast_shadows", True)
                try:
                    c.set_editor_property("atmosphere_sun_light", True)
                except:
                    pass
            log("Luz solar ajustada a iluminación diurna clara (10.0 Lux).")
        except Exception as e:
            log(f"Aviso configurando sol: {e}")

    # Configurar SkyLight
    if sky_light:
        for c in sky_light.get_components_by_class(unreal.SkyLightComponent):
            try:
                c.set_editor_property("intensity", 1.8)
                c.set_editor_property("real_time_capture", True)
            except:
                pass

    # Configurar Niebla Atmosférica Nítida
    if fog_actor:
        for c in fog_actor.get_components_by_class(unreal.ExponentialHeightFogComponent):
            try:
                c.set_editor_property("fog_density", 0.0003)
                c.set_editor_property("volumetric_fog", False)
            except Exception as e:
                pass
        log("Niebla atmosférica nítida configurada (visibilidad panorámica 100%).")

    # Configurar PostProcessVolume (Exposición equilibrada y nítida)
    if not pp_actor:
        try:
            pp_actor = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.PostProcessVolume, unreal.Vector(0,0,0))
            pp_actor.set_actor_label("PostProcess_GoldenHour")
        except:
            pass
    
    if pp_actor:
        try:
            pp_actor.set_editor_property("unbound", True)
            settings = pp_actor.get_editor_property("settings")
            settings.auto_exposure_method = unreal.AutoExposureMethod.AEM_HISTOGRAM
            settings.auto_exposure_min_brightness = 0.8
            settings.auto_exposure_max_brightness = 2.5
            settings.bloom_intensity = 0.3
            settings.motion_blur_amount = 0.0
            settings.vignette_intensity = 0.1
            pp_actor.set_editor_property("settings", settings)
            log("PostProcessVolume configurado con exposición equilibrada y nitidez total.")
        except Exception as e:
            log(f"Aviso configurando postprocess: {e}")

    # =========================================================================
    # 6. GENERAR PARRILLA DE SALIDA: RIVALES IA (Delante del jugador)
    # =========================================================================
    rival_configs = [
        {"label": "Rival_Racer_1", "dist": 4000.0, "offset": 180.0,  "speed": 175.0, "mat": paint_black},
        {"label": "Rival_Racer_2", "dist": 2800.0, "offset": -180.0, "speed": 165.0, "mat": paint_gray},
        {"label": "Rival_Racer_3", "dist": 1600.0, "offset": 120.0,  "speed": 155.0, "mat": paint_red},
    ]

    for cfg in rival_configs:
        loc, rot = get_track_point(spline_comp, cfg["dist"], cfg["offset"], 38.0)
        rival = unreal.EditorLevelLibrary.spawn_actor_from_class(player_bp, loc, rot)
        rival.set_actor_label(cfg["label"])
        rival.set_editor_property("is_ai_racer", True)
        rival.set_editor_property("ai_target_speed_kmh", cfg["speed"])
        rival.set_editor_property("auto_possess_player", unreal.AutoReceiveInput.DISABLED)
        try:
            rival.set_editor_property("auto_possess_ai", unreal.AutoPossessAI.PLACED_IN_WORLD_OR_SPAWNED)
        except:
            pass

        # Configurar sonido de motor
        for c in rival.get_components_by_class(unreal.AudioComponent):
            if "Engine" in c.get_name():
                c.set_editor_property("sound", engine_sound)
                c.set_editor_property("auto_activate", True)

        # Asignar chasis orientado hacia adelante (Yaw=180) y pintura personalizada
        for c in rival.get_components_by_class(unreal.StaticMeshComponent):
            if "ChassisMeshComponent" in c.get_name():
                c.set_relative_location(unreal.Vector(0.0, 0.0, 0.0), False, False)
                c.set_relative_rotation(unreal.Rotator(pitch=0.0, yaw=180.0, roll=0.0), False, False)
                if cfg["mat"]:
                    c.set_material(17, cfg["mat"])
                if clear_glass:
                    for s in [1, 16, 18, 19, 32, 42, 43]:
                        try:
                            c.set_material(s, clear_glass)
                        except:
                            pass

        log(f"Rival IA desplegado: {cfg['label']} en dist={cfg['dist']/100.0:.1f}m (Velocidad={cfg['speed']} km/h)")

    # =========================================================================
    # 7. GENERAR VEHÍCULO DEL JUGADOR (BP_VrVehiclePawn - Player 0)
    # =========================================================================
    player_dist = 600.0 # 6 metros de la salida
    player_loc, player_rot = get_track_point(spline_comp, player_dist, -120.0, 38.0)
    player = unreal.EditorLevelLibrary.spawn_actor_from_class(player_bp, player_loc, player_rot)
    player.set_actor_label("Player_VrVehicle")
    player.set_editor_property("auto_possess_player", unreal.AutoReceiveInput.PLAYER0)
    player.set_editor_property("auto_possess_ai", unreal.AutoPossessAI.DISABLED)
    player.set_editor_property("is_ai_racer", False)

    # Configuración de alta fidelidad de la cabina de conducción ergonómica
    import math
    pitch_dash = -15.0
    rad_dash = math.radians(15.0)

    def calc_dash_text_coords(dy, dz):
        base_x = 44.5
        base_z = -14.0
        d_fwd = 1.2
        x = base_x + (dz * math.sin(rad_dash)) - (d_fwd * math.cos(rad_dash))
        y = dy
        z = base_z + (dz * math.cos(rad_dash)) + (d_fwd * math.sin(rad_dash))
        return unreal.Vector(x, y, z)

    for c in player.get_components_by_class(unreal.SceneComponent):
        c_name = c.get_name()
        # Ojos del piloto situados en X=18.0, Y=-38.0 (lado piloto), Z=106.0 (altura óptima de ojos)
        if "CockpitRoot" in c_name:
            c.set_relative_location(unreal.Vector(18.0, -38.0, 106.0), False, False)
            c.set_relative_rotation(unreal.Rotator(pitch=-3.0, yaw=0.0, roll=0.0), False, False)
        # Volante deportivo posicionado en el tercio inferior del campo de visión (X=36, Y=0, Z=-18)
        elif "SteeringWheelComponent" in c_name and not isinstance(c, unreal.StaticMeshComponent):
            c.set_relative_location(unreal.Vector(36.0, 0.0, -18.0), False, False)
            c.set_relative_rotation(unreal.Rotator(pitch=-18.0, yaw=0.0, roll=0.0), False, False)
        elif "SteeringWheelVisualMesh" in c_name and isinstance(c, unreal.StaticMeshComponent):
            c.set_relative_location(unreal.Vector(0.0, 0.0, 0.0), False, False)
            c.set_relative_rotation(unreal.Rotator(pitch=0.0, yaw=0.0, roll=0.0), False, False)
            c.set_relative_scale3d(unreal.Vector(85.0, 185.0, 85.0))
            if wheel_mesh:
                c.set_editor_property("static_mesh", wheel_mesh)
            if wheel_mat:
                c.set_material(0, wheel_mat)
        # Tablero Digital OLED Widescreen 36x12cm integrado en el salpicadero (X=46, Y=0, Z=-14)
        elif "DashboardBackplateMesh" in c_name and isinstance(c, unreal.StaticMeshComponent):
            c.set_relative_location(unreal.Vector(46.0, 0.0, -14.0), False, False)
            c.set_relative_rotation(unreal.Rotator(pitch=pitch_dash, yaw=0.0, roll=0.0), False, False)
            c.set_relative_scale3d(unreal.Vector(0.015, 0.36, 0.12))
            if cube_mesh:
                c.set_editor_property("static_mesh", cube_mesh)
            if wheel_mat:
                c.set_material(0, wheel_mat)
        elif "SteeringColumnMesh" in c_name and isinstance(c, unreal.StaticMeshComponent):
            c.set_relative_location(unreal.Vector(44.0, 0.0, -18.0), False, False)
            c.set_relative_rotation(unreal.Rotator(pitch=-18.0, yaw=0.0, roll=0.0), False, False)
            c.set_relative_scale3d(unreal.Vector(0.05, 0.05, 0.12))
            if cylinder_mesh:
                c.set_editor_property("static_mesh", cylinder_mesh)
            if wheel_mat:
                c.set_material(0, wheel_mat)
        elif "GearShiftLeverMesh" in c_name and isinstance(c, unreal.StaticMeshComponent):
            c.set_relative_location(unreal.Vector(25.0, 24.0, -25.0), False, False)
            c.set_relative_rotation(unreal.Rotator(pitch=-12.0, yaw=0.0, roll=0.0), False, False)
            c.set_relative_scale3d(unreal.Vector(0.025, 0.025, 0.14))
            if cylinder_mesh:
                c.set_editor_property("static_mesh", cylinder_mesh)
            if wheel_mat:
                c.set_material(0, wheel_mat)
        elif "GearShiftKnobMesh" in c_name and isinstance(c, unreal.StaticMeshComponent):
            c.set_relative_scale3d(unreal.Vector(2.4, 2.4, 0.45))
            if sphere_mesh:
                c.set_editor_property("static_mesh", sphere_mesh)
            if chrome_mat:
                c.set_material(0, chrome_mat)
        elif "ChassisMeshComponent" in c_name and isinstance(c, unreal.StaticMeshComponent):
            c.set_relative_location(unreal.Vector(0.0, 0.0, 0.0), False, False)
            c.set_relative_rotation(unreal.Rotator(pitch=0.0, yaw=180.0, roll=0.0), False, False)
            if paint_red:
                c.set_material(17, paint_red)
            if clear_glass:
                for s in [1, 16, 18, 19, 32, 42, 43]:
                    try:
                        c.set_material(s, clear_glass)
                    except:
                        pass

    # Indicadores Digitales OLED montados sobre el Tablero con Anti-Recorte Milimétrico
    rot_text = unreal.Rotator(pitch=pitch_dash, yaw=180.0, roll=0.0)
    for c in player.get_components_by_class(unreal.TextRenderComponent):
        c_name = c.get_name()
        c.set_relative_rotation(rot_text, False, False)
        if "SpeedTextRender" in c_name:
            c.set_relative_location(calc_dash_text_coords(0.0, 0.0), False, False)
            c.set_text(unreal.Text("0 KM/H"))
            c.set_world_size(3.6)
            c.set_text_render_color(unreal.Color(0, 245, 255, 255)) # OLED Cyan
        elif "PositionTextRender" in c_name:
            c.set_relative_location(calc_dash_text_coords(-11.0, 3.2), False, False)
            c.set_text(unreal.Text("POS: P4/7"))
            c.set_world_size(2.2)
            c.set_text_render_color(unreal.Color(255, 215, 0, 255)) # Oro campeón
        elif "GearTextRender" in c_name:
            c.set_relative_location(calc_dash_text_coords(0.0, 3.2), False, False)
            c.set_text(unreal.Text("GEAR: 1"))
            c.set_world_size(2.4)
            c.set_text_render_color(unreal.Color(255, 140, 0, 255)) # Ámbar deportivo
        elif "PoliceAlertTextRender" in c_name:
            c.set_relative_location(calc_dash_text_coords(0.0, -3.8), False, False)
            c.set_text(unreal.Text("PATRULLA: DESPEJADO"))
            c.set_world_size(1.8)
            c.set_text_render_color(unreal.Color(0, 255, 128, 255)) # Verde esmeralda

    for c in player.get_components_by_class(unreal.AudioComponent):
        if "Engine" in c.get_name():
            c.set_editor_property("sound", engine_sound)
            c.set_editor_property("auto_activate", True)

    log(f"Vehículo del JUGADOR posicionado en {player_loc} con cabina ergonómica GT3 despejada.")

    # =========================================================================
    # 8. GENERAR ESCUADRÓN DE PATRULLAS POLICIALES (Detrás del Jugador)
    # =========================================================================
    police_configs = [
        {"label": "Police_Pursuit_Interceptor_1", "dist": -2500.0, "offset": 0.0,    "rate": 6.0},
        {"label": "Police_Pursuit_Interceptor_2", "dist": -4500.0, "offset": -240.0, "rate": 5.5},
        {"label": "Police_Pursuit_Interceptor_3", "dist": -6500.0, "offset": 240.0,  "rate": 6.8},
    ]

    for cfg in police_configs:
        loc, rot = get_track_point(spline_comp, cfg["dist"], cfg["offset"], 38.0)
        police = unreal.EditorLevelLibrary.spawn_actor_from_class(police_bp, loc, rot)
        police.set_actor_label(cfg["label"])
        police.set_editor_property("auto_possess_player", unreal.AutoReceiveInput.DISABLED)
        try:
            police.set_editor_property("auto_possess_ai", unreal.AutoPossessAI.PLACED_IN_WORLD_OR_SPAWNED)
            police.set_editor_property("siren_strobe_rate", cfg["rate"])
            police.set_editor_property("b_is_siren_active", True)
        except:
            pass

        # Escalar chasis de policía a dimensiones reales y ruedas en el asfalto (Z=0)
        for c in police.get_components_by_class(unreal.StaticMeshComponent):
            c_name = c.get_name()
            if "ChassisMeshComponent" in c_name:
                c.set_relative_scale3d(unreal.Vector(0.0125, 0.0125, 0.0125))
                c.set_relative_location(unreal.Vector(0.0, 0.0, 0.0), False, False)
                c.set_relative_rotation(unreal.Rotator(pitch=0.0, yaw=90.0, roll=0.0), False, False)
                if ioniq_mesh:
                    c.set_editor_property("static_mesh", ioniq_mesh)
            elif "RedSirenMesh" in c_name:
                c.set_relative_location(unreal.Vector(0.0, -25.0, 152.0), False, False)
            elif "BlueSirenMesh" in c_name:
                c.set_relative_location(unreal.Vector(0.0, 25.0, 152.0), False, False)

        for c in police.get_components_by_class(unreal.PointLightComponent):
            c_name = c.get_name()
            c.set_editor_property("intensity", 4500.0)
            c.set_editor_property("attenuation_radius", 900.0)
            c.set_editor_property("use_inverse_squared_falloff", True)
            if "RedSirenLight" in c_name:
                c.set_relative_location(unreal.Vector(0.0, -25.0, 155.0), False, False)
            elif "BlueSirenLight" in c_name:
                c.set_relative_location(unreal.Vector(0.0, 25.0, 155.0), False, False)

        # Configurar audios de patrulla (Sirena activa + Motor)
        for c in police.get_components_by_class(unreal.AudioComponent):
            c_name = c.get_name()
            if "Siren" in c_name:
                c.set_editor_property("sound", siren_sound)
                c.set_editor_property("auto_activate", True)
            elif "Engine" in c_name:
                c.set_editor_property("sound", engine_sound)
                c.set_editor_property("auto_activate", True)

        # Asignar objetivo de persecución (Jugador)
        try:
            police.set_target_player(player)
        except Exception as e:
            log(f"Aviso vinculando target player en {cfg['label']}: {e}")

        log(f"Patrulla desplegada: {cfg['label']} en dist={cfg['dist']/100.0:.1f}m (Sirena={cfg['rate']} Hz)")

    # 9. Desactivar GameMode residual
    world = unreal.EditorLevelLibrary.get_editor_world()
    world.get_world_settings().set_editor_property("default_game_mode", None)

    # 10. Guardar nivel y assets
    unreal.EditorLevelLibrary.save_current_level()
    log("=== ¡GRAN PREMIO VR CONFIGURADO, ESCALADO Y GUARDADO EXITOSAMENTE! ===")

if __name__ == "__main__":
    setup()
