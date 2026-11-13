import unreal

def inspect_meshes_and_audio():
    unreal.EditorLevelLibrary.load_level("/Game/Maps/L_RaceTrack_VR")

    unreal.log_warning("=== INSPECTING MESH BOUNDS & ASSETS ===")
    for mesh_path in [
        "/Game/Vehicles/Meshes/SM_Merkurs_Chassis",
        "/Game/Vehicles/Meshes/SM_Steering_Wheel_Centered",
        "/Game/Vehicles/Meshes/SM_Hyundai_Ioniq5"
    ]:
        mesh = unreal.EditorAssetLibrary.load_asset(mesh_path)
        if mesh:
            bounds = mesh.get_bounds()
            unreal.log_warning(f"Mesh {mesh_path}:")
            unreal.log_warning(f"   Origin: {bounds.origin}")
            unreal.log_warning(f"   Box Extent: {bounds.box_extent} (Size: {bounds.box_extent.x*2:.1f} x {bounds.box_extent.y*2:.1f} x {bounds.box_extent.z*2:.1f} cm)")
            unreal.log_warning(f"   Sphere Radius: {bounds.sphere_radius:.1f}")

    unreal.log_warning("=== INSPECTING AUDIO ASSETS & COMPONENTS ===")
    for a in unreal.EditorLevelLibrary.get_all_level_actors():
        label = a.get_actor_label()
        if "Player" in label or "Police_1" in label or "Rival_1" in label:
            audios = a.get_components_by_class(unreal.AudioComponent)
            audio_info = []
            for ac in audios:
                snd = ac.get_editor_property("sound") if hasattr(ac, "get_editor_property") else None
                sname = snd.get_name() if snd else "None"
                vol = ac.get_editor_property("volume_multiplier") if hasattr(ac, "get_editor_property") else 1.0
                atten = ac.get_editor_property("attenuation_settings") if hasattr(ac, "get_editor_property") else None
                audio_info.append(f"{ac.get_name()}(sound={sname}, vol={vol}, atten={atten is not None})")
            unreal.log_warning(f"{label} Audios: {', '.join(audio_info)}")

if __name__ == "__main__":
    inspect_meshes_and_audio()

