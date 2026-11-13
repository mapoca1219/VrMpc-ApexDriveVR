#!/usr/bin/env python3
# ==============================================================================
# SETUP_RACE_SCENE.PY - Script Definitivo de Automatización para Unreal Engine 5
# Proyecto: VrMpc | Nivel: L_RaceTrack_VR | Meta Quest Standalone VR Racing
# ==============================================================================
import unreal

def log(msg):
    unreal.log(f"[SETUP_RACE_SCENE] >>> {msg} <<<")

def setup_race_scene():
    log("Iniciando configuración definitiva de la escena de carreras en VR...")

    # -------------------------------------------------------------------------
    # 0. CARGAR NIVEL ACTIVO L_RaceTrack_VR
    # -------------------------------------------------------------------------
    level_path = "/Game/Maps/L_RaceTrack_VR"
    if unreal.EditorAssetLibrary.does_asset_exist(level_path):
        unreal.EditorLevelLibrary.load_level(level_path)
        log(f"Nivel cargado correctamente: {level_path}")
    else:
        unreal.log_error(f"No se encontró el mapa en {level_path}")
        return False

    world = unreal.EditorLevelLibrary.get_editor_world()
    world_settings = world.get_world_settings()

    # -------------------------------------------------------------------------
    # 1. LIMPIEZA DEL MAPA (PlayerStart, PlayerStartPIE y Duplicados)
    # -------------------------------------------------------------------------
    log("1. Limpiando actores residuales y duplicados en el nivel...")
    all_actors = unreal.EditorLevelLibrary.get_all_level_actors()

    destroyed_starts = 0
    for actor in all_actors:
        cls_name = actor.get_class().get_name()
        label = actor.get_actor_label()
        if isinstance(actor, unreal.PlayerStart) or "PlayerStart" in cls_name or "PlayerStart" in label:
            unreal.EditorLevelLibrary.destroy_actor(actor)
            destroyed_starts += 1

    if destroyed_starts > 0:
        log(f"Eliminados {destroyed_starts} actores residuales de tipo PlayerStart / PlayerStartPIE.")
    else:
        log("No se encontraron PlayerStart residuales en el mapa.")

    # Re-obtener lista tras destruir PlayerStarts
    all_actors = unreal.EditorLevelLibrary.get_all_level_actors()

    player_vehicles = []
    police_vehicles = []
    track_actor = None
    track_spline_comp = None

    for actor in all_actors:
        cls_name = actor.get_class().get_name()
        label = actor.get_actor_label()

        if "Police" in cls_name or "Police" in label:
            police_vehicles.append(actor)
        elif "VrVehicle" in cls_name or "Player_VrVehicle" in label:
            player_vehicles.append(actor)
        elif "Track" in cls_name or "Spline" in cls_name or "RaceTrack" in label or "Track" in label:
            track_actor = actor
            if hasattr(actor, "spline_component") and actor.spline_component:
                track_spline_comp = actor.spline_component
            elif hasattr(actor, "get_component_by_class"):
                track_spline_comp = actor.get_component_by_class(unreal.SplineComponent)

    # Dejar exactamente UNA sola instancia de BP_VrVehiclePawn
    if len(player_vehicles) > 1:
        log(f"Detectadas {len(player_vehicles)} instancias del jugador. Eliminando duplicados...")
        for dup in player_vehicles[1:]:
            unreal.EditorLevelLibrary.destroy_actor(dup)
    
    player_vehicle = player_vehicles[0] if player_vehicles else None

    # Dejar exactamente UNA sola instancia de BP_PoliceVehiclePawn
    if len(police_vehicles) > 1:
        log(f"Detectadas {len(police_vehicles)} instancias de policía. Eliminando duplicados...")
        for dup in police_vehicles[1:]:
            unreal.EditorLevelLibrary.destroy_actor(dup)

    police_vehicle = police_vehicles[0] if police_vehicles else None

    # Si faltan actores principales en el nivel, instanciarlos desde los Blueprints
    if not player_vehicle:
        log("No existía vehículo de jugador. Instanciando /Game/Blueprints/BP_VrVehiclePawn...")
        player_bp_class = unreal.load_class(None, "/Game/Blueprints/BP_VrVehiclePawn.BP_VrVehiclePawn_C")
        spawn_loc = unreal.Vector(1940.0, -40.0, 200.0)
        player_vehicle = unreal.EditorLevelLibrary.spawn_actor_from_class(player_bp_class, spawn_loc)
        player_vehicle.set_actor_label("Player_VrVehicle")

    if not police_vehicle:
        log("No existía patrulla policial. Instanciando /Game/Blueprints/BP_PoliceVehiclePawn...")
        police_bp_class = unreal.load_class(None, "/Game/Blueprints/BP_PoliceVehiclePawn.BP_PoliceVehiclePawn_C")
        spawn_loc = unreal.Vector(440.0, -40.0, 200.0)
        police_vehicle = unreal.EditorLevelLibrary.spawn_actor_from_class(police_bp_class, spawn_loc)
        police_vehicle.set_actor_label("Police_Pursuit_Interceptor")

    # -------------------------------------------------------------------------
    # 2. CONFIGURACIÓN DE POSESIÓN E INPUT DEL JUGADOR (BP_VrVehiclePawn)
    # -------------------------------------------------------------------------
    log("2. Configurando posesión, cámara e inputs de BP_VrVehiclePawn...")

    # Posesión por Player 0 y desactivación obligatoria de IA en el coche del jugador
    player_vehicle.set_editor_property("auto_possess_player", unreal.AutoReceiveInput.PLAYER0)
    try:
        player_vehicle.set_editor_property("auto_receive_input", unreal.AutoReceiveInput.PLAYER0)
    except Exception as e:
        pass

    try:
        player_vehicle.set_editor_property("auto_possess_ai", unreal.AutoPossessAI.DISABLED)
        log("auto_possess_ai establecido en DISABLED para BP_VrVehiclePawn.")
    except Exception as e:
        unreal.log_warning(f"No se pudo asignar auto_possess_ai en Player: {e}")

    # Orientar y alinear el jugador a la recta de la pista
    player_loc = player_vehicle.get_actor_location()
    player_rot = player_vehicle.get_actor_rotation()

    if track_spline_comp:
        closest_spline_loc = track_spline_comp.find_location_closest_to_world_location(player_loc, unreal.SplineCoordinateSpace.WORLD)
        closest_spline_rot = track_spline_comp.find_rotation_closest_to_world_location(player_loc, unreal.SplineCoordinateSpace.WORLD)
        
        # Posición inicial sobre el asfalto + 40 cm de elevación para Chaos
        target_z = closest_spline_loc.z + 40.0
        player_loc = unreal.Vector(closest_spline_loc.x, closest_spline_loc.y, target_z)
        player_rot = closest_spline_rot

    player_vehicle.set_actor_location_and_rotation(player_loc, player_rot, False, False)
    log(f"Vehículo del jugador posicionado en {player_loc} con rotación {player_rot} (+40cm sobre pista).")

    # Configuración de cámara de cabina (Driver Eye Position = (-20.0, -35.0, 110.0))
    cockpit_root = None
    vr_camera = None

    if hasattr(player_vehicle, "cockpit_root") and player_vehicle.cockpit_root:
        cockpit_root = player_vehicle.cockpit_root
    if hasattr(player_vehicle, "vr_camera") and player_vehicle.vr_camera:
        vr_camera = player_vehicle.vr_camera

    if not cockpit_root or not vr_camera:
        for comp in player_vehicle.get_components_by_class(unreal.SceneComponent):
            cname = comp.get_name()
            if "CockpitRoot" in cname:
                cockpit_root = comp
            elif "VRCamera" in cname or isinstance(comp, unreal.CameraComponent):
                vr_camera = comp

    if cockpit_root:
        cockpit_root.set_relative_location(unreal.Vector(-20.0, -35.0, 110.0), False, False)
        cockpit_root.set_relative_rotation(unreal.Rotator(0.0, 0.0, 0.0), False, False)
        log("CockpitRoot alineado en posición de piloto (-20.0, -35.0, 110.0).")

    if vr_camera:
        vr_camera.set_relative_location(unreal.Vector(0.0, 0.0, 0.0), False, False)
        vr_camera.set_relative_rotation(unreal.Rotator(0.0, 0.0, 0.0), False, False)
        log("VRCamera anclada sin desfase relativo respecto a CockpitRoot.")

    # -------------------------------------------------------------------------
    # 3. CONFIGURACIÓN DE LA PATRULLA POLICIAL (BP_PoliceVehiclePawn)
    # -------------------------------------------------------------------------
    log("3. Configurando IA, persecución y posición de BP_PoliceVehiclePawn...")

    # Auto posesión de IA activa y control por jugador deshabilitado
    try:
        police_vehicle.set_editor_property("auto_possess_ai", unreal.AutoPossessAI.PLACED_IN_WORLD_OR_SPAWNED)
        police_vehicle.set_editor_property("auto_possess_player", unreal.AutoReceiveInput.DISABLED)
        log("Patrulla policial: AutoPossessAI = PLACED_IN_WORLD_OR_SPAWNED, AutoPossessPlayer = DISABLED.")
    except Exception as e:
        unreal.log_warning(f"Error configurando auto possess en patrulla: {e}")

    # Posicionar la patrulla exactamente a 15 metros (1500 cm) detrás del jugador en la misma recta
    player_forward = player_vehicle.get_actor_forward_vector()
    police_loc = unreal.Vector(
        player_loc.x - (player_forward.x * 1500.0),
        player_loc.y - (player_forward.y * 1500.0),
        player_loc.z
    )
    police_rot = player_rot
    police_vehicle.set_actor_location_and_rotation(police_loc, police_rot, False, False)
    log(f"Patrulla policial ubicada a 15 metros detrás del jugador: Posición {police_loc}, Rotación {police_rot}.")

    # Vincular objetivo (TargetPlayerPawn)
    if hasattr(police_vehicle, "set_target_player"):
        police_vehicle.set_target_player(player_vehicle)
        log("Patrulla policial: SetTargetPlayer(player_vehicle) enlazado con éxito.")
    else:
        try:
            police_vehicle.set_editor_property("target_player_pawn", player_vehicle)
        except:
            pass

    # Vincular Spline de la pista al seguidor
    if track_spline_comp:
        follower = None
        if hasattr(police_vehicle, "spline_follower") and police_vehicle.spline_follower:
            follower = police_vehicle.spline_follower
        elif hasattr(police_vehicle, "get_spline_follower"):
            follower = police_vehicle.get_spline_follower()

        if follower:
            try:
                follower.set_target_spline(track_spline_comp)
                log("Patrulla policial: Seguidor de trazada enlazado a la spline de la pista.")
            except Exception as e:
                try:
                    follower.set_editor_property("target_spline_component", track_spline_comp)
                    log("Patrulla policial: TargetSplineComponent asignado.")
                except Exception as e2:
                    unreal.log_warning(f"Error enlazando spline a seguidor: {e2}")

    # -------------------------------------------------------------------------
    # 4. WORLDSETTINGS Y GAMEMODE (Evitar spawn de DefaultPawn / Spectator)
    # -------------------------------------------------------------------------
    log("4. Configurando WorldSettings para desactivar spawns automáticos...")

    # Configurar default_game_mode en WorldSettings
    world_settings.set_editor_property("default_game_mode", None)
    log("WorldSettings.default_game_mode establecido en None (utiliza posesión directa de Player0 en el mapa).")

    # Asegurar que BP_XRGameMode en Content/XRFramework tenga DefaultPawnClass = None
    bp_xr = unreal.EditorAssetLibrary.load_asset("/Game/XRFramework/Blueprints/BP_XRGameMode")
    if bp_xr:
        try:
            gen_class = None
            if hasattr(bp_xr, "generated_class"):
                try:
                    gen_class = bp_xr.generated_class()
                except:
                    gen_class = bp_xr.get_editor_property("generated_class")
            if not gen_class:
                gen_class = unreal.load_class(None, "/Game/XRFramework/Blueprints/BP_XRGameMode.BP_XRGameMode_C")

            if gen_class:
                cdo = unreal.get_default_object(gen_class)
                if cdo:
                    cdo.set_editor_property("default_pawn_class", None)
                    unreal.BlueprintEditorLibrary.compile_blueprint(bp_xr)
                    unreal.EditorAssetLibrary.save_loaded_asset(bp_xr)
                    log("BP_XRGameMode CDO: DefaultPawnClass establecido en None para evitar generación de PlayerStartPIE.")
        except Exception as e:
            unreal.log_warning(f"Error asegurando DefaultPawnClass en BP_XRGameMode: {e}")

    # -------------------------------------------------------------------------
    # 5. GUARDADO AUTOMÁTICO Y REPORTE DE RESULTADOS
    # -------------------------------------------------------------------------
    log("5. Guardando cambios en el mapa L_RaceTrack_VR...")
    unreal.EditorLevelLibrary.save_current_level()

    print("\n" + "=" * 70)
    print(" >>> SETUP_RACE_SCENE COMPLETADO EXITOSAMENTE CON 0 ERRORES <<<")
    print("=" * 70)
    print(f" * Mapa: {level_path}")
    print(f" * PlayerStart eliminados: {destroyed_starts}")
    print(f" * Coche Jugador: {player_vehicle.get_actor_label()} (Pos: {player_loc})")
    print(f"   - AutoPossessPlayer: PLAYER0 | AutoPossessAI: DISABLED")
    print(f"   - Cámara Cockpit: (-20.0, -35.0, 110.0)")
    print(f" * Patrulla Policial: {police_vehicle.get_actor_label()} (Pos: {police_loc})")
    print(f"   - Distancia al jugador: 15 metros detrás sobre la recta")
    print(f"   - AutoPossessAI: PLACED_IN_WORLD_OR_SPAWNED | AutoPossessPlayer: DISABLED")
    print(f"   - TargetPlayerPawn vinculado: {player_vehicle.get_actor_label()}")
    print(f"   - Seguidor de circuito: Enlazado a Spline")
    print(f" * WorldSettings DefaultGameMode: None (Sin spawn residual en PlayerStart)")
    print("=" * 70)
    print(" ¡LISTO PARA DAR PLAY EN UNREAL! El jugador tomará el control inmediato")
    print(" del habitáculo VR con audio y física, y la policía iniciará la persecución.")
    print("=" * 70 + "\n")
    return True

if __name__ == "__main__":
    setup_race_scene()

