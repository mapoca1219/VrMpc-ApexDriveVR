import unreal

unreal.EditorLevelLibrary.load_level("/Game/Maps/L_RaceTrack_VR")
all_actors = unreal.EditorLevelLibrary.get_all_level_actors()
buildings = [a for a in all_actors if "City_" in a.get_actor_label() or "Building" in a.get_actor_label() or "Skyscraper" in a.get_actor_label()]
print(f"Total buildings in map: {len(buildings)}", flush=True)
for b in buildings[:10]:
    comp = b.get_component_by_class(unreal.StaticMeshComponent)
    mat = comp.get_material(0) if comp else None
    print(f"  {b.get_actor_label()}: {mat.get_name() if mat else 'None'}", flush=True)
