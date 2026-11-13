import unreal

def log(msg):
    unreal.log(f"[ALIGN_RACE] >>> {msg} <<<")

def align_race():
    log("Iniciando alineación de vehículos y regeneración de pista...")
    level_path = "/Game/Maps/L_RaceTrack_VR"
    unreal.EditorLevelLibrary.load_level(level_path)

    # 1. Buscar actores clave
    track_actor = None
    player_actor = None
    police_actor = None

    for a in unreal.EditorLevelLibrary.get_all_level_actors():
        cls_name = a.get_class().get_name()
        label = a.get_actor_label()
        if "RaceTrackSpline" in cls_name or "Track" in label:
            track_actor = a
        elif "BP_VrVehiclePawn" in cls_name or "Player" in label:
            player_actor = a
        elif "BP_PoliceVehiclePawn" in cls_name or "Police" in label:
            police_actor = a

    if not track_actor:
        log("ERROR: No se encontró ARaceTrackSpline en el nivel.")
        return

    # 2. Configurar propiedades de la pista (muros de contención altos de 2.2m)
    try:
        track_actor.set_editor_property("WallHeight", 220.0)
        track_actor.set_editor_property("WallThickness", 60.0)
        track_actor.set_editor_property("bGenerateGuardrails", True)
        curr_loc = track_actor.get_actor_location()
        track_actor.set_actor_location(curr_loc, False, False)
        log("Pista ARaceTrackSpline configurada con muros de contención de 2.2m (WallHeight=220, WallThickness=60).")
    except Exception as e:
        log(f"Aviso actualizando propiedades de pista: {e}")

    spline_comp = track_actor.get_component_by_class(unreal.SplineComponent)
    if not spline_comp:
        log("ERROR: No se encontró SplineComponent en track_actor.")
        return

    spline_len = spline_comp.get_spline_length()
    log(f"Longitud total del circuito: {spline_len:.1f} cm ({spline_len/100.0:.1f} m)")

    # 3. Ubicar al jugador en la recta principal (ej. distancia 1500 cm = 15m)
    player_dist = 2000.0
    player_loc = spline_comp.get_location_at_distance_along_spline(player_dist, unreal.SplineCoordinateSpace.WORLD)
    player_rot = spline_comp.get_rotation_at_distance_along_spline(player_dist, unreal.SplineCoordinateSpace.WORLD)
    # Elevar ligeramente sobre el asfalto (35cm)
    player_loc.z += 35.0

    if player_actor:
        player_actor.set_actor_location_and_rotation(player_loc, player_rot, False, True)
        log(f"Jugador posicionado en {player_loc} con rotación {player_rot}")
    else:
        log("ADVERTENCIA: No se encontró player_actor para alinear.")

    # 4. Ubicar a la patrulla 18 metros detrás del jugador (distancia 200 cm = 2m)
    police_dist = 200.0
    police_loc = spline_comp.get_location_at_distance_along_spline(police_dist, unreal.SplineCoordinateSpace.WORLD)
    police_rot = spline_comp.get_rotation_at_distance_along_spline(police_dist, unreal.SplineCoordinateSpace.WORLD)
    police_loc.z += 40.0

    if police_actor:
        police_actor.set_actor_location_and_rotation(police_loc, police_rot, False, True)
        # Asegurar asignación del jugador a la patrulla
        if hasattr(police_actor, "set_target_player") and player_actor:
            police_actor.set_target_player(player_actor)
        log(f"Patrulla posicionada en {police_loc} con rotación {police_rot} persiguiendo al jugador.")
    else:
        log("ADVERTENCIA: No se encontró police_actor para alinear.")

    # 5. Guardar nivel
    unreal.EditorLevelLibrary.save_current_level()
    log("Nivel L_RaceTrack_VR guardado exitosamente con pista y persecución alineadas.")

if __name__ == "__main__":
    align_race()
