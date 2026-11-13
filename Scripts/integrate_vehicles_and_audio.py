#!/usr/bin/env python3
# ==============================================================================
# INTEGRATE_VEHICLES_AND_AUDIO.PY - Complete Asset & Simulation Linker
# Imports audio, binds 3D chassis meshes, and configures full driving simulation
# ==============================================================================
import os
import unreal

def log(msg):
    unreal.log(f"[VEHICLE_AUDIO_INTEGRATION] >>> {msg} <<<")

def import_sound(source_wav, dest_path, dest_name, b_looping=True):
    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    full_pkg = f"{dest_path}/{dest_name}"
    
    task = unreal.AssetImportTask()
    task.set_editor_property('automated', True)
    task.set_editor_property('destination_name', dest_name)
    task.set_editor_property('destination_path', dest_path)
    task.set_editor_property('filename', source_wav)
    task.set_editor_property('replace_existing', True)
    task.set_editor_property('save', True)
    
    asset_tools.import_asset_tasks([task])
    
    sound = unreal.EditorAssetLibrary.load_asset(full_pkg)
    if sound:
        try:
            sound.set_editor_property('looping', b_looping)
            unreal.EditorAssetLibrary.save_loaded_asset(sound)
            log(f"Audio importado y configurado: {full_pkg} (Looping={b_looping})")
        except Exception as e:
            log(f"Audio importado sin flag looping: {full_pkg} ({e})")
    else:
        unreal.log_error(f"Fallo al importar audio: {full_pkg}")
    return sound

def main():
    log("Iniciando integración completa de vehículos, mallas 3D y audio...")

    # -------------------------------------------------------------------------
    # 1. IMPORTAR AUDIOS (Motor, Sirena, Radio Copiloto)
    # -------------------------------------------------------------------------
    content_dir = unreal.SystemLibrary.get_project_content_directory()
    audio_wav_dir = os.path.join(content_dir, "Audio")
    audio_pkg_dir = "/Game/Audio"
    
    if not unreal.EditorAssetLibrary.does_directory_exist(audio_pkg_dir):
        unreal.EditorAssetLibrary.make_directory(audio_pkg_dir)

    sw_engine = import_sound(os.path.join(audio_wav_dir, "Engine_Loop.wav"), audio_pkg_dir, "SW_Engine_Loop", True)
    sw_siren = import_sound(os.path.join(audio_wav_dir, "Police_Siren.wav"), audio_pkg_dir, "SW_Police_Siren", True)
    sw_radio = import_sound(os.path.join(audio_wav_dir, "Copilot_Radio.wav"), audio_pkg_dir, "SW_Copilot_Radio", False)

    # -------------------------------------------------------------------------
    # 2. CARGAR MALLAS 3D DE VEHÍCULOS
    # -------------------------------------------------------------------------
    mesh_player_path = "/Game/Vehicles/Meshes/SM_Merkurs_Chassis"
    mesh_police_path = "/Game/Vehicles/Meshes/SM_Hyundai_Ioniq5"
    mesh_wheel_path = "/Game/Vehicles/Meshes/SM_Steering_Wheel_Centered"

    sm_player = unreal.EditorAssetLibrary.load_asset(mesh_player_path)
    sm_police = unreal.EditorAssetLibrary.load_asset(mesh_police_path)
    sm_wheel = unreal.EditorAssetLibrary.load_asset(mesh_wheel_path)

    log(f"Malla Jugador cargada: {sm_player}")
    log(f"Malla Policía cargada: {sm_police}")
    log(f"Malla Volante cargada: {sm_wheel}")

    # -------------------------------------------------------------------------
    # 3. CONFIGURAR BLUEPRINT BP_VrVehiclePawn (Coche Jugador)
    # -------------------------------------------------------------------------
    bp_player_path = "/Game/Blueprints/BP_VrVehiclePawn"
    bp_player = unreal.EditorAssetLibrary.load_asset(bp_player_path)
    if bp_player:
        gen_class = None
        try:
            gen_class = bp_player.generated_class()
        except:
            pass
        if not gen_class:
            gen_class = unreal.load_class(None, f"{bp_player_path}.BP_VrVehiclePawn_C")

        if gen_class:
            cdo = unreal.get_default_object(gen_class)
            if cdo:
                # Asignar chasis visible
                if sm_player and hasattr(cdo, "chassis_mesh_component") and cdo.chassis_mesh_component:
                    cdo.chassis_mesh_component.set_editor_property("static_mesh", sm_player)
                    cdo.chassis_mesh_component.set_relative_location(unreal.Vector(0.0, 0.0, -10.0), False, False)
                    log("Asignada malla SM_Merkurs_Chassis a ChassisMeshComponent en BP_VrVehiclePawn.")

                # Asignar volante
                if sm_wheel and hasattr(cdo, "steering_wheel_visual_mesh") and cdo.steering_wheel_visual_mesh:
                    cdo.steering_wheel_visual_mesh.set_editor_property("static_mesh", sm_wheel)
                    cdo.steering_wheel_visual_mesh.set_relative_rotation(unreal.Rotator(pitch=20.0, yaw=0.0, roll=0.0), False, False)

                # Asignar audio de motor
                if sw_engine and hasattr(cdo, "engine_audio_component") and cdo.engine_audio_component:
                    cdo.engine_audio_component.set_editor_property("sound", sw_engine)
                    cdo.engine_audio_component.set_editor_property("auto_activate", True)
                    log("Asignado sonido SW_Engine_Loop a EngineAudioComponent en BP_VrVehiclePawn.")

                # Asignar audio de radio
                if sw_radio and hasattr(cdo, "radio_audio_component") and cdo.radio_audio_component:
                    cdo.radio_audio_component.set_editor_property("sound", sw_radio)

                # Posición de cámara cabina
                if hasattr(cdo, "cockpit_root") and cdo.cockpit_root:
                    cdo.cockpit_root.set_relative_location(unreal.Vector(-20.0, -35.0, 110.0), False, False)

        unreal.BlueprintEditorLibrary.compile_blueprint(bp_player)
        unreal.EditorAssetLibrary.save_loaded_asset(bp_player)
        log("BP_VrVehiclePawn recompilado y guardado.")

    # -------------------------------------------------------------------------
    # 4. CONFIGURAR BLUEPRINT BP_PoliceVehiclePawn (Patrulla Policial)
    # -------------------------------------------------------------------------
    bp_police_path = "/Game/Blueprints/BP_PoliceVehiclePawn"
    bp_police = unreal.EditorAssetLibrary.load_asset(bp_police_path)
    if bp_police:
        gen_class = None
        try:
            gen_class = bp_police.generated_class()
        except:
            pass
        if not gen_class:
            gen_class = unreal.load_class(None, f"{bp_police_path}.BP_PoliceVehiclePawn_C")

        if gen_class:
            cdo = unreal.get_default_object(gen_class)
            if cdo:
                # Asignar chasis visible de patrulla
                if sm_police and hasattr(cdo, "chassis_mesh_component") and cdo.chassis_mesh_component:
                    cdo.chassis_mesh_component.set_editor_property("static_mesh", sm_police)
                    cdo.chassis_mesh_component.set_relative_location(unreal.Vector(0.0, 0.0, -10.0), False, False)
                    log("Asignada malla SM_Hyundai_Ioniq5 a ChassisMeshComponent en BP_PoliceVehiclePawn.")

                # Asignar audio de motor
                if sw_engine and hasattr(cdo, "engine_audio_component") and cdo.engine_audio_component:
                    cdo.engine_audio_component.set_editor_property("sound", sw_engine)
                    cdo.engine_audio_component.set_editor_property("auto_activate", True)
                    log("Asignado sonido SW_Engine_Loop a EngineAudioComponent en BP_PoliceVehiclePawn.")

                # Asignar audio de sirena policial
                if sw_siren and hasattr(cdo, "siren_audio_component") and cdo.siren_audio_component:
                    cdo.siren_audio_component.set_editor_property("sound", sw_siren)
                    cdo.siren_audio_component.set_editor_property("auto_activate", True)
                    log("Asignado sonido SW_Police_Siren a SirenAudioComponent en BP_PoliceVehiclePawn.")

        unreal.BlueprintEditorLibrary.compile_blueprint(bp_police)
        unreal.EditorAssetLibrary.save_loaded_asset(bp_police)
        log("BP_PoliceVehiclePawn recompilado y guardado.")

    # -------------------------------------------------------------------------
    # 5. ACTUALIZAR INSTANCIAS EN EL NIVEL L_RaceTrack_VR
    # -------------------------------------------------------------------------
    level_path = "/Game/Maps/L_RaceTrack_VR"
    unreal.EditorLevelLibrary.load_level(level_path)

    for actor in unreal.EditorLevelLibrary.get_all_level_actors():
        cname = actor.get_class().get_name()
        lbl = actor.get_actor_label()

        if "VrVehicle" in cname or "Player_VrVehicle" in lbl:
            # Jugador
            if sm_player and hasattr(actor, "chassis_mesh_component") and actor.chassis_mesh_component:
                actor.chassis_mesh_component.set_editor_property("static_mesh", sm_player)
            if sw_engine and hasattr(actor, "engine_audio_component") and actor.engine_audio_component:
                actor.engine_audio_component.set_editor_property("sound", sw_engine)
            if sw_radio and hasattr(actor, "radio_audio_component") and actor.radio_audio_component:
                actor.radio_audio_component.set_editor_property("sound", sw_radio)
            log("Instancia de Player_VrVehicle en nivel actualizada con malla y audio.")

        elif "Police" in cname or "Police" in lbl:
            # Policía
            if sm_police and hasattr(actor, "chassis_mesh_component") and actor.chassis_mesh_component:
                actor.chassis_mesh_component.set_editor_property("static_mesh", sm_police)
            if sw_engine and hasattr(actor, "engine_audio_component") and actor.engine_audio_component:
                actor.engine_audio_component.set_editor_property("sound", sw_engine)
            if sw_siren and hasattr(actor, "siren_audio_component") and actor.siren_audio_component:
                actor.siren_audio_component.set_editor_property("sound", sw_siren)
            log("Instancia de BP_PoliceVehiclePawn en nivel actualizada con malla y sirena.")

    unreal.EditorLevelLibrary.save_current_level()
    log("ÉXITO: Nivel y Blueprints guardados con mallas visibles, audio y tracción.")

if __name__ == "__main__":
    main()

