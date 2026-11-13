import unreal

out = []
def log(s):
    out.append(s)

unreal.EditorLevelLibrary.load_level("/Game/Maps/L_RaceTrack_VR")
actors = unreal.EditorLevelLibrary.get_all_level_actors()

log(f"Total actors in L_RaceTrack_VR: {len(actors)}")
for a in actors:
    lbl = a.get_actor_label()
    cls_name = a.get_class().get_name()
    loc = a.get_actor_location()
    log(f"Actor: '{lbl}' (Class: {cls_name}) Loc={loc}")
    if any(k in lbl or k in cls_name for k in ["Vehicle", "Player", "Police", "Rival"]):
        for c in a.get_components_by_class(unreal.SceneComponent):
            c_name = c.get_name()
            rel_loc = c.get_editor_property("relative_location")
            rel_rot = c.get_editor_property("relative_rotation")
            rel_scale = c.get_editor_property("relative_scale3d")
            vis = c.get_editor_property("visible")
            mesh_name = "None"
            mat0_name = "None"
            if isinstance(c, unreal.StaticMeshComponent):
                sm = c.get_editor_property("static_mesh")
                mesh_name = sm.get_name() if sm else "None"
                mat0 = c.get_material(0)
                mat0_name = mat0.get_name() if mat0 else "None"
            log(f"    Comp: {c_name} ({c.get_class().get_name()}) | Loc={rel_loc} | Rot={rel_rot} | Scale={rel_scale} | Vis={vis} | Mesh={mesh_name} | Mat0={mat0_name}")

with open("/Users/marcopolo/Documents/Unreal Projects/VrMpc/Scripts/level_inspect.txt", "w") as f:
    f.write("\n".join(out))

