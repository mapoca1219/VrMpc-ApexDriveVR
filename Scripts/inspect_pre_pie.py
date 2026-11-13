import unreal

def inspect_pie():
    unreal.EditorLevelLibrary.load_level("/Game/Maps/L_RaceTrack_VR")
    world = unreal.EditorLevelLibrary.get_editor_world()
    
    unreal.log_warning("=== INSPECTING PRE-PLAY LEVEL ACTORS ===")
    actors = unreal.EditorLevelLibrary.get_all_level_actors()
    for a in actors:
        label = a.get_actor_label()
        cls = a.get_class().get_name()
        loc = a.get_actor_location()
        if any(k in label for k in ["Player", "Rival", "Police", "Camera", "Start", "Track"]):
            unreal.log_warning(f"Actor: {label} ({cls}) at {loc}")
            # Check components of vehicles
            if "VrVehicle" in cls or "Police" in cls:
                comps = a.get_components_by_class(unreal.MeshComponent)
                mesh_info = []
                for m in comps:
                    s_mesh = m.get_editor_property("static_mesh") if hasattr(m, "get_editor_property") and hasattr(m, "static_mesh") else None
                    sk_mesh = m.get_editor_property("skeletal_mesh_asset") if hasattr(m, "get_editor_property") and hasattr(m, "skeletal_mesh_asset") else None
                    vis = m.get_editor_property("visible") if hasattr(m, "get_editor_property") else True
                    mesh_info.append(f"{m.get_name()}(vis={vis}, sm={s_mesh.get_name() if s_mesh else 'None'}, skm={sk_mesh.get_name() if sk_mesh else 'None'})")
                unreal.log_warning(f"   -> Meshes: {', '.join(mesh_info)}")

if __name__ == "__main__":
    inspect_pie()

