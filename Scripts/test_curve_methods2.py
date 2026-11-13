import unreal

with open("/Users/marcopolo/Documents/Unreal Projects/VrMpc/Scripts/test_output.txt", "w") as f:
    curve = unreal.EditorAssetLibrary.load_asset("/Game/Blueprints/Curve_Torque")
    f.write(f"Curve: {curve}\n")
    # Check all methods on curve
    for attr in dir(curve):
        f.write(f"  {attr}\n")

