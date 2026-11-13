import unreal

mat = unreal.load_asset("/Game/Vehicles/Materials/M_SteeringWheel_Alcantara")
unreal.log_warning(f"M_SteeringWheel_Alcantara: {mat}")
if mat:
    unreal.log_warning(f"  Class: {mat.get_class().get_name()}")

