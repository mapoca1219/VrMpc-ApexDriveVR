import unreal

out_lines = []
def log(msg):
    out_lines.append(str(msg))
    unreal.log_warning(str(msg))

log("=== INSPECTING SM_Merkurs_Chassis ===")
mesh = unreal.EditorAssetLibrary.load_asset("/Game/Vehicles/Meshes/SM_Merkurs_Chassis")
if mesh:
    num_sec = mesh.get_num_sections(0)
    log(f"Mesh: {mesh.get_name()}, Num Sections: {num_sec}")
    for i in range(num_sec):
        mat = mesh.get_material(i)
        mname = mat.get_name() if mat else "None"
        log(f"  Slot {i}: {mname}")
else:
    log("ERROR: SM_Merkurs_Chassis not found")

log("\n=== INSPECTING LEVEL ACTORS ===")
world = unreal.EditorLevelLibrary.get_editor_world()
if not world or "L_RaceTrack_VR" not in world.get_path_name():
    unreal.EditorLevelLibrary.load_level("/Game/Maps/L_RaceTrack_VR")

actors = unreal.EditorLevelLibrary.get_all_level_actors()
for a in actors:
    lbl = a.get_actor_label()
    if "Rival" in lbl or "Player" in lbl or "Police" in lbl:
        log(f"\nActor: {lbl} (Class: {a.get_class().get_name()})")
        for c in a.get_components_by_class(unreal.StaticMeshComponent):
            c_name = c.get_name()
            sm = c.get_editor_property("static_mesh")
            sm_name = sm.get_name() if sm else "None"
            num_mats = c.get_num_materials()
            log(f"  Comp: {c_name} | StaticMesh: {sm_name} | NumMats: {num_mats}")
            for s in range(min(5, num_mats)):
                m = c.get_material(s)
                log(f"    Mat[{s}]: {m.get_name() if m else 'None'}")
            if num_mats > 17:
                m17 = c.get_material(17)
                log(f"    Mat[17]: {m17.get_name() if m17 else 'None'}")

with open("/Users/marcopolo/Documents/Unreal Projects/VrMpc/Scripts/inspect_car_out.txt", "w") as f:
    f.write("\n".join(out_lines))

log("Inspection completed successfully.")
