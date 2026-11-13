import os
import json
import glob

workspace_dir = "/Users/marcopolo/Documents/Unreal Projects/VrMpc"
vscode_dir = os.path.join(workspace_dir, ".vscode")
sysroot = "/Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX.sdk"
clang_path = "/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/bin/clang++"
cpp_include = f"{sysroot}/usr/include/c++/v1"
c_include = f"{sysroot}/usr/include"

print(">>> [INTELLISENSE FIX] Configurando rutas C++ de Xcode para VS Code...", flush=True)

# 1. Update response files (.rsp)
for rsp_dir in ["compileCommands_VrMpc", "compileCommands_Default"]:
    rsp_folder = os.path.join(vscode_dir, rsp_dir)
    if os.path.exists(rsp_folder):
        for rsp_file in glob.glob(os.path.join(rsp_folder, "*.rsp")):
            with open(rsp_file, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Remove any duplicate flags if previously added
            lines = content.splitlines()
            filtered_lines = [l for l in lines if not any(x in l for x in ["-stdlib=libc++", "-std=c++20", "MacOSX.sdk/usr/include"])]
            
            header_flags = [
                "-std=c++20",
                "-stdlib=libc++",
                f'-isysroot "{sysroot}"',
                f'-I "{cpp_include}"',
                f'-I "{c_include}"'
            ]
            new_content = "\n".join(header_flags) + "\n" + "\n".join(filtered_lines) + "\n"
            with open(rsp_file, "w", encoding="utf-8") as f:
                f.write(new_content)
            print(f"Updated {rsp_file} with C++ standard library include paths.", flush=True)

# 2. Update compileCommands_*.json
source_dir = os.path.join(workspace_dir, "Source", "VrMpc")
cpp_files = sorted(glob.glob(os.path.join(source_dir, "*.cpp")))
h_files = sorted(glob.glob(os.path.join(source_dir, "*.h")))

for cc_name in ["compileCommands_VrMpc.json", "compileCommands_Default.json"]:
    cc_path = os.path.join(vscode_dir, cc_name)
    rsp_folder = "compileCommands_VrMpc" if "VrMpc" in cc_name else "compileCommands_Default"
    rsp_file = os.path.join(vscode_dir, rsp_folder, "VrMpc.0.rsp")

    entries = []
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
                "-I", cpp_include,
                "-I", c_include,
                f"@{rsp_file}",
                f
            ]
        })
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
                "-I", cpp_include,
                "-I", c_include,
                f"@{rsp_file}",
                h
            ]
        })

    with open(cc_path, "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=2)
    print(f"Updated {cc_path} with {len(entries)} entries.", flush=True)

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
                "-isysroot", sysroot
            ],
            "includePath": [
                "${workspaceFolder}/Source/**",
                cpp_include,
                c_include
            ],
            "macFrameworkPath": [
                f"{sysroot}/System/Library/Frameworks"
            ],
            "cStandard": "c17",
            "cppStandard": "c++20",
            "intelliSenseMode": "macos-clang-arm64",
            "compileCommands": f"{vscode_dir}/compileCommands_VrMpc.json"
        },
        {
            "name": "Mac",
            "compilerPath": clang_path,
            "compilerArgs": [
                "-std=c++20",
                "-stdlib=libc++",
                "-arch", "arm64",
                "-isysroot", sysroot
            ],
            "includePath": [
                "${workspaceFolder}/Source/**",
                cpp_include,
                c_include
            ],
            "macFrameworkPath": [
                f"{sysroot}/System/Library/Frameworks"
            ],
            "cStandard": "c17",
            "cppStandard": "c++20",
            "intelliSenseMode": "macos-clang-arm64",
            "compileCommands": f"{vscode_dir}/compileCommands_Default.json"
        }
    ],
    "version": 4
}

with open(c_cpp_prop_path, "w", encoding="utf-8") as f:
    json.dump(prop_data, f, indent=4)
print(f"Updated {c_cpp_prop_path} successfully.", flush=True)

# 4. Update settings.json
settings_path = os.path.join(vscode_dir, "settings.json")
settings_data = {
    "C_Cpp.default.compileCommands": "${workspaceFolder}/.vscode/compileCommands_VrMpc.json",
    "C_Cpp.default.cppStandard": "c++20",
    "C_Cpp.default.cStandard": "c17",
    "C_Cpp.default.intelliSenseMode": "macos-clang-arm64",
    "C_Cpp.default.includePath": [
        "${workspaceFolder}/Source/**",
        cpp_include,
        c_include
    ],
    "C_Cpp.errorSquiggles": "enabled",
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
print(f"Updated {settings_path} successfully.", flush=True)
print(">>> [INTELLISENSE FIX] ¡Configuración completada con éxito!", flush=True)
