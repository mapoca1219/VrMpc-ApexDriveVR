import unreal

world = unreal.EditorLevelLibrary.get_editor_world()
for a in unreal.EditorLevelLibrary.get_all_level_actors():
    if a.get_actor_label() == "Player_VrVehicle":
        unreal.log_warning(f"=== Player_VrVehicle Location={a.get_actor_location()} ===")
        for comp in a.get_components_by_class(unreal.SceneComponent):
            cname = comp.get_name()
            rloc = comp.get_editor_property("relative_location")
            rrot = comp.get_editor_property("relative_rotation")
            rscale = comp.get_editor_property("relative_scale3d")
            wloc = comp.get_world_location()
            bounds = comp.get_bounds() if hasattr(comp, "get_bounds") else None
            unreal.log_warning(f"COMP: {cname} ({comp.get_class().get_name()})")
            unreal.log_warning(f"  RelLoc={rloc}, RelRot={rrot}, RelScale={rscale}")
            unreal.log_warning(f"  WorldLoc={wloc}")
            if bounds:
                unreal.log_warning(f"  Bounds: Origin={bounds.origin}, BoxExtent={bounds.box_extent}, Radius={bounds.sphere_radius}")

