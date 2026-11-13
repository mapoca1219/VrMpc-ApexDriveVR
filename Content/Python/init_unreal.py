# Content/Python/init_unreal.py
# Startup script for Unreal Engine 5.8
import unreal
import sys
import os

project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
scripts_dir = os.path.join(project_dir, "Scripts")
content_python_dir = os.path.dirname(__file__)

for p in [project_dir, scripts_dir, content_python_dir]:
    if p not in sys.path:
        sys.path.insert(0, p)

unreal.log(">>> [VrMpc] Python environment initialized safely. 'import fix; fix.fix()' is ready.")
