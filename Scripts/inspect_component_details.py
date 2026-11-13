import unreal

def inspect_details():
    unreal.EditorLevelLibrary.load_level("/Game/Maps/L_RaceTrack_VR")
    actors = unreal.EditorLevelLibrary.get_all_level_actors()

    unreal.log_warning("=== INSPECTING COMPONENT TRANSFORMS & VISIBILITY ===")
    for a in actors:
        label = a.get_actor_label()
        if "Player" in label or "Rival_1" in label or "Police_1" in label:
            unreal.log_warning(f"--- ACTOR: {label} ---")
            unreal.log_warning(f"World Location: {a.get_actor_location()}")
            unreal.log_warning(f"World Rotation: {a.get_actor_rotation()}")
            unreal.log_warning(f"World Scale: {a.get_actor_scale3d()}")

            for c in a.get_components_by_class(unreal.SceneComponent):
                cname = c.get_name()
                if any(k in cname.lower() for k in ["chassis", "camera", "cockpit", "wheel", "mesh", "widget"]):
                    rel_loc = c.get_editor_property("relative_location") if hasattr(c, "get_editor_property") else "N/A"
                    rel_rot = c.get_editor_property("relative_rotation") if hasattr(c, "get_editor_property") else "N/A"
                    rel_scale = c.get_editor_property("relative_scale3d") if hasattr(c, "get_editor_property") else "N/A"
                    vis = c.is_visible() if hasattr(c, "is_visible") else "N/A"
                    attach = c.get_attach_parent().get_name() if c.get_attach_parent() else "None"
                    unreal.log_warning(f"  * {cname} (Class: {c.get_class().get_name()})")
                    unreal.log_warning(f"      Parent: {attach} | Visible: {vis}")
                    unreal.log_warning(f"      RelLoc: {rel_loc} | RelRot: {rel_rot} | RelScale: {rel_scale}")
                    if hasattr(c, "static_mesh") and c.static_mesh:
                        unreal.log_warning(f"      StaticMesh: {c.static_mesh.get_name()}")
                        # check materials
                        mats = [c.get_material(i).get_name() if c.get_material(i) else "None" for i in range(c.get_num_materials())]
                        unreal.log_warning(f"      Materials: {mats}")

if __name__ == "__main__":
    inspect_details()

