import unreal

def inspect_level():
    world = unreal.EditorLevelLibrary.get_editor_world()
    actors = unreal.EditorLevelLibrary.get_all_level_actors()
    print(f"Total actors in level: {len(actors)}", flush=True)

    buildings = []
    for a in actors:
        name = a.get_name()
        label = a.get_actor_label()
        loc = a.get_actor_location()
        if "Building" in name or "Building" in label or "City" in name or "City" in label or "Cube" in name:
            buildings.append((label, loc, a))
            print(f"Building: {label} at {loc}", flush=True)

    print(f"Found {len(buildings)} building/cube actors.", flush=True)

if __name__ == "__main__":
    inspect_level()
