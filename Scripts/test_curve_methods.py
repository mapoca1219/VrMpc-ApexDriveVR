import unreal

with open("/Users/marcopolo/Documents/Unreal Projects/VrMpc/Scripts/test_output.txt", "w") as f:
    f.write(f"RichCurveKey:\n{dir(unreal.RichCurveKey)}\n\n")
    f.write(f"FloatCurve:\n{dir(unreal.FloatCurve)}\n\n")
    f.write(f"RichCurve:\n{dir(unreal.RichCurve)}\n\n")
