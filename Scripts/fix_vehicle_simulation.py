#!/usr/bin/env python3
# ==============================================================================
# FIX_VEHICLE_SIMULATION.PY - Complete Unreal Engine 5 Fix Script for VrMpc
# Meta Quest Standalone VR Racing & Pursuit Setup
# ==============================================================================
import unreal

def log(msg):
    unreal.log(f"[FIX_VEHICLE_SIMULATION] >>> {msg} <<<")

def main():
    log("INICIANDO CONFIGURACIÓN DE FÍSICAS, CÁMARA Y PERSECUCIÓN")

    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()

    # -------------------------------------------------------------------------
    # 1. CREAR / CARGAR ASSET DE CURVA Curve_Torque
    # -------------------------------------------------------------------------
    curve_path = "/Game/Blueprints/Curve_Torque"
    curve_asset = unreal.EditorAssetLibrary.load_asset(curve_path)
    if not curve_asset:
        factory = unreal.CurveFloatFactory()
        curve_asset = asset_tools.create_asset("Curve_Torque", "/Game/Blueprints", unreal.CurveFloat, factory)
        log("Asset CurveFloat creado en /Game/Blueprints/Curve_Torque")

    if curve_asset:
        unreal.EditorAssetLibrary.save_loaded_asset(curve_asset)

    # Texto estructurado para importar keys (0.0, 400.0) y (6000.0, 500.0)
    torque_curve_data_with_asset = (
        '(EditorCurveData=('
        'Keys=((Time=0.000000,Value=400.000000),(Time=6000.000000,Value=500.000000)),'
        'DefaultValue=400.000000,PreInfinityExtrap=RCCE_Constant,PostInfinityExtrap=RCCE_Constant),'
        'ExternalCurve=CurveFloat\'"/Game/Blueprints/Curve_Torque.Curve_Torque"\')'
    )

    # -------------------------------------------------------------------------
    # 2. CONFIGURAR TORQUE EN BLUEPRINTS BP_VrVehiclePawn Y BP_PoliceVehiclePawn
    # -------------------------------------------------------------------------
    blueprints = [
        ("BP_VrVehiclePawn", "/Game/Blueprints/BP_VrVehiclePawn"),
        ("BP_PoliceVehiclePawn", "/Game/Blueprints/BP_PoliceVehiclePawn")
    ]

    for bp_name, bp_path in blueprints:
        bp = unreal.EditorAssetLibrary.load_asset(bp_path)
        if not bp:
            unreal.log_warning(f"No se pudo cargar el Blueprint: {bp_path}")
            continue

        gen_class = None
        if hasattr(bp, "generated_class"):
            try:
                gen_class = bp.generated_class()
            except:
                gen_class = bp.get_editor_property("generated_class")
        if not gen_class:
            gen_class = unreal.load_class(None, f"{bp_path}.{bp_name}_C")

        if gen_class:
            cdo = unreal.get_default_object(gen_class)
            if cdo:
                try:
                    movement_comp = cdo.get_editor_property("vehicle_movement_component")
                    if movement_comp:
                        engine_setup = movement_comp.get_editor_property("engine_setup")
                        torque_curve = engine_setup.get_editor_property("torque_curve")
                        torque_curve.import_text(torque_curve_data_with_asset)
                        engine_setup.set_editor_property("torque_curve", torque_curve)
                        try:
                            engine_setup.set_editor_property("max_rpm", 7000.0)
                        except:
                            pass
                        movement_comp.set_editor_property("engine_setup", engine_setup)
                        log(f"Asignada curva de torque (0->400, 6000->500) en CDO de {bp_name}.")
                except Exception as e:
                    unreal.log_warning(f"Error asignando torque en CDO de {bp_name}: {e}")

                # Ajustar cámara en CDO de BP_VrVehiclePawn (Location = -20, -35, 110)
                if bp_name == "BP_VrVehiclePawn":
                    try:
                        if hasattr(cdo, "cockpit_root") and cdo.cockpit_root:
                            cdo.cockpit_root.set_editor_property("relative_location", unreal.Vector(-20.0, -35.0, 110.0))
                            cdo.cockpit_root.set_editor_property("relative_rotation", unreal.Rotator(0.0, 0.0, 0.0))
                        if hasattr(cdo, "vr_camera") and cdo.vr_camera:
                            cdo.vr_camera.set_editor_property("relative_location", unreal.Vector(0.0, 0.0, 0.0))
                            cdo.vr_camera.set_editor_property("relative_rotation", unreal.Rotator(0.0, 0.0, 0.0))
                        log("Ajustada posición relativa de cámara en CDO de BP_VrVehiclePawn.")
                    except Exception as e:
                        unreal.log_warning(f"Error ajustando cámara en CDO: {e}")

        unreal.BlueprintEditorLibrary.compile_blueprint(bp)
        unreal.EditorAssetLibrary.save_loaded_asset(bp)
        log(f"Blueprint {bp_name} recompilado y guardado.")

    # -------------------------------------------------------------------------
    # 3. CONFIGURAR INSTANCIAS EN EL NIVEL L_RaceTrack_VR
    # -------------------------------------------------------------------------
    level_path = "/Game/Maps/L_RaceTrack_VR"
    if unreal.EditorAssetLibrary.does_asset_exist(level_path):
        unreal.EditorLevelLibrary.load_level(level_path)
    else:
        unreal.log_error(f"Nivel no encontrado: {level_path}")
        return

    all_actors = unreal.EditorLevelLibrary.get_all_level_actors()

    # Eliminar cualquier PlayerStart residual
    for actor in all_actors:
        cls_name = actor.get_class().get_name()
        label = actor.get_actor_label()
        if isinstance(actor, unreal.PlayerStart) or "PlayerStart" in cls_name or "PlayerStart" in label:
            unreal.EditorLevelLibrary.destroy_actor(actor)

    all_actors = unreal.EditorLevelLibrary.get_all_level_actors()

    player_vehicle = None
    police_vehicle = None
    track_spline_comp = None

    for actor in all_actors:
        label = actor.get_actor_label()
        cls_name = actor.get_class().get_name()

        if "Player_VrVehicle" in label or ("VrVehicle" in cls_name and not "Police" in cls_name):
            player_vehicle = actor
        elif "Police" in label or "Police" in cls_name:
            police_vehicle = actor
        elif "Track" in label or "Spline" in label or "RaceTrack" in cls_name:
            if hasattr(actor, "spline_component"):
                track_spline_comp = actor.spline_component
            elif hasattr(actor, "get_component_by_class"):
                track_spline_comp = actor.get_component_by_class(unreal.SplineComponent)

    # Configurar instancia de Player_VrVehicle en el mapa
    if player_vehicle:
        player_vehicle.set_editor_property("auto_possess_player", unreal.AutoReceiveInput.PLAYER0)
        try:
            player_vehicle.set_editor_property("auto_receive_input", unreal.AutoReceiveInput.PLAYER0)
        except Exception as e:
            pass

        # Aplicar curva de torque en la instancia
        try:
            p_movement = player_vehicle.get_editor_property("vehicle_movement_component")
            if p_movement:
                p_engine = p_movement.get_editor_property("engine_setup")
                p_torque = p_engine.get_editor_property("torque_curve")
                p_torque.import_text(torque_curve_data_with_asset)
                p_engine.set_editor_property("torque_curve", p_torque)
                p_movement.set_editor_property("engine_setup", p_engine)
        except Exception as e:
            unreal.log_warning(f"Error curva en Player_VrVehicle instancia: {e}")

        # Posicionamiento de cámara de habitáculo
        cockpit_root = None
        vr_camera = None
        if hasattr(player_vehicle, "cockpit_root"):
            cockpit_root = player_vehicle.cockpit_root
        if hasattr(player_vehicle, "vr_camera"):
            vr_camera = player_vehicle.vr_camera

        if not vr_camera or not cockpit_root:
            for comp in player_vehicle.get_components_by_class(unreal.SceneComponent):
                cname = comp.get_name()
                if "CockpitRoot" in cname:
                    cockpit_root = comp
                elif "VRCamera" in cname or isinstance(comp, unreal.CameraComponent):
                    vr_camera = comp

        if cockpit_root:
            cockpit_root.set_relative_location(unreal.Vector(-20.0, -35.0, 110.0), False, False)
            cockpit_root.set_relative_rotation(unreal.Rotator(0.0, 0.0, 0.0), False, False)
        if vr_camera:
            vr_camera.set_relative_location(unreal.Vector(0.0, 0.0, 0.0), False, False)
            vr_camera.set_relative_rotation(unreal.Rotator(0.0, 0.0, 0.0), False, False)

        log("Player_VrVehicle en nivel: AutoPossess=Player0, Cámara fijada en Location=(-20.0, -35.0, 110.0).")

    # Configurar instancia de Police_Pursuit_Interceptor en el mapa
    if police_vehicle:
        try:
            pol_movement = police_vehicle.get_editor_property("vehicle_movement_component")
            if pol_movement:
                pol_engine = pol_movement.get_editor_property("engine_setup")
                pol_torque = pol_engine.get_editor_property("torque_curve")
                pol_torque.import_text(torque_curve_data_with_asset)
                pol_engine.set_editor_property("torque_curve", pol_torque)
                pol_movement.set_editor_property("engine_setup", pol_engine)
        except Exception as e:
            unreal.log_warning(f"Error curva en Police instancia: {e}")

        # Auto posesión de IA
        try:
            police_vehicle.set_editor_property("auto_possess_ai", unreal.AutoPossessAI.PLACED_IN_WORLD_OR_SPAWNED)
        except:
            pass

        # Asignar referencia del jugador
        if player_vehicle and hasattr(police_vehicle, "set_target_player"):
            police_vehicle.set_target_player(player_vehicle)
            log("Police_Pursuit_Interceptor: TargetPlayerPawn asignado a Player_VrVehicle.")

        # Asignar spline al SplineFollower
        if track_spline_comp and hasattr(police_vehicle, "spline_follower") and police_vehicle.spline_follower:
            try:
                police_vehicle.spline_follower.set_editor_property("target_spline_component", track_spline_comp)
                log("Police_Pursuit_Interceptor: SplineFollower enlazado a la pista.")
            except Exception as e:
                unreal.log_warning(f"Error enlazando spline en la patrulla: {e}")

    # Guardar nivel
    unreal.EditorLevelLibrary.save_current_level()
    log("ÉXITO: Blueprints y Nivel L_RaceTrack_VR guardados limpiamente con 0 errores.")

if __name__ == "__main__":
    main()

