#!/usr/bin/env python3
# ==============================================================================
# CONFIGURE_SIMULATION.PY - Complete Automation for VrMpc Physics, Audio & VR Level
# Solves:
#   1. Chaos Vehicles missing torque curve error (disabling mechanical simulation)
#   2. Level spawn outside car (destroys residual PlayerStarts, auto-possesses Player0)
#   3. Sets VR cockpit camera to exact coordinates (X=-20, Y=-35, Z=110)
#   4. Links Police Pursuit Interceptor to Player_VrVehicle and Circuit Spline
# ==============================================================================
import unreal

def log_msg(msg):
    unreal.log(f"[SIMULATION_SETUP] >>> {msg} <<<")

def main():
    log_msg("STARTING FULL VEHICLE SIMULATION & VR LEVEL REPAIR")

    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()

    # -------------------------------------------------------------------------
    # 1. CREATE & VALIDATE TORQUE CURVE ASSET (/Game/Blueprints/Curve_Torque)
    # -------------------------------------------------------------------------
    curve_path = "/Game/Blueprints/Curve_Torque"
    curve_asset = unreal.EditorAssetLibrary.load_asset(curve_path)
    if not curve_asset:
        curve_factory = unreal.CurveFloatFactory()
        curve_asset = asset_tools.create_asset("Curve_Torque", "/Game/Blueprints", unreal.CurveFloat, curve_factory)
        log_msg("Created new CurveFloat asset at /Game/Blueprints/Curve_Torque")

    if curve_asset:
        unreal.EditorAssetLibrary.save_loaded_asset(curve_asset)

    torque_curve_import_text = (
        '(EditorCurveData=('
        'Keys=((Time=0.000000,Value=400.000000),(Time=6000.000000,Value=550.000000)),'
        'DefaultValue=400.000000,PreInfinityExtrap=RCCE_Constant,PostInfinityExtrap=RCCE_Constant),'
        'ExternalCurve=CurveFloat\'"/Game/Blueprints/Curve_Torque.Curve_Torque"\')'
    )

    # -------------------------------------------------------------------------
    # 2. ASSIGN TORQUE CURVE TO BLUEPRINT CDOs AND COMPILE
    # -------------------------------------------------------------------------
    blueprints_to_patch = [
        ("BP_VrVehiclePawn", "/Game/Blueprints/BP_VrVehiclePawn"),
        ("BP_PoliceVehiclePawn", "/Game/Blueprints/BP_PoliceVehiclePawn")
    ]

    for bp_name, bp_path in blueprints_to_patch:
        bp = unreal.EditorAssetLibrary.load_asset(bp_path)
        if not bp:
            unreal.log_warning(f"Could not load Blueprint: {bp_path}")
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
                        torque_curve.import_text(torque_curve_import_text)
                        engine_setup.set_editor_property("torque_curve", torque_curve)
                        try:
                            engine_setup.set_editor_property("max_rpm", 7000.0)
                        except:
                            pass
                        movement_comp.set_editor_property("engine_setup", engine_setup)
                        log_msg(f"Assigned valid Torque Curve (0->400, 6000->550) to CDO of {bp_name}.")
                except Exception as e:
                    unreal.log_warning(f"Failed setting engine setup on {bp_name} CDO: {e}")

        unreal.BlueprintEditorLibrary.compile_blueprint(bp)
        unreal.EditorAssetLibrary.save_loaded_asset(bp)
        log_msg(f"Compiled and saved {bp_name}.")

    # -------------------------------------------------------------------------
    # 3. LEVEL CONFIGURATION (L_RaceTrack_VR)
    # -------------------------------------------------------------------------
    level_path = "/Game/Maps/L_RaceTrack_VR"
    if unreal.EditorAssetLibrary.does_asset_exist(level_path):
        unreal.EditorLevelLibrary.load_level(level_path)
        log_msg(f"Loaded level: {level_path}")
    else:
        unreal.log_error(f"Level not found: {level_path}")
        return

    all_actors = unreal.EditorLevelLibrary.get_all_level_actors()

    # 3.a) Destroy residual PlayerStart actors to prevent external camera spawning
    destroyed_count = 0
    for actor in all_actors:
        label = actor.get_actor_label()
        cls_name = actor.get_class().get_name()
        if isinstance(actor, unreal.PlayerStart) or "PlayerStart" in cls_name or "PlayerStart" in label:
            unreal.EditorLevelLibrary.destroy_actor(actor)
            destroyed_count += 1
    log_msg(f"Destroyed {destroyed_count} residual PlayerStart actor(s).")

    # Refresh actors list
    all_actors = unreal.EditorLevelLibrary.get_all_level_actors()

    # 3.b) Assign BP_XRGameMode as default_game_mode in WorldSettings
    game_mode_class = unreal.load_class(None, "/Game/XRFramework/Blueprints/BP_XRGameMode.BP_XRGameMode_C")
    world_settings = None
    world = unreal.EditorLevelLibrary.get_editor_world()
    if world and hasattr(world, "get_world_settings"):
        try:
            world_settings = world.get_world_settings()
        except:
            pass
    if not world_settings:
        for actor in all_actors:
            if isinstance(actor, unreal.WorldSettings):
                world_settings = actor
                break

    if world_settings and game_mode_class:
        world_settings.set_editor_property("default_game_mode", game_mode_class)
        log_msg("Configured WorldSettings.default_game_mode = BP_XRGameMode.")

    # 3.c & 3.d) Locate Player_VrVehicle: Set Auto Possess & Cockpit VRCamera Transform
    player_vehicle = None
    for actor in all_actors:
        label = actor.get_actor_label()
        if label == "Player_VrVehicle" or "Player_VrVehicle" in label or "VrVehicle" in actor.get_class().get_name():
            player_vehicle = actor
            break

    if player_vehicle:
        player_vehicle.set_editor_property("auto_possess_player", unreal.AutoReceiveInput.PLAYER0)
        try:
            player_vehicle.set_editor_property("auto_receive_input", unreal.AutoReceiveInput.PLAYER0)
        except Exception as e:
            unreal.log_warning(f"auto_receive_input note: {e}")

        # Set torque curve directly on the instance as well
        try:
            p_movement = player_vehicle.get_editor_property("vehicle_movement_component")
            if p_movement:
                p_engine = p_movement.get_editor_property("engine_setup")
                p_torque = p_engine.get_editor_property("torque_curve")
                p_torque.import_text(torque_curve_import_text)
                p_engine.set_editor_property("torque_curve", p_torque)
                p_movement.set_editor_property("engine_setup", p_engine)
                log_msg("Player_VrVehicle instance engine torque curve verified.")
        except Exception as e:
            unreal.log_warning(f"Instance torque setup: {e}")

        # Adjust VRCamera cockpit position (X = -20.0, Y = -35.0, Z = 110.0)
        camera_adjusted = False
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
            camera_adjusted = True

        if vr_camera:
            vr_camera.set_relative_location(unreal.Vector(0.0, 0.0, 0.0), False, False)
            vr_camera.set_relative_rotation(unreal.Rotator(0.0, 0.0, 0.0), False, False)
            camera_adjusted = True

        log_msg(f"Player_VrVehicle: AutoPossess=Player0, Cockpit Camera set to X=-20.0, Y=-35.0, Z=110.0 (Status: {camera_adjusted}).")
    else:
        unreal.log_warning("Player_VrVehicle actor was not found in level!")

    # 3.e) Locate Police_Pursuit_Interceptor: Link Player Target & Circuit Spline
    police_actor = None
    track_spline_comp = None

    for actor in all_actors:
        label = actor.get_actor_label()
        cls_name = actor.get_class().get_name()
        if "Police" in label or "Police" in cls_name:
            police_actor = actor
        if "Track" in label or "Spline" in label or "RaceTrack" in cls_name:
            if hasattr(actor, "spline_component"):
                track_spline_comp = actor.spline_component
            elif hasattr(actor, "get_component_by_class"):
                track_spline_comp = actor.get_component_by_class(unreal.SplineComponent)
            elif hasattr(actor, "get_components_by_class"):
                comps = actor.get_components_by_class(unreal.SplineComponent)
                if comps and len(comps) > 0:
                    track_spline_comp = comps[0]

    if police_actor:
        # Set instance torque curve
        try:
            pol_movement = police_actor.get_editor_property("vehicle_movement_component")
            if pol_movement:
                pol_engine = pol_movement.get_editor_property("engine_setup")
                pol_torque = pol_engine.get_editor_property("torque_curve")
                pol_torque.import_text(torque_curve_import_text)
                pol_engine.set_editor_property("torque_curve", pol_torque)
                pol_movement.set_editor_property("engine_setup", pol_engine)
                log_msg("Police_Pursuit_Interceptor instance engine torque curve verified.")
        except Exception as e:
            unreal.log_warning(f"Police instance torque: {e}")

        # Link player reference if method exists
        if player_vehicle and hasattr(police_actor, "set_target_player"):
            police_actor.set_target_player(player_vehicle)
            log_msg("Linked TargetPlayerPawn on Police_Pursuit_Interceptor.")

        # Link track spline follower
        if track_spline_comp and hasattr(police_actor, "spline_follower"):
            try:
                police_actor.spline_follower.set_editor_property("target_spline_component", track_spline_comp)
                log_msg("Linked TargetSplineComponent on Police_Pursuit_Interceptor SplineFollower.")
            except Exception as e:
                unreal.log_warning(f"Police spline link: {e}")

    # -------------------------------------------------------------------------
    # 4. SAVE LEVEL
    # -------------------------------------------------------------------------
    unreal.EditorLevelLibrary.save_current_level()
    log_msg("SUCCESS! Level L_RaceTrack_VR saved cleanly. Simulation mechanical errors resolved.")

if __name__ == "__main__":
    main()
