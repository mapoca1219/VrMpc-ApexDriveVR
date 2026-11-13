import unreal

eal = unreal.EditorLevelLibrary
eal.load_level("/Game/Maps/L_RaceTrack_VR")
actors = eal.get_all_level_actors()
for a in actors:
    if a.get_actor_label() == "Player_VrVehicle":
        unreal.log_warning(f"FOUND Player_VrVehicle at {a.get_actor_location()}")
        for c in a.get_components_by_class(unreal.SceneComponent):
            unreal.log_warning(f"  Component: {c.get_name()} ({c.get_class().get_name()})")
            unreal.log_warning(f"    RelLoc: {c.get_editor_property('relative_location')}")
            unreal.log_warning(f"    RelRot: {c.get_editor_property('relative_rotation')}")
            unreal.log_warning(f"    RelScale: {c.get_editor_property('relative_scale3d')}")
            if isinstance(c, unreal.StaticMeshComponent):
                sm = c.get_editor_property("static_mesh")
                unreal.log_warning(f"    StaticMesh: {sm.get_name() if sm else 'None'}")

