import os
import json
import glob

workspace_dir = "/Users/marcopolo/Documents/Unreal Projects/VrMpc"
vscode_dir = os.path.join(workspace_dir, ".vscode")
sysroot = "/Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX.sdk"
clang_path = "/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/bin/clang++"

# 1. Update response files (.rsp)
for rsp_rel in ["compileCommands_VrMpc/VrMpc.0.rsp", "compileCommands_Default/VrMpc.0.rsp"]:
    rsp_path = os.path.join(vscode_dir, rsp_rel)
    if os.path.exists(rsp_path):
        with open(rsp_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        flags_to_prepend = f'-std=c++20\n-stdlib=libc++\n-isysroot "{sysroot}"\n'
        if "-std=c++20" not in content:
            with open(rsp_path, "w", encoding="utf-8") as f:
                f.write(flags_to_prepend + content)
            print(f"Updated {rsp_path}")

# 2. Update compileCommands_*.json
source_dir = os.path.join(workspace_dir, "Source", "VrMpc")
cpp_files = sorted(glob.glob(os.path.join(source_dir, "*.cpp")))
h_files = sorted(glob.glob(os.path.join(source_dir, "*.h")))

for cc_rel in ["compileCommands_VrMpc.json", "compileCommands_Default.json"]:
    cc_path = os.path.join(vscode_dir, cc_rel)
    rsp_rel = "compileCommands_VrMpc/VrMpc.0.rsp" if "VrMpc" in cc_rel else "compileCommands_Default/VrMpc.0.rsp"
    rsp_abs = os.path.join(vscode_dir, rsp_rel)

    entries = []
    
    # Add CPP files
    for f in cpp_files:
        entries.append({
            "file": f,
            "directory": workspace_dir,
            "arguments": [
                clang_path,
                "-std=c++20",
                "-stdlib=libc++",
                "-arch", "arm64",
                "-isysroot", sysroot,
                "-x", "objective-c++",
                f"@{rsp_abs}",
                f
            ]
        })
        
    # Add Header files
    for h in h_files:
        entries.append({
            "file": h,
            "directory": workspace_dir,
            "arguments": [
                clang_path,
                "-std=c++20",
                "-stdlib=libc++",
                "-arch", "arm64",
                "-isysroot", sysroot,
                "-x", "objective-c++-header",
                f"@{rsp_abs}",
                h
            ]
        })

    with open(cc_path, "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=2)
    print(f"Updated {cc_path} with {len(entries)} entries ({len(cpp_files)} cpp + {len(h_files)} headers)")

# 3. Update c_cpp_properties.json
c_cpp_prop_path = os.path.join(vscode_dir, "c_cpp_properties.json")
prop_data = {
    "configurations": [
        {
            "name": "VrMpcEditor Editor Mac Development (VrMpc)",
            "compilerPath": clang_path,
            "compilerArgs": [
                "-std=c++20",
                "-stdlib=libc++",
                "-arch", "arm64",
                "-isysroot", sysroot,
                "-x", "objective-c++"
            ],
            "macFrameworkPath": [
                f"{sysroot}/System/Library/Frameworks"
            ],
            "cStandard": "c17",
            "cppStandard": "c++20",
            "intelliSenseMode": "macos-clang-arm64",
            "compileCommands": [
                f"{vscode_dir}/compileCommands_VrMpc.json"
            ]
        },
        {
            "name": "Mac",
            "compilerPath": clang_path,
            "compilerArgs": [
                "-std=c++20",
                "-stdlib=libc++",
                "-arch", "arm64",
                "-isysroot", sysroot,
                "-x", "objective-c++"
            ],
            "macFrameworkPath": [
                f"{sysroot}/System/Library/Frameworks"
            ],
            "cStandard": "c17",
            "cppStandard": "c++20",
            "intelliSenseMode": "macos-clang-arm64",
            "compileCommands": [
                f"{vscode_dir}/compileCommands_Default.json"
            ]
        }
    ],
    "version": 4
}
with open(c_cpp_prop_path, "w", encoding="utf-8") as f:
    json.dump(prop_data, f, indent=4)
print(f"Updated {c_cpp_prop_path}")

# 4. Create/Update settings.json
settings_path = os.path.join(vscode_dir, "settings.json")
settings_data = {
    "C_Cpp.default.compileCommands": "${workspaceFolder}/.vscode/compileCommands_VrMpc.json",
    "C_Cpp.default.cppStandard": "c++20",
    "C_Cpp.default.cStandard": "c17",
    "C_Cpp.default.intelliSenseMode": "macos-clang-arm64",
    "C_Cpp.errorSquiggles": "enabled",
    "sonarlint.pathToCompileCommands": "${workspaceFolder}/.vscode/compileCommands_VrMpc.json",
    "files.exclude": {
        "**/.git": True,
        "**/.svn": True,
        "**/.hg": True,
        "**/CVS": True,
        "**/.DS_Store": True,
        "**/Thumbs.db": True,
        "**/DerivedDataCache": True
    }
}
with open(settings_path, "w", encoding="utf-8") as f:
    json.dump(settings_data, f, indent=4)
print(f"Updated {settings_path}")

