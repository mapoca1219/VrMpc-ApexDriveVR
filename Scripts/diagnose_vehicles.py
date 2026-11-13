import unreal

def diagnose():
    out = []
    def log(msg):
        unreal.log(f"[FINAL_VERIFY] {msg}")
        out.append(str(msg))

    try:
        level_path = "/Game/Maps/L_RaceTrack_VR"
        unreal.EditorLevelLibrary.load_level(level_path)

        log("=== VERIFICACION FINAL DE BLUEPRINTS ===")
        blueprints = [
            ("BP_VrVehiclePawn", "/Game/Blueprints/BP_VrVehiclePawn"),
            ("BP_PoliceVehiclePawn", "/Game/Blueprints/BP_PoliceVehiclePawn")
        ]

        for name, path in blueprints:
            bp = unreal.EditorAssetLibrary.load_asset(path)
            gen_class = unreal.load_class(None, f"{path}.{name}_C")
            cdo = unreal.get_default_object(gen_class)
            log(f"Blueprint: {name}")
            
            # ChassisMesh
            cm = getattr(cdo, "chassis_mesh_component", None)
            if cm:
                log(f"   ChassisMesh: {cm.get_editor_property('static_mesh')}")
            else:
                log("   ChassisMesh: None")

            # Audio
            for a in cdo.get_components_by_class(unreal.AudioComponent):
                log(f"   Audio [{a.get_name()}]: Sound={a.get_editor_property('sound')}")

        log("=== VERIFICACION FINAL DE ACTORES EN NIVEL ===")
        for act in unreal.EditorLevelLibrary.get_all_level_actors():
            cname = act.get_class().get_name()
            lbl = act.get_actor_label()
            if "vehicle" in cname.lower() or "vehicle" in lbl.lower():
                log(f"Actor en nivel: {lbl} ({cname})")
                cm = getattr(act, "chassis_mesh_component", None)
                if cm:
                    log(f"   Instancia ChassisMesh: {cm.get_editor_property('static_mesh')}")
                for a in act.get_components_by_class(unreal.AudioComponent):
                    log(f"   Instancia Audio [{a.get_name()}]: Sound={a.get_editor_property('sound')}")

    finally:
        with open("/Users/marcopolo/Documents/Unreal Projects/VrMpc/Scripts/diagnostic_output.txt", "w") as f:
            f.write("\n".join(out))

if __name__ == "__main__":
    diagnose()
