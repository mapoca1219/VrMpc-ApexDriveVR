import unreal

def verify():
    unreal.log_warning("[VERIFY] Verificando estado final del nivel L_RaceTrack_VR...")
    unreal.EditorLevelLibrary.load_level("/Game/Maps/L_RaceTrack_VR")

    actors = unreal.EditorLevelLibrary.get_all_level_actors()
    player = None
    rivals = []
    police = []
    track = None

    for a in actors:
        lbl = a.get_actor_label()
        cls_name = a.get_class().get_name()
        if "RaceTrack" in cls_name or "RaceTrack" in lbl:
            track = a
        elif "Player_VrVehicle" in lbl:
            player = a
        elif "Rival" in lbl:
            rivals.append(a)
        elif "Police" in lbl:
            police.append(a)

    unreal.log_warning(f"[VERIFY] Track: {track.get_actor_label() if track else 'None'}")
    if track:
        unreal.log_warning(f"  Width: {track.get_editor_property('TrackWidth')}, WallHeight: {track.get_editor_property('WallHeight')}, WallThickness: {track.get_editor_property('WallThickness')}")

    unreal.log_warning(f"[VERIFY] Player: {player.get_actor_label() if player else 'None'}")
    if player:
        for c in player.get_components_by_class(unreal.SceneComponent):
            c_name = c.get_name()
            if any(k in c_name for k in ["SteeringWheel", "Cockpit", "GearShift", "TextRender", "Audio"]):
                unreal.log_warning(f"  Player Comp: {c_name} ({c.get_class().get_name()})")

    unreal.log_warning(f"[VERIFY] Rivales encontrados: {len(rivals)}")
    for r in rivals:
        unreal.log_warning(f"  Rival: {r.get_actor_label()}, is_ai_racer={r.get_editor_property('is_ai_racer')}")

    unreal.log_warning(f"[VERIFY] Patrullas encontradas: {len(police)}")
    for p in police:
        chassis_scale = "N/A"
        siren_snd = "N/A"
        engine_snd = "N/A"
        for c in p.get_components_by_class(unreal.ActorComponent):
            if "Chassis" in c.get_name() and isinstance(c, unreal.SceneComponent):
                chassis_scale = str(c.get_editor_property("relative_scale3d"))
            elif "SirenAudio" in c.get_name() and isinstance(c, unreal.AudioComponent):
                snd = c.get_editor_property("sound")
                siren_snd = snd.get_name() if snd else "None"
            elif "EngineAudio" in c.get_name() and isinstance(c, unreal.AudioComponent):
                snd = c.get_editor_property("sound")
                engine_snd = snd.get_name() if snd else "None"
        unreal.log_warning(f"  Police: {p.get_actor_label()} | Scale: {chassis_scale} | Siren: {siren_snd} | Engine: {engine_snd}")

verify()

