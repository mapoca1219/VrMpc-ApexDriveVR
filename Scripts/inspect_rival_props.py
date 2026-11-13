import unreal

def inspect():
    player_bp = unreal.load_class(None, "/Game/Blueprints/BP_VrVehiclePawn.BP_VrVehiclePawn_C")
    rival = unreal.EditorLevelLibrary.spawn_actor_from_class(player_bp, unreal.Vector(0, 0, 100))
    props = [p for p in dir(rival) if 'ai' in p.lower() or 'racer' in p.lower() or 'speed' in p.lower()]
    unreal.log_warning(f"Rival properties matching ai/racer/speed: {props}")
    unreal.EditorLevelLibrary.destroy_actor(rival)

if __name__ == "__main__":
    inspect()

