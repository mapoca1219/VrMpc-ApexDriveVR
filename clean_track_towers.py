import unreal

def inspect_and_clean_buildings():
    print("=== INSPECTING AND FIXING BUILDINGS ON TRACK ===", flush=True)
    unreal.EditorLevelLibrary.load_level("/Game/Maps/L_RaceTrack_VR")
    actors = unreal.EditorLevelLibrary.get_all_level_actors()

    track = None
    for a in actors:
        if "RaceTrack" in a.get_actor_label():
            track = a
            break

    if not track:
        print("ERROR: Track not found!", flush=True)
        return

    spline = track.get_component_by_class(unreal.SplineComponent)
    spline_len = spline.get_spline_length()
    print(f"Track Spline Length: {spline_len:.0f} cm", flush=True)

    # Sample spline points to get the full bounding box and bounds of the track
    min_x, max_x = float('inf'), float('-inf')
    min_y, max_y = float('inf'), float('-inf')
    for d in range(0, int(spline_len), 200):
        pos = spline.get_location_at_distance_along_spline(float(d), unreal.SplineCoordinateSpace.WORLD)
        min_x = min(min_x, pos.x)
        max_x = max(max_x, pos.x)
        min_y = min(min_y, pos.y)
        max_y = max(max_y, pos.y)

    print(f"Track Bounds: X=[{min_x:.0f}, {max_x:.0f}], Y=[{min_y:.0f}, {max_y:.0f}]", flush=True)

    # Check each tower
    towers = [a for a in actors if "Skyline_Tower" in a.get_actor_label() or "Building" in a.get_actor_label()]
    print(f"Checking {len(towers)} towers...", flush=True)

    destroyed_count = 0
    for t in towers:
        loc = t.get_actor_location()
        key = spline.find_input_key_closest_to_world_location(loc)
        spline_pos = spline.get_location_at_spline_input_key(key, unreal.SplineCoordinateSpace.WORLD)
        
        dx = loc.x - spline_pos.x
        dy = loc.y - spline_pos.y
        dist_2d = (dx*dx + dy*dy) ** 0.5
        
        print(f"Tower {t.get_actor_label()} at ({loc.x:.0f}, {loc.y:.0f}): distance to track = {dist_2d:.0f} cm", flush=True)
        
        # If tower is within 85 meters (8500 cm) of the track centerline, DESTROY IT!
        if dist_2d < 8500.0:
            print(f"  --> DESTROYING {t.get_actor_label()} because it is on/too close to the track! ({dist_2d:.0f} cm < 8500 cm)", flush=True)
            unreal.EditorLevelLibrary.destroy_actor(t)
            destroyed_count += 1

    print(f"Destroyed {destroyed_count} towers that were blocking the road.", flush=True)

    unreal.EditorLevelLibrary.save_current_level()
    print("=== MAP CLEANED AND SAVED SUCCESSFULLY ===", flush=True)

if __name__ == "__main__":
    inspect_and_clean_buildings()
