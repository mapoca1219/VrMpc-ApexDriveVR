import unreal

def inspect_bp(bp_path):
    bp_gc = unreal.load_class(None, bp_path)
    if not bp_gc:
        unreal.log_warning(f"Could not load BP: {bp_path}")
        return
    cdo = unreal.get_default_object(bp_gc)
    unreal.log_warning(f"=== CDO for {bp_path} ===")
    for c in cdo.get_components_by_class(unreal.ActorComponent):
        c_name = c.get_name()
        c_class = c.get_class().get_name()
        extra = ""
        if isinstance(c, unreal.StaticMeshComponent):
            sm = c.get_editor_property("static_mesh")
            extra = f"StaticMesh={sm.get_name() if sm else 'None'}, RelativeScale={c.get_editor_property('relative_scale3d')}, RelativeLocation={c.get_editor_property('relative_location')}"
        elif isinstance(c, unreal.AudioComponent):
            snd = c.get_editor_property("sound")
            extra = f"Sound={snd.get_name() if snd else 'None'}"
        unreal.log_warning(f"  Component: {c_name} ({c_class}) - {extra}")

inspect_bp("/Game/Blueprints/BP_VrVehiclePawn.BP_VrVehiclePawn_C")
inspect_bp("/Game/Blueprints/BP_PoliceVehiclePawn.BP_PoliceVehiclePawn_C")

