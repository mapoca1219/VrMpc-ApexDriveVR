import unreal

mesh = unreal.load_asset("/Game/Vehicles/Meshes/SM_Steering_Wheel_Centered")
# Let's inspect LOD 0 sections
unreal.log_warning(f"Mesh: {mesh.get_name()}")
# Let's check if there are other meshes in /Engine/BasicShapes or /Game
for m_path in [
    "/Game/Vehicles/Meshes/SM_Steering_Wheel_Centered",
    "/Engine/BasicShapes/Cylinder",
    "/Engine/BasicShapes/Torus",
    "/Engine/EngineMeshes/SM_MatPreviewMesh_02"
]:
    m = unreal.load_asset(m_path)
    if m:
        b = m.get_bounding_box()
        unreal.log_warning(f"{m_path}: dx={b.max.x-b.min.x:.2f}, dy={b.max.y-b.min.y:.2f}, dz={b.max.z-b.min.z:.2f}")

