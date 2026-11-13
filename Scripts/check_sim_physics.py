import unreal

def check_physics():
    unreal.EditorLevelLibrary.load_level("/Game/Maps/L_RaceTrack_VR")
    for a in unreal.EditorLevelLibrary.get_all_level_actors():
        label = a.get_actor_label()
        if "Player" in label or "Police_1" in label or "Rival_1" in label:
            mesh = a.get_component_by_class(unreal.SkeletalMeshComponent)
            if mesh:
                sim = mesh.is_simulating_physics()
                coll = mesh.get_collision_profile_name()
                unreal.log_warning(f"{label}: Mesh={mesh.get_name()}, is_simulating_physics()={sim}, CollisionProfile={coll}")

if __name__ == "__main__":
    check_physics()

