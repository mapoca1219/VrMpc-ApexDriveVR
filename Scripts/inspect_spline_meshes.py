import unreal

unreal.EditorLevelLibrary.load_level("/Game/Maps/L_RaceTrack_VR")
track = None
for a in unreal.EditorLevelLibrary.get_all_level_actors():
    if "RaceTrack" in a.get_class().get_name():
        track = a
        break

spline_meshes = track.get_components_by_class(unreal.SplineMeshComponent)
lines = [f"Total SplineMeshComponents on track: {len(spline_meshes)}"]

for i, sm in enumerate(spline_meshes[:15]):
    start_pos, start_tan = sm.get_start_position_and_tangent()
    end_pos, end_tan = sm.get_end_position_and_tangent()
    start_scale = sm.get_start_scale()
    start_offset = sm.get_start_offset()
    mesh = sm.get_editor_property("static_mesh")
    mesh_name = mesh.get_name() if mesh else "None"
    lines.append(f"SM {i}: Mesh={mesh_name} | StartOffset={start_offset} | StartScale={start_scale} | Pos={start_pos}")

with open("/Users/marcopolo/Documents/Unreal Projects/VrMpc/Scripts/spline_mesh_inspect.txt", "w") as f:
    f.write("\n".join(lines))

