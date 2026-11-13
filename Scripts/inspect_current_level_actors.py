import unreal

def inspect_level_vehicle():
    unreal.EditorLevelLibrary.load_level("/Game/Maps/L_RaceTrack_VR")
    actors = unreal.EditorLevelLibrary.get_all_level_actors()
    
    print(f"[INSPECT_LEVEL] Total actors: {len(actors)}")
    for a in actors:
        lbl = a.get_actor_label()
        cls_name = a.get_class().get_name()
        loc = a.get_actor_location()
        print(f"Actor: '{lbl}' (Class: {cls_name}) at {loc}")
        
        if "Vehicle" in cls_name or "Vehicle" in lbl or "Police" in lbl or "Player" in lbl:
            print(f"  --- Details for {lbl} ---")
            for c in a.get_components_by_class(unreal.SceneComponent):
                c_name = c.get_name()
                c_class = c.get_class().get_name()
                rel_loc = c.get_editor_property("relative_location")
                rel_rot = c.get_editor_property("relative_rotation")
                rel_scale = c.get_editor_property("relative_scale3d")
                vis = c.get_editor_property("visible")
                extra = ""
                if isinstance(c, unreal.StaticMeshComponent):
                    sm = c.get_editor_property("static_mesh")
                    mat0 = c.get_material(0)
                    extra = f"Mesh: {sm.get_name() if sm else 'None'}, Mat0: {mat0.get_name() if mat0 else 'None'}"
                print(f"    Component: {c_name} ({c_class}) | Loc: {rel_loc} | Rot: {rel_rot} | Scale: {rel_scale} | Vis: {vis} | {extra}")

inspect_level_vehicle()

