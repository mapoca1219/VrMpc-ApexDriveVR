import unreal

unreal.EditorLevelLibrary.load_level("/Game/Maps/L_RaceTrack_VR")
all_actors = unreal.EditorLevelLibrary.get_all_level_actors()

print(f"=== TOTAL ACTORS IN LEVEL: {len(all_actors)} ===", flush=True)

track = None
for a in all_actors:
    if "RaceTrack" in a.get_actor_label() or "RaceTrack" in a.get_class().get_name():
        track = a
        break

spline = track.get_component_by_class(unreal.SplineComponent) if track else None
spline_len = spline.get_spline_length() if spline else 0
print(f"Track: {track.get_actor_label() if track else 'None'}, SplineLength: {spline_len}", flush=True)

buildings = [a for a in all_actors if "City_" in a.get_actor_label() or "Building" in a.get_actor_label() or "Skyscraper" in a.get_actor_label()]
print(f"Total Buildings: {len(buildings)}", flush=True)

for b in buildings[:15]:
    loc = b.get_actor_location()
    scale = b.get_actor_scale3d()
    comp = b.get_component_by_class(unreal.StaticMeshComponent)
    mat = comp.get_material(0) if comp else None
    mat_name = mat.get_name() if mat else "None"
    
    # Calculate distance to spline
    dist_to_spline = 999999.0
    if spline:
        key = spline.find_input_key_closest_to_world_location(loc)
        spline_pos = spline.get_location_at_spline_input_key(key, unreal.SplineCoordinateSpace.WORLD)
        diff = loc - spline_pos
        dist_to_spline = diff.length()

    print(f"  {b.get_actor_label():20} | Loc: ({loc.x:.0f}, {loc.y:.0f}, {loc.z:.0f}) | Scale: ({scale.x:.1f}, {scale.y:.1f}, {scale.z:.1f}) | Mat: {mat_name:25} | DistToSpline: {dist_to_spline:.0f} cm", flush=True)
