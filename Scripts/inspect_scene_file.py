import unreal

unreal.EditorLevelLibrary.load_level("/Game/Maps/L_RaceTrack_VR")
all_actors = unreal.EditorLevelLibrary.get_all_level_actors()

with open("/Users/marcopolo/Documents/Unreal Projects/VrMpc/inspect_out.txt", "w") as f:
    f.write(f"=== TOTAL ACTORS: {len(all_actors)} ===\n")
    buildings = [a for a in all_actors if "City_" in a.get_actor_label() or "Building" in a.get_actor_label() or "Skyscraper" in a.get_actor_label()]
    f.write(f"Total Buildings: {len(buildings)}\n")
    for b in buildings[:25]:
        loc = b.get_actor_location()
        scale = b.get_actor_scale3d()
        comp = b.get_component_by_class(unreal.StaticMeshComponent)
        mat = comp.get_material(0) if comp else None
        mat_name = mat.get_name() if mat else "None"
        f.write(f"  {b.get_actor_label():20} | Loc: ({loc.x:.0f}, {loc.y:.0f}, {loc.z:.0f}) | Scale: ({scale.x:.1f}, {scale.y:.1f}, {scale.z:.1f}) | Mat: {mat_name}\n")
