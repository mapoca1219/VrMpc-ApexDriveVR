import unreal

def inspect_map():
    print("Loading level /Game/Maps/L_RaceTrack_VR...", flush=True)
    unreal.EditorLevelLibrary.load_level("/Game/Maps/L_RaceTrack_VR")
    world = unreal.EditorLevelLibrary.get_editor_world()
    actors = unreal.EditorLevelLibrary.get_all_level_actors()
    print(f"Total actors in level: {len(actors)}", flush=True)

    with open("/Users/marcopolo/Documents/Unreal Projects/VrMpc/map_actors_dump.txt", "w") as f:
        f.write(f"Total actors: {len(actors)}\n")
        for a in actors:
            label = a.get_actor_label()
            cls = a.get_class().get_name()
            loc = a.get_actor_location()
            f.write(f"Actor: {label} [{cls}] at {loc}\n")
            # print static mesh components and materials
            comps = a.get_components_by_class(unreal.StaticMeshComponent)
            for c in comps:
                mesh = c.static_mesh
                mesh_name = mesh.get_name() if mesh else "None"
                num_mats = c.get_num_materials()
                mats = []
                for m_idx in range(num_mats):
                    m = c.get_material(m_idx)
                    m_name = m.get_name() if m else "None"
                    mats.append(f"{m_idx}:{m_name}")
                f.write(f"  Comp: {c.get_name()} | Mesh: {mesh_name} | Mats: {', '.join(mats)}\n")

    print("Map inspection written to map_actors_dump.txt", flush=True)

if __name__ == "__main__":
    inspect_map()
