import unreal

unreal.EditorLevelLibrary.load_level("/Game/Maps/L_RaceTrack_VR")
actors = unreal.EditorLevelLibrary.get_all_level_actors()
for a in actors:
    unreal.log_warning(f"ACTOR: {a.get_actor_label()} ({a.get_class().get_name()}) at {a.get_actor_location()}")
    if "VrVehicle" in a.get_class().get_name() or "Player" in a.get_actor_label():
        for comp in a.get_components_by_class(unreal.SceneComponent):
            unreal.log_warning(f"  COMP: {comp.get_name()} ({comp.get_class().get_name()}) RelLoc={comp.get_relative_location()} RelRot={comp.get_relative_rotation()} RelScale={comp.get_relative_scale3d()} Visible={comp.is_visible()}")
            if isinstance(comp, unreal.StaticMeshComponent):
                sm = comp.get_editor_property("static_mesh")
                sm_name = sm.get_name() if sm else "None"
                mat = comp.get_material(0)
                mat_name = mat.get_name() if mat else "None"
                unreal.log_warning(f"    Mesh={sm_name}, Mat0={mat_name}")

