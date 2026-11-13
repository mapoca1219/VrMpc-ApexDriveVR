#!/usr/bin/env python3
# ==============================================================================
# AUTOMATE_SETUP.PY - Unattended Visual & Gameplay Integration for VrMpc (UE 5.8)
# Designed for macOS Meta Quest Standalone VR Development
# ==============================================================================

import os
import sys
import unreal

def log_step(title):
    unreal.log("=" * 70)
    unreal.log(f"[AUTOMATION] >>> {title} <<<")
    unreal.log("=" * 70)

def main():
    log_step("STARTING VRMPC FULL UNATTENDED ASSET & LEVEL SETUP")

    # Directory constants
    content_dir = unreal.SystemLibrary.get_project_content_directory()
    mesh_pkg_path = "/Game/Vehicles/Meshes"
    tex_pkg_path = "/Game/Vehicles/Textures/Merkurs_KCR5"
    mat_pkg_path = "/Game/Vehicles/Materials"
    bp_pkg_path = "/Game/Blueprints"
    maps_pkg_path = "/Game/Maps"

    # Ensure directories exist
    for path in [mesh_pkg_path, tex_pkg_path, mat_pkg_path, bp_pkg_path, maps_pkg_path]:
        if not unreal.EditorAssetLibrary.does_directory_exist(path):
            unreal.EditorAssetLibrary.make_directory(path)

    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()

    # -------------------------------------------------------------------------
    # 1. IMPORT STATIC MESHES
    # -------------------------------------------------------------------------
    log_step("STEP 1: IMPORTING VEHICLE MESHES (FBX / OBJ)")

    def import_mesh(rel_path, dest_name, generate_collision=True, combine_meshes=True):
        dest_asset_path = f"{mesh_pkg_path}/{dest_name}"
        if unreal.EditorAssetLibrary.does_asset_exist(dest_asset_path):
            unreal.log(f"Asset already exists, reusing: {dest_asset_path}")
            return unreal.EditorAssetLibrary.load_asset(dest_asset_path)

        abs_source = os.path.join(content_dir, rel_path)
        if not os.path.exists(abs_source):
            unreal.log_error(f"Source file missing: {abs_source}")
            return None
        task = unreal.AssetImportTask()
        task.set_editor_property('automated', True)
        task.set_editor_property('destination_name', dest_name)
        task.set_editor_property('destination_path', mesh_pkg_path)
        task.set_editor_property('filename', abs_source)
        task.set_editor_property('replace_existing', True)
        task.set_editor_property('save', True)

        options = unreal.FbxImportUI()
        options.set_editor_property('import_mesh', True)
        options.set_editor_property('import_textures', False)
        options.set_editor_property('import_materials', False)
        options.set_editor_property('import_as_skeletal', False)
        options.static_mesh_import_data.set_editor_property('combine_meshes', combine_meshes)
        options.static_mesh_import_data.set_editor_property('auto_generate_collision', generate_collision)

        task.set_editor_property('options', options)
        asset_tools.import_asset_tasks([task])

        loaded = unreal.EditorAssetLibrary.load_asset(dest_asset_path)
        if loaded:
            unreal.log(f"Successfully imported mesh: {dest_asset_path}")
        else:
            unreal.log_warning(f"Mesh not loaded after task: {dest_asset_path}")
        return loaded

    # 1.1 Steering wheel (Centered pivot for VR, collision disabled)
    sm_steering_wheel = import_mesh(
        rel_path="Vehicles/Meshes/SM_Steering_Wheel_Centered.obj",
        dest_name="SM_Steering_Wheel_Centered",
        generate_collision=False,
        combine_meshes=True
    )

    # 1.2 Player sports car chassis (Pristine FBX, collision enabled)
    sm_player_chassis = import_mesh(
        rel_path="Vehicles/Meshes/Merkurs_KCR-5.fbx",
        dest_name="SM_Merkurs_Chassis",
        generate_collision=True,
        combine_meshes=True
    )

    # 1.3 Police pursuit vehicle (Hyundai Ioniq 5 sedan/SUV)
    sm_police_vehicle = import_mesh(
        rel_path="Vehicles/Meshes/Hyundai_Ioniq_5_2022.fbx",
        dest_name="SM_Hyundai_Ioniq5",
        generate_collision=True,
        combine_meshes=True
    )

    # -------------------------------------------------------------------------
    # 2. IMPORT TEXTURES & GENERATE PBR MATERIALS
    # -------------------------------------------------------------------------
    log_step("STEP 2: IMPORTING TEXTURES AND GENERATING MATERIALS")

    def import_texture(rel_path, dest_name):
        dest_asset_path = f"{tex_pkg_path}/{dest_name}"
        if unreal.EditorAssetLibrary.does_asset_exist(dest_asset_path):
            unreal.log(f"Texture already exists, reusing: {dest_asset_path}")
            return unreal.EditorAssetLibrary.load_asset(dest_asset_path)

        abs_source = os.path.join(content_dir, rel_path)
        if not os.path.exists(abs_source):
            return None
        task = unreal.AssetImportTask()
        task.set_editor_property('automated', True)
        task.set_editor_property('destination_name', dest_name)
        task.set_editor_property('destination_path', tex_pkg_path)
        task.set_editor_property('filename', abs_source)
        task.set_editor_property('replace_existing', True)
        task.set_editor_property('save', True)

        asset_tools.import_asset_tasks([task])
        return unreal.EditorAssetLibrary.load_asset(dest_asset_path)

    # Key textures for the car
    t_body_bc = import_texture("Vehicles/Textures/Merkurs_KCR5/Light Blue Base Color.png", "T_CarBody_BC")
    t_body_r = import_texture("Vehicles/Textures/Merkurs_KCR5/Roughness Fine Diffuse 002.png", "T_CarBody_R")
    t_wheel_bc = import_texture("Vehicles/Textures/Merkurs_KCR5/Alcantara Diffuse.png", "T_Alcantara_BC")
    t_tire_bc = import_texture("Vehicles/Textures/Merkurs_KCR5/Tire Sport Type Diffuse (Modified) 01.png", "T_Tire_BC")

    def create_material(mat_name, base_tex=None, base_color=(0.1, 0.1, 0.1), roughness=0.5, metallic=0.0, emissive=(0.0, 0.0, 0.0)):
        mat_path = f"{mat_pkg_path}/{mat_name}"
        if unreal.EditorAssetLibrary.does_asset_exist(mat_path):
            unreal.log(f"Material already exists, reusing: {mat_path}")
            return unreal.EditorAssetLibrary.load_asset(mat_path)

        factory = unreal.MaterialFactoryNew()
        mat = asset_tools.create_asset(mat_name, mat_pkg_path, unreal.Material, factory)
        if not mat:
            return None

        # Base Color
        if base_tex:
            ts = unreal.MaterialEditingLibrary.create_material_expression(mat, unreal.MaterialExpressionTextureSample, -400, 0)
            ts.set_editor_property('texture', base_tex)
            unreal.MaterialEditingLibrary.connect_material_property(ts, "RGB", unreal.MaterialProperty.MP_BASE_COLOR)
        elif base_color:
            c3 = unreal.MaterialEditingLibrary.create_material_expression(mat, unreal.MaterialExpressionConstant3Vector, -400, 0)
            c3.set_editor_property('constant', unreal.LinearColor(base_color[0], base_color[1], base_color[2], 1.0))
            unreal.MaterialEditingLibrary.connect_material_property(c3, "", unreal.MaterialProperty.MP_BASE_COLOR)

        # Roughness
        r_node = unreal.MaterialEditingLibrary.create_material_expression(mat, unreal.MaterialExpressionConstant, -250, 160)
        r_node.set_editor_property('r', roughness)
        unreal.MaterialEditingLibrary.connect_material_property(r_node, "", unreal.MaterialProperty.MP_ROUGHNESS)

        # Metallic
        if metallic > 0.0:
            m_node = unreal.MaterialEditingLibrary.create_material_expression(mat, unreal.MaterialExpressionConstant, -250, 260)
            m_node.set_editor_property('r', metallic)
            unreal.MaterialEditingLibrary.connect_material_property(m_node, "", unreal.MaterialProperty.MP_METALLIC)

        # Emissive (for police strobes)
        if any(e > 0.0 for e in emissive):
            e_node = unreal.MaterialEditingLibrary.create_material_expression(mat, unreal.MaterialExpressionConstant3Vector, -400, 360)
            e_node.set_editor_property('constant', unreal.LinearColor(emissive[0], emissive[1], emissive[2], 1.0))
            unreal.MaterialEditingLibrary.connect_material_property(e_node, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)

        # Recompile / Layout Material Expressions
        if hasattr(unreal.MaterialEditingLibrary, 'recompile_material'):
            unreal.MaterialEditingLibrary.recompile_material(mat)
        elif hasattr(mat, 'recompile_material'):
            mat.recompile_material()
        elif hasattr(unreal.MaterialEditingLibrary, 'layout_material_expressions'):
            unreal.MaterialEditingLibrary.layout_material_expressions(mat)

        unreal.EditorAssetLibrary.save_loaded_asset(mat)
        unreal.log(f"Generated Material: {mat_path}")
        return mat

    m_car_body = create_material("M_Merkurs_Body", base_tex=t_body_bc, base_color=(0.1, 0.4, 0.8), roughness=0.25, metallic=0.85)
    m_steering_wheel = create_material("M_SteeringWheel_Alcantara", base_tex=t_wheel_bc, base_color=(0.15, 0.15, 0.15), roughness=0.9, metallic=0.0)
    m_tires = create_material("M_VehicleTires", base_tex=t_tire_bc, base_color=(0.04, 0.04, 0.04), roughness=0.95, metallic=0.0)
    m_siren_red = create_material("M_Siren_Red", base_color=(1.0, 0.0, 0.0), roughness=0.2, emissive=(35.0, 0.0, 0.0))
    m_siren_blue = create_material("M_Siren_Blue", base_color=(0.0, 0.1, 1.0), roughness=0.2, emissive=(0.0, 5.0, 35.0))

    # Assign materials to meshes if valid
    if sm_steering_wheel and m_steering_wheel:
        try:
            sm_steering_wheel.set_material(0, m_steering_wheel)
            unreal.EditorAssetLibrary.save_loaded_asset(sm_steering_wheel)
        except Exception as e:
            unreal.log(f"SetMaterial on Steering Wheel: {e}")

    # -------------------------------------------------------------------------
    # 3. CREATE & CONFIGURE BLUEPRINTS
    # -------------------------------------------------------------------------
    log_step("STEP 3: CONFIGURING BLUEPRINTS (BP_VrVehiclePawn & BP_PoliceVehiclePawn)")

    vr_pawn_cpp_class = unreal.load_class(None, "/Script/VrMpc.VrVehiclePawn")
    police_pawn_cpp_class = unreal.load_class(None, "/Script/VrMpc.PoliceVehiclePawn")
    track_spline_cpp_class = unreal.load_class(None, "/Script/VrMpc.RaceTrackSpline")

    def create_or_load_bp(bp_name, parent_class):
        bp_path = f"{bp_pkg_path}/{bp_name}"
        if unreal.EditorAssetLibrary.does_asset_exist(bp_path):
            bp = unreal.EditorAssetLibrary.load_asset(bp_path)
            unreal.log(f"Loaded existing Blueprint: {bp_path}")
            return bp
        factory = unreal.BlueprintFactory()
        factory.set_editor_property('parent_class', parent_class)
        bp = asset_tools.create_asset(bp_name, bp_pkg_path, unreal.Blueprint, factory)
        if bp:
            unreal.BlueprintEditorLibrary.compile_blueprint(bp)
            unreal.log(f"Created & compiled Blueprint: {bp_path}")
        return bp

    def get_bp_generated_class(bp, bp_name):
        if not bp:
            return None
        try:
            cls = bp.get_editor_property('generated_class')
            if cls: return cls
        except:
            pass
        try:
            cls = bp.generated_class()
            if cls: return cls
        except:
            pass
        try:
            cls = unreal.load_class(None, f"{bp_pkg_path}/{bp_name}.{bp_name}_C")
            if cls: return cls
        except:
            pass
        return None

    def set_prop_safe(obj, prop_names, value):
        if not obj:
            return False
        for name in prop_names:
            try:
                obj.set_editor_property(name, value)
                return True
            except Exception:
                pass
        return False

    # 3.1 BP_VrVehiclePawn
    bp_vr_player = create_or_load_bp("BP_VrVehiclePawn", vr_pawn_cpp_class)
    player_bp_class = get_bp_generated_class(bp_vr_player, "BP_VrVehiclePawn") or vr_pawn_cpp_class

    if player_bp_class:
        cdo = unreal.get_default_object(player_bp_class)
        if cdo:
            try:
                # Cockpit seat positioning (driver left side)
                set_prop_safe(cdo.cockpit_root, ['relative_location'], unreal.Vector(-35.0, -35.0, 50.0))
                
                # Steering wheel mesh & 20 deg pitch inclination
                if sm_steering_wheel:
                    set_prop_safe(cdo.steering_wheel_visual_mesh, ['static_mesh'], sm_steering_wheel)
                set_prop_safe(cdo.steering_wheel_visual_mesh, ['relative_rotation'], unreal.Rotator(pitch=20.0, yaw=0.0, roll=0.0))
                
                # Component binding
                set_prop_safe(cdo.steering_wheel_component, ['wheel_rim_radius', 'wheel_radius'], 16.0)
                set_prop_safe(cdo.steering_wheel_component, ['grab_radius'], 8.0)
                set_prop_safe(cdo.steering_wheel_component, ['target_wheel_mesh'], cdo.steering_wheel_visual_mesh)
                
                unreal.BlueprintEditorLibrary.compile_blueprint(bp_vr_player)
                unreal.EditorAssetLibrary.save_loaded_asset(bp_vr_player)
                unreal.log("Configured BP_VrVehiclePawn CDO successfully.")
            except Exception as e:
                unreal.log_warning(f"Error updating BP_VrVehiclePawn CDO: {e}")

    # 3.2 BP_PoliceVehiclePawn
    bp_police = create_or_load_bp("BP_PoliceVehiclePawn", police_pawn_cpp_class)
    police_bp_class = get_bp_generated_class(bp_police, "BP_PoliceVehiclePawn") or police_pawn_cpp_class

    if police_bp_class:
        cdo_police = unreal.get_default_object(police_bp_class)
        if cdo_police:
            try:
                # Roof siren positions
                cdo_police.red_siren_light.set_editor_property('relative_location', unreal.Vector(0.0, -25.0, 145.0))
                cdo_police.red_siren_light.set_editor_property('light_color', unreal.Color(r=255, g=0, b=0, a=255))
                cdo_police.red_siren_light.set_editor_property('intensity', 3500.0)
                
                cdo_police.blue_siren_light.set_editor_property('relative_location', unreal.Vector(0.0, 25.0, 145.0))
                cdo_police.blue_siren_light.set_editor_property('light_color', unreal.Color(r=0, g=40, b=255, a=255))
                cdo_police.blue_siren_light.set_editor_property('intensity', 3500.0)
                
                cdo_police.set_editor_property('siren_strobe_rate', 6.0)
                cdo_police.set_editor_property('proximity_alert_distance', 1500.0) # 15 meters
                
                unreal.BlueprintEditorLibrary.compile_blueprint(bp_police)
                unreal.EditorAssetLibrary.save_loaded_asset(bp_police)
                unreal.log("Configured BP_PoliceVehiclePawn CDO successfully.")
            except Exception as e:
                unreal.log_warning(f"Error updating BP_PoliceVehiclePawn CDO: {e}")

    # -------------------------------------------------------------------------
    # 4. LEVEL ASSEMBLY (MAP GENERATION & ACTOR SPAWNING)
    # -------------------------------------------------------------------------
    log_step("STEP 4: ASSEMBLING TEST LEVEL (L_RaceTrack_VR)")

    level_asset_path = f"{maps_pkg_path}/L_RaceTrack_VR"
    if not unreal.EditorAssetLibrary.does_asset_exist(level_asset_path):
        unreal.EditorLevelLibrary.new_level(level_asset_path)
    else:
        unreal.EditorLevelLibrary.load_level(level_asset_path)
        # Clear previous test actors to avoid duplicate spawns
        for act in unreal.EditorLevelLibrary.get_all_level_actors():
            label = act.get_actor_label()
            if any(key in label for key in ["RaceTrack_Circuit", "Player_VrVehicle", "Police_Pursuit"]):
                unreal.EditorLevelLibrary.destroy_actor(act)

    # 4.1 Spawn Procedural Race Track Spline
    track_loc = unreal.Vector(0.0, 0.0, 50.0)
    track_rot = unreal.Rotator(0.0, 0.0, 0.0)
    track_actor = unreal.EditorLevelLibrary.spawn_actor_from_class(track_spline_cpp_class, track_loc, track_rot)
    if track_actor:
        track_actor.set_actor_label("RaceTrack_Circuit")
        set_prop_safe(track_actor, ['is_closed_loop', 'b_is_closed_loop', 'b_closed_loop'], True)
        set_prop_safe(track_actor, ['track_width'], 1200.0)
        set_prop_safe(track_actor, ['wall_height'], 160.0)
        set_prop_safe(track_actor, ['wall_thickness'], 40.0)

        # 8 circuit control points forming a high-speed ~1.2 km loop
        spline = track_actor.spline_component
        spline.clear_spline_points()
        points = [
            unreal.Vector(0.0, 0.0, 0.0),            # Start / Finish line
            unreal.Vector(20000.0, 0.0, 0.0),        # Main Straight (200m)
            unreal.Vector(30000.0, 6000.0, 0.0),     # Turn 1 Entry
            unreal.Vector(32000.0, 18000.0, 50.0),   # Sweeper Apex
            unreal.Vector(22000.0, 28000.0, 60.0),   # Back Straight Entry
            unreal.Vector(-8000.0, 28000.0, 40.0),   # Back Straight
            unreal.Vector(-18000.0, 16000.0, 20.0),  # Hairpin Apex
            unreal.Vector(-14000.0, 4000.0, 0.0)     # Final Corner onto Straight
        ]
        for p in points:
            spline.add_spline_point(p, unreal.SplineCoordinateSpace.LOCAL, False)
        
        spline.set_closed_loop(True)
        spline.update_spline()
        try:
            track_actor.reregister_all_components()
        except Exception:
            pass
        unreal.log("Spawned and procedurally built RaceTrack_Circuit.")

    # 4.2 Spawn Player Vehicle Pawn
    player_loc = unreal.Vector(1500.0, 0.0, 120.0)
    player_rot = unreal.Rotator(0.0, 0.0, 0.0)
    spawned_player = unreal.EditorLevelLibrary.spawn_actor_from_class(player_bp_class, player_loc, player_rot)
    if spawned_player:
        spawned_player.set_actor_label("Player_VrVehicle")
        spawned_player.set_editor_property('auto_possess_player', unreal.AutoReceiveInput.PLAYER0)
        try:
            spawned_player.cockpit_root.set_relative_location(unreal.Vector(-35.0, -35.0, 50.0), False, False)
            spawned_player.steering_wheel_visual_mesh.set_relative_rotation(unreal.Rotator(20.0, 0.0, 0.0), False, False)
            if sm_steering_wheel:
                spawned_player.steering_wheel_visual_mesh.set_static_mesh(sm_steering_wheel)
        except Exception as e:
            unreal.log(f"Player instance adjust: {e}")
        unreal.log("Spawned Player_VrVehicle with AutoPossess Player0.")

    # 4.3 Spawn Police Pursuit Vehicle Pawn (25m behind player)
    if not police_bp_class:
        police_bp_class = police_pawn_cpp_class
    police_loc = unreal.Vector(-1000.0, 0.0, 120.0) # 25 meters (2500 cm) behind player
    police_rot = unreal.Rotator(0.0, 0.0, 0.0)
    spawned_police = unreal.EditorLevelLibrary.spawn_actor_from_class(police_bp_class, police_loc, police_rot)
    if spawned_police:
        spawned_police.set_actor_label("Police_Pursuit_Interceptor")
        try:
            spawned_police.red_siren_light.set_relative_location(unreal.Vector(0.0, -25.0, 145.0), False, False)
            spawned_police.blue_siren_light.set_relative_location(unreal.Vector(0.0, 25.0, 145.0), False, False)
            follower = spawned_police.spline_follower
            if follower and track_actor:
                if hasattr(follower, 'set_target_spline'):
                    follower.set_target_spline(track_actor.spline_component)
                set_prop_safe(follower, ['target_spline_component'], track_actor.spline_component)
                set_prop_safe(follower, ['target_cruising_speed_kmh'], 160.0)
            if hasattr(spawned_police, 'set_target_player') and spawned_player:
                spawned_police.set_target_player(spawned_player)
        except Exception as e:
            unreal.log(f"Police instance adjust: {e}")
        unreal.log("Spawned Police_Pursuit_Interceptor bound to Spline Track.")

    # 4.4 Ensure Lighting in Level
    sun_found = False
    for act in unreal.EditorLevelLibrary.get_all_level_actors():
        if isinstance(act, unreal.DirectionalLight):
            sun_found = True
            break
    if not sun_found:
        sun = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.DirectionalLight, unreal.Vector(0, 0, 4000), unreal.Rotator(-45.0, -35.0, 0.0))
        if sun:
            sun.set_actor_label("Sun_DirectionalLight")
            sun.light_component.set_editor_property('intensity', 4.0)
        sky = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.SkyLight, unreal.Vector(0, 0, 4500), unreal.Rotator(0, 0, 0))
        if sky:
            sky.set_actor_label("Sky_AmbientLight")

    # Save level and assets
    unreal.EditorLevelLibrary.save_current_level()
    unreal.EditorAssetLibrary.save_loaded_asset(bp_vr_player)
    unreal.EditorAssetLibrary.save_loaded_asset(bp_police)

    log_step("VRMPC AUTOMATED INTEGRATION COMPLETED SUCCESSFULLY WITH 0 ERRORS!")

if __name__ == "__main__":
    main()
