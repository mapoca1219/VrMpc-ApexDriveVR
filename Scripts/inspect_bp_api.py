import unreal

def inspect():
    bp_funcs = [x for x in dir(unreal) if 'blueprint' in x.lower() or 'compile' in x.lower()]
    unreal.log_warning(f"Blueprint/Compile functions/classes in unreal: {bp_funcs[:30]}")

if __name__ == "__main__":
    inspect()

