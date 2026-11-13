#!/usr/bin/env python3
# ==============================================================================
# SETUP_GRAND_PRIX.PY - Configuración Definitiva del Gran Premio VR en Unreal Engine 5
# Circuito: L_RaceTrack_VR | Múltiples Rivales IA + Escuadrón Policial + Confinamiento Total
# ==============================================================================
import unreal

def log(msg):
    unreal.log_warning(f"[GRAND_PRIX] >>> {msg} <<<")

def get_track_point(spline_comp, distance, lateral_offset=0.0, height_offset=38.0):
    """Calcula la posición y rotación exacta en la pista aplicando desplazamiento lateral y altura."""
    spline_len = spline_comp.get_spline_length()
    wrapped_dist = distance % spline_len
    if wrapped_dist < 0.0:
        wrapped_dist += spline_len

    center_loc = spline_comp.get_location_at_distance_along_spline(wrapped_dist, unreal.SplineCoordinateSpace.WORLD)
    rot = spline_comp.get_rotation_at_distance_along_spline(wrapped_dist, unreal.SplineCoordinateSpace.WORLD)
    
    # Obtener el vector derecho para el desplazamiento lateral
    right_vec = spline_comp.get_right_vector_at_distance_along_spline(wrapped_dist, unreal.SplineCoordinateSpace.WORLD)
    
    final_loc = unreal.Vector(
        center_loc.x + (right_vec.x * lateral_offset),
        center_loc.y + (right_vec.y * lateral_offset),
        center_loc.z + height_offset
    )
    return final_loc, rot

def setup_grand_prix():
    log("Iniciando despliegue del Gran Premio VR: Pista Reforzada, Rivales y Escuadrón Policial...")

    level_path = "/Game/Maps/L_RaceTrack_VR"
    unreal.EditorLevelLibrary.load_level(level_path)

    # 1. Localizar y reconfigurar la pista (ARaceTrackSpline)
    track_actor = None
    existing_vehicles = []

    for a in unreal.EditorLevelLibrary.get_all_level_actors():
        cls_name = a.get_class().get_name()
        label = a.get_actor_label()
        if "RaceTrackSpline" in cls_name or "RaceTrack_Circuit" in label:
            track_actor = a
        elif any(k in cls_name or k in label for k in ["BP_VrVehiclePawn", "Player", "Police", "Rival"]):
            existing_vehicles.append(a)

    if not track_actor:
        log("ERROR: No se encontró RaceTrack_Circuit en el mapa.")
        return

    # Limpiar vehículos previos para recrear la parrilla completa y ordenada
    log(f"Limpiando {len(existing_vehicles)} vehículos residuales previos...")
    for v in existing_vehicles:
        unreal.EditorLevelLibrary.destroy_actor(v)

    # Configurar dimensiones reforzadas de la pista: 14m ancho, muros de 3.5m altura y 1.2m espesor
    track_actor.set_editor_property("TrackWidth", 1400.0)
    track_actor.set_editor_property("WallHeight", 350.0)
    track_actor.set_editor_property("WallThickness", 120.0)
    track_actor.set_editor_property("bGenerateGuardrails", True)

    # Forzar reconstrucción de los SplineMesh components
    curr_loc = track_actor.get_actor_location()
    track_actor.set_actor_location(curr_loc, False, False)
    log("Pista ARaceTrackSpline actualizada: Ancho=14m, Muros=3.5m altura, Espesor=1.2m.")

    spline_comp = track_actor.get_component_by_class(unreal.SplineComponent)
    if not spline_comp:
        log("ERROR: No se encontró SplineComponent en la pista.")
        return

    circuit_len = spline_comp.get_spline_length()
    log(f"Longitud total del circuito: {circuit_len/100.0:.1f} metros.")

    # 2. Cargar Blueprints de vehículos
    player_bp = unreal.load_class(None, "/Game/Blueprints/BP_VrVehiclePawn.BP_VrVehiclePawn_C")
    police_bp = unreal.load_class(None, "/Game/Blueprints/BP_PoliceVehiclePawn.BP_PoliceVehiclePawn_C")

    if not player_bp or not police_bp:
        log("ERROR: No se pudieron cargar los Blueprints de vehículos.")
        return

    # =========================================================================
    # 3. GENERAR PARRILLA DE SALIDA: RIVALES IA
    # =========================================================================
    rival_configs = [
        {"label": "Rival_Racer_1", "dist": 7200.0, "offset": 230.0,  "speed": 175.0},
        {"label": "Rival_Racer_2", "dist": 5400.0, "offset": -230.0, "speed": 165.0},
        {"label": "Rival_Racer_3", "dist": 3700.0, "offset": 200.0,  "speed": 155.0},
    ]

    for cfg in rival_configs:
        loc, rot = get_track_point(spline_comp, cfg["dist"], cfg["offset"], 38.0)
        rival = unreal.EditorLevelLibrary.spawn_actor_from_class(player_bp, loc, rot)
        rival.set_actor_label(cfg["label"])
        
        # Configurar como IA Rival
        rival.set_editor_property("is_ai_racer", True)
        rival.set_editor_property("ai_target_speed_kmh", cfg["speed"])
        log(f"Rival IA activado: is_ai_racer=True, ai_target_speed_kmh={cfg['speed']} km/h")

        rival.set_editor_property("auto_possess_player", unreal.AutoReceiveInput.DISABLED)
        try:
            rival.set_editor_property("auto_possess_ai", unreal.AutoPossessAI.PLACED_IN_WORLD_OR_SPAWNED)
        except:
            pass

        log(f"Rival desplegado: {cfg['label']} en dist={cfg['dist']/100.0:.1f}m (Velocidad objetivo={cfg['speed']} km/h)")

    # =========================================================================
    # 4. GENERAR VEHÍCULO DEL JUGADOR (BP_VrVehiclePawn - Player 0)
    # =========================================================================
    player_dist = 2000.0 # 20 metros de la salida
    player_loc, player_rot = get_track_point(spline_comp, player_dist, -180.0, 38.0)
    player = unreal.EditorLevelLibrary.spawn_actor_from_class(player_bp, player_loc, player_rot)
    player.set_actor_label("Player_VrVehicle")
    player.set_editor_property("auto_possess_player", unreal.AutoReceiveInput.PLAYER0)
    player.set_editor_property("auto_possess_ai", unreal.AutoPossessAI.DISABLED)
    player.set_editor_property("is_ai_racer", False)

    # Alinear cabina de piloto
    try:
        cockpit = player.get_component_by_class(unreal.SceneComponent)
        for c in player.get_components_by_class(unreal.SceneComponent):
            if "CockpitRoot" in c.get_name():
                c.set_relative_location(unreal.Vector(-20.0, -35.0, 110.0), False, False)
                break
    except Exception as e:
        log(f"Aviso alineando cockpit: {e}")

    log(f"Vehículo del JUGADOR posicionado en {player_loc} con AutoPossess = PLAYER0.")

    # =========================================================================
    # 5. GENERAR ESCUADRÓN DE PATRULLAS POLICIALES (Múltiples Policías en Persecución)
    # =========================================================================
    police_configs = [
        {"label": "Police_Pursuit_Interceptor_1", "dist": 600.0,   "offset": 0.0,    "rate": 6.0},
        {"label": "Police_Pursuit_Interceptor_2", "dist": -1000.0, "offset": -280.0, "rate": 5.5},
        {"label": "Police_Pursuit_Interceptor_3", "dist": -2400.0, "offset": 280.0,  "rate": 6.8},
    ]

    for cfg in police_configs:
        loc, rot = get_track_point(spline_comp, cfg["dist"], cfg["offset"], 42.0)
        police = unreal.EditorLevelLibrary.spawn_actor_from_class(police_bp, loc, rot)
        police.set_actor_label(cfg["label"])
        police.set_editor_property("auto_possess_player", unreal.AutoReceiveInput.DISABLED)
        try:
            police.set_editor_property("auto_possess_ai", unreal.AutoPossessAI.PLACED_IN_WORLD_OR_SPAWNED)
            police.set_editor_property("SirenStrobeRate", cfg["rate"])
        except:
            pass

        # Vincular objetivo (Jugador)
        if hasattr(police, "set_target_player"):
            police.set_target_player(player)

        log(f"Patrulla desplegada: {cfg['label']} en dist={cfg['dist']/100.0:.1f}m (Sirena={cfg['rate']} Hz)")

    # 6. Desactivar GameMode residual
    world = unreal.EditorLevelLibrary.get_editor_world()
    world.get_world_settings().set_editor_property("default_game_mode", None)

    # 7. Guardar nivel
    unreal.EditorLevelLibrary.save_current_level()
    log("=== ¡GRAN PREMIO VR CONFIGURADO Y GUARDADO EXITOSAMENTE! ===")

if __name__ == "__main__":
    setup_grand_prix()

