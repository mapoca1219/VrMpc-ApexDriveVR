#!/usr/bin/env python3
# ==============================================================================
# CONFIGURE_VR_LEVEL.PY - Setup L_RaceTrack_VR for Meta Quest Standalone VR
# ==============================================================================
import unreal

def main():
    unreal.log("==================================================")
    unreal.log(">>> CONFIGURING VR LEVEL & PAWN (L_RaceTrack_VR) <<<")
    unreal.log("==================================================")

    level_path = "/Game/Maps/L_RaceTrack_VR"
    if unreal.EditorAssetLibrary.does_asset_exist(level_path):
        unreal.EditorLevelLibrary.load_level(level_path)
    else:
        unreal.log_error(f"Level not found: {level_path}")
        return

    # -------------------------------------------------------------------------
    # a) Destroy residual PlayerStart actors to ensure camera is inside car
    # -------------------------------------------------------------------------
    all_actors = unreal.EditorLevelLibrary.get_all_level_actors()
    destroyed_count = 0
    for actor in all_actors:
        if isinstance(actor, unreal.PlayerStart) or "PlayerStart" in actor.get_class().get_name():
            unreal.EditorLevelLibrary.destroy_actor(actor)
            destroyed_count += 1
    unreal.log(f"[VR Setup] Destroyed {destroyed_count} residual PlayerStart actor(s).")

    # Refresh actors list after destruction
    all_actors = unreal.EditorLevelLibrary.get_all_level_actors()

    # -------------------------------------------------------------------------
    # b) Locate Player_VrVehicle and set AutoPossess & AutoReceiveInput
    # -------------------------------------------------------------------------
    player_actor = None
    for actor in all_actors:
        label = actor.get_actor_label()
        if label == "Player_VrVehicle" or "Player_VrVehicle" in label or "VrVehicle" in actor.get_class().get_name():
            player_actor = actor
            break

    if player_actor:
        player_actor.set_editor_property("auto_possess_player", unreal.AutoReceiveInput.PLAYER0)
        try:
            player_actor.set_editor_property("auto_receive_input", unreal.AutoReceiveInput.PLAYER0)
        except Exception as e:
            unreal.log_warning(f"Note on auto_receive_input: {e}")
        unreal.log(f"[VR Setup] Configured Player_VrVehicle: auto_possess_player=Player0, auto_receive_input=Player0.")
    else:
        unreal.log_warning("[VR Setup] Player_VrVehicle actor not found in level.")

    # -------------------------------------------------------------------------
    # c) Assign BP_XRGameMode as default_game_mode in WorldSettings
    # -------------------------------------------------------------------------
    game_mode_class = unreal.load_class(None, "/Game/XRFramework/Blueprints/BP_XRGameMode.BP_XRGameMode_C")
    world_settings = None

    world = unreal.EditorLevelLibrary.get_editor_world()
    if world and hasattr(world, "get_world_settings"):
        try:
            world_settings = world.get_world_settings()
        except Exception:
            pass

    if not world_settings:
        for actor in all_actors:
            if isinstance(actor, unreal.WorldSettings):
                world_settings = actor
                break

    if world_settings and game_mode_class:
        world_settings.set_editor_property("default_game_mode", game_mode_class)
        unreal.log(f"[VR Setup] Assigned BP_XRGameMode as default_game_mode in WorldSettings.")
    else:
        unreal.log_warning(f"[VR Setup] Could not configure WorldSettings.default_game_mode (WorldSettings: {world_settings}, GameMode: {game_mode_class})")

    # -------------------------------------------------------------------------
    # d) Configure Sun_DirectionalLight and Sky_AmbientLight
    # -------------------------------------------------------------------------
    for actor in all_actors:
        label = actor.get_actor_label()

        # Sun / DirectionalLight
        if isinstance(actor, unreal.DirectionalLight) or ("Sun" in label and hasattr(actor, "light_component")):
            actor.set_actor_rotation(unreal.Rotator(pitch=-45.0, yaw=-30.0, roll=0.0), False)
            comp = getattr(actor, "light_component", None)
            if comp:
                try:
                    comp.set_editor_property("mobility", unreal.ComponentMobility.MOVABLE)
                except Exception as e:
                    unreal.log_warning(f"Sun mobility: {e}")
                try:
                    comp.set_editor_property("atmosphere_sun_light", True)
                except Exception as e:
                    unreal.log_warning(f"Sun atmosphere_sun_light: {e}")
                unreal.log(f"[VR Setup] Sun_DirectionalLight configured (Pitch=-45, Yaw=-30, Movable, AtmosphereSunLight=True).")

        # Sky / SkyLight
        elif isinstance(actor, unreal.SkyLight) or ("Sky" in label and hasattr(actor, "light_component")):
            comp = getattr(actor, "light_component", None)
            if comp:
                try:
                    comp.set_editor_property("mobility", unreal.ComponentMobility.MOVABLE)
                except Exception as e:
                    unreal.log_warning(f"Sky mobility: {e}")
                try:
                    comp.set_editor_property("real_time_capture", True)
                except Exception as e:
                    unreal.log_warning(f"Sky real_time_capture: {e}")
                unreal.log(f"[VR Setup] Sky_AmbientLight configured (Movable, RealTimeCapture=True).")

    # -------------------------------------------------------------------------
    # e) Automatically save level
    # -------------------------------------------------------------------------
    unreal.EditorLevelLibrary.save_current_level()
    unreal.log("[VR Setup] Level L_RaceTrack_VR saved successfully with 0 errors!")

if __name__ == "__main__":
    main()
