#!/usr/bin/env python3
import os
import unreal

def log(msg):
    unreal.log(f"[AUDIO_IMPORT] >>> {msg} <<<")

def import_soundtrack():
    content_dir = unreal.SystemLibrary.get_project_content_directory()
    source_wav = os.path.join(content_dir, "Audio", "Synthwave_Soundtrack.wav")
    dest_path = "/Game/Audio"
    dest_name = "SW_Synthwave_Music"
    full_pkg = f"{dest_path}/{dest_name}"
    
    log(f"Importing soundtrack from {source_wav} to {full_pkg}...")
    
    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
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
        sound.set_editor_property('looping', True)
        unreal.EditorAssetLibrary.save_loaded_asset(sound)
        log(f"SUCCESS: Soundtrack imported as USoundWave with Looping=True at {full_pkg}")
    else:
        unreal.log_error(f"FAILED to load imported sound at {full_pkg}")

if __name__ == "__main__":
    import_soundtrack()
