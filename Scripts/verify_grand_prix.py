import unreal

def verify():
    unreal.EditorLevelLibrary.load_level("/Game/Maps/L_RaceTrack_VR")
    actors = unreal.EditorLevelLibrary.get_all_level_actors()
    unreal.log_warning(f"=== PARRILLA DEL GRAN PREMIO VR ({len(actors)} ACTORES) ===")
    
    for a in sorted(actors, key=lambda x: x.get_actor_label()):
        label = a.get_actor_label()
        cls = a.get_class().get_name()
        loc = a.get_actor_location()
        if any(k in label for k in ["Player", "Rival", "Police", "Track"]):
            extra = ""
            if hasattr(a, "get_editor_property"):
                try:
                    if "Player" in label:
                        p = a.get_editor_property("auto_possess_player")
                        ai = a.get_editor_property("is_ai_racer")
                        extra = f" | PlayerPossess={p}, is_ai_racer={ai}"
                    elif "Rival" in label:
                        ai = a.get_editor_property("is_ai_racer")
                        spd = a.get_editor_property("ai_target_speed_kmh")
                        extra = f" | is_ai_racer={ai}, TargetSpeed={spd} km/h"
                    elif "Police" in label:
                        rate = a.get_editor_property("SirenStrobeRate")
                        extra = f" | StrobeRate={rate} Hz"
                    elif "Track" in label:
                        w = a.get_editor_property("TrackWidth")
                        h = a.get_editor_property("WallHeight")
                        extra = f" | Width={w}cm, WallHeight={h}cm"
                except:
                    pass
            unreal.log_warning(f"  * [{cls}] {label} en ({loc.x:.1f}, {loc.y:.1f}, {loc.z:.1f}){extra}")

if __name__ == "__main__":
    verify()

