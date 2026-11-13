import unreal

def inspect_police_bp():
    bp_police = unreal.EditorAssetLibrary.load_asset("/Game/Blueprints/BP_PoliceVehiclePawn")
    police_actor = None
    for a in unreal.EditorLevelLibrary.get_all_level_actors():
        if "Police" in a.get_actor_label():
            police_actor = a
            break

    if police_actor:
        unreal.log_warning(f"Inspecting Police Actor in level: {police_actor.get_actor_label()}")
        for ac in police_actor.get_components_by_class(unreal.AudioComponent):
            snd = ac.get_editor_property("sound")
            unreal.log_warning(f"   AudioComp: {ac.get_name()}, Sound={snd.get_name() if snd else 'None'}, AutoActivate={ac.get_editor_property('auto_activate')}")

if __name__ == "__main__":
    inspect_police_bp()

