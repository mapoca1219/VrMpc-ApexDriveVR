import unreal

def run():
    print("=== INSPECTING PLAYER VR VEHICLE ===", flush=True)
    all_actors = unreal.EditorLevelLibrary.get_all_level_actors()
    player = None
    for a in all_actors:
        lbl = a.get_actor_label()
        cls = a.get_class().get_name()
        if "Player" in lbl or ("VrVehicle" in cls and "Rival" not in lbl and "Police" not in lbl):
            player = a
            break

    if not player:
        print("Player not found!", flush=True)
        return

    print(f"Found Player Actor: {player.get_actor_label()} ({player.get_class().get_name()})", flush=True)
    comps = player.get_components_by_class(unreal.SceneComponent)
    for c in comps:
        name = c.get_name()
        loc = c.get_relative_location()
        rot = c.get_relative_rotation()
        scale = c.get_relative_scale3d()
        vis = c.get_editor_property("visible") if hasattr(c, "visible") else True
        mesh_info = ""
        mat_info = ""
        if isinstance(c, unreal.StaticMeshComponent):
            sm = c.get_editor_property("static_mesh")
            mesh_info = f" | Mesh: {sm.get_name() if sm else 'None'}"
            num_mats = c.get_num_materials()
            mats = [c.get_material(m).get_name() if c.get_material(m) else "None" for m in range(min(num_mats, 6))]
            mat_info = f" | Mats: {mats}"
        print(f"  Comp: {name:30} | Loc: {loc} | Rot: {rot} | Scale: {scale} | Vis: {vis}{mesh_info}{mat_info}", flush=True)

if __name__ == "__main__":
    run()
