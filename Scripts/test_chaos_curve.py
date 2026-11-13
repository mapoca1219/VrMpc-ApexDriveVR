import unreal

with open("/Users/marcopolo/Documents/Unreal Projects/VrMpc/Scripts/test_output.txt", "w") as f:
    bp = unreal.EditorAssetLibrary.load_asset("/Game/Blueprints/BP_VrVehiclePawn")
    gen_class = bp.generated_class() if bp else None
    cdo = unreal.get_default_object(gen_class) if gen_class else None
    movement_comp = cdo.get_editor_property("vehicle_movement_component")
    engine_setup = movement_comp.get_editor_property("engine_setup")
    torque_curve = engine_setup.get_editor_property("torque_curve")
    
    # Test import_text
    curve_text = '(EditorCurveData=(Keys=((Time=0.000000,Value=400.000000),(Time=6000.000000,Value=550.000000))),ExternalCurve=CurveFloat\'"/Game/Blueprints/Curve_Torque.Curve_Torque"\')'
    torque_curve.import_text(curve_text)
    f.write(f"Updated torque_curve export_text:\n{torque_curve.export_text()}\n\n")
    
    engine_setup.set_editor_property("torque_curve", torque_curve)
    movement_comp.set_editor_property("engine_setup", engine_setup)
    
    # Check again
    engine_setup_after = movement_comp.get_editor_property("engine_setup")
    f.write(f"After set_editor_property export_text:\n{engine_setup_after.get_editor_property('torque_curve').export_text()}\n\n")
    
    # Save & Compile BP
    unreal.BlueprintEditorLibrary.compile_blueprint(bp)
    unreal.EditorAssetLibrary.save_loaded_asset(bp)
    f.write("Successfully compiled and saved BP_VrVehiclePawn!\n")
