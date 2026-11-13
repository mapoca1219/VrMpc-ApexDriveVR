import unreal

def log(msg):
    unreal.log_warning(f"[VERIFY_RACE] {msg}")

def verify():
    level_path = "/Game/Maps/L_RaceTrack_VR"
    unreal.EditorLevelLibrary.load_level(level_path)

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

    log("=== ESTADO DEL NIVEL L_RaceTrack_VR ===")
    if track_actor:
        spline = track_actor.get_component_by_class(unreal.SplineComponent)
        spline_len = spline.get_spline_length() if spline else 0.0
        wall_h = track_actor.get_editor_property("WallHeight") if hasattr(track_actor, "get_editor_property") else "N/A"
        wall_t = track_actor.get_editor_property("WallThickness") if hasattr(track_actor, "get_editor_property") else "N/A"
        log(f"TrackActor: {track_actor.get_actor_label()} | Longitud Spline: {spline_len:.1f} cm | Muros: H={wall_h}cm, T={wall_t}cm")
    else:
        log("ERROR: TrackActor no encontrado!")

    if player_actor:
        loc = player_actor.get_actor_location()
        rot = player_actor.get_actor_rotation()
        auto_p = player_actor.get_editor_property("auto_possess_player")
        log(f"PlayerActor: {player_actor.get_actor_label()} | Pos: {loc} | Rot: {rot} | AutoPossess: {auto_p}")
    else:
        log("ERROR: PlayerActor no encontrado!")

    if police_actor:
        loc = police_actor.get_actor_location()
        rot = police_actor.get_actor_rotation()
        auto_ai = police_actor.get_editor_property("auto_possess_ai")
        log(f"PoliceActor: {police_actor.get_actor_label()} | Pos: {loc} | Rot: {rot} | AutoPossessAI: {auto_ai}")
    else:
        log("ERROR: PoliceActor no encontrado!")

    if player_actor and police_actor:
        dist_euclid = player_actor.get_distance_to(police_actor)
        log(f"Distancia euclidiana entre Patrulla y Jugador: {dist_euclid/100.0:.2f} metros")

if __name__ == "__main__":
    verify()

