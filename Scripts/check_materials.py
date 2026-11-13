import unreal

mat_paths = [
    "/Game/Vehicles/Glass_-_Clear_001",
    "/Game/Vehicles/40__vd_glass",
    "/Game/Vehicles/Car_Paint_-_Red",
    "/Game/Vehicles/Car_Paint_-_Black",
    "/Game/Vehicles/Tire",
    "/Game/Vehicles/Plastic_-_Black_-_Bumpy_Small",
    "/Game/Vehicles/Materials/M_SteeringWheel_Alcantara",
    "/Game/Vehicles/Materials/M_Siren_Red",
    "/Game/Vehicles/Materials/M_Siren_Blue",
]

for p in mat_paths:
    m = unreal.load_asset(p)
    if m:
        unreal.log_warning(f"[MAT_CHECK] Found material: {p} ({m.get_class().get_name()})")
    else:
        unreal.log_warning(f"[MAT_CHECK] NOT FOUND: {p}")

