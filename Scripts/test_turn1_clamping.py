import unreal

def test_clamping_sim():
    unreal.EditorLevelLibrary.load_level("/Game/Maps/L_RaceTrack_VR")
    track = None
    for a in unreal.EditorLevelLibrary.get_all_level_actors():
        if "RaceTrackSpline" in a.get_class().get_name() or "Track" in a.get_actor_label():
            track = a
            break

    spline = track.get_component_by_class(unreal.SplineComponent)
    unreal.log_warning("=== TESTING CLAMP SIMULATION AT TURN 1 ===")

    # Test positions drifting straight past Point 1 (X=20000, Y=0) into (X=22000, Y=0), (X=25000, Y=0)
    for test_x in [20000.0, 22000.0, 25000.0, 28000.0, 32000.0]:
        test_loc = unreal.Vector(test_x, 0.0, 88.0)
        key = spline.find_input_key_closest_to_world_location(test_loc)
        spline_pos = spline.get_location_at_spline_input_key(key, unreal.SplineCoordinateSpace.WORLD)
        spline_dir = spline.get_direction_at_spline_input_key(key, unreal.SplineCoordinateSpace.WORLD)
        spline_right = spline.get_right_vector_at_spline_input_key(key, unreal.SplineCoordinateSpace.WORLD)
        
        offset = test_loc - spline_pos
        lateral = offset.dot(spline_right)
        unreal.log_warning(f"TestLoc ({test_x}, 0): Key={key:.2f}, SplinePos={spline_pos}, LateralDist={lateral:.1f} cm")

if __name__ == "__main__":
    test_clamping_sim()

