import unreal

lines = []
unreal.EditorLevelLibrary.load_level("/Game/Maps/L_RaceTrack_VR")
track = None
for a in unreal.EditorLevelLibrary.get_all_level_actors():
    if "RaceTrack" in a.get_class().get_name():
        track = a
        break
        
spline = track.get_component_by_class(unreal.SplineComponent)
lines.append(f"Spline length: {spline.get_spline_length()}")

for dist in range(0, int(spline.get_spline_length()), 15000):
    loc_d = spline.get_location_at_distance_along_spline(dist, unreal.SplineCoordinateSpace.WORLD)
    key = spline.find_input_key_closest_to_world_location(loc_d)
    loc = spline.get_location_at_spline_input_key(key, unreal.SplineCoordinateSpace.WORLD)
    dir_vec = spline.get_direction_at_spline_input_key(key, unreal.SplineCoordinateSpace.WORLD)
    right_vec = spline.get_right_vector_at_spline_input_key(key, unreal.SplineCoordinateSpace.WORLD)
    up_vec = spline.get_up_vector_at_spline_input_key(key, unreal.SplineCoordinateSpace.WORLD)
    
    cross1 = dir_vec.cross(up_vec)
    lines.append(f"Dist {dist}: Dir=({dir_vec.x:.2f},{dir_vec.y:.2f},{dir_vec.z:.2f}) Right=({right_vec.x:.2f},{right_vec.y:.2f},{right_vec.z:.2f}) DirXUp=({cross1.x:.2f},{cross1.y:.2f},{cross1.z:.2f})")

with open("/Users/marcopolo/Documents/Unreal Projects/VrMpc/Scripts/spline_test_output.txt", "w") as f:
    f.write("\n".join(lines))
