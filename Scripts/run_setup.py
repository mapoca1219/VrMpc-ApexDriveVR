import unreal

print("[RUN_SETUP] Cargando version fresca de deploy_grand_prix_vr.py desde disco...")
with open('/Users/marcopolo/Documents/Unreal Projects/VrMpc/Scripts/deploy_grand_prix_vr.py', 'r') as f:
    code = f.read()

exec(code, globals())
setup()

