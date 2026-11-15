import unreal

level_path = "/Game/Maps/L_RaceTrack_VR"
unreal.EditorLevelLibrary.load_level(level_path)
all_actors = unreal.EditorLevelLibrary.get_all_level_actors()

police_actors = []
rival_actors = []
player_actors = []

for a in all_actors:
    lbl = a.get_actor_label()
    cls = a.get_class().get_name()
    if "police" in lbl.lower() or "police" in cls.lower():
        police_actors.append((lbl, cls, a.get_actor_location()))
    elif "rival" in lbl.lower():
        rival_actors.append((lbl, cls, a.get_actor_location()))
    elif "player" in lbl.lower() or "vrvehiclepawn" in cls.lower():
        player_actors.append((lbl, cls, a.get_actor_location()))

with open("/Users/marcopolo/Documents/Unreal Projects/VrMpc/Scripts/inspect_vehicles_out.txt", "w") as f:
    f.write("=== POLICE ACTORS ===\n")
    for p in police_actors:
        f.write(f"  {p[0]} ({p[1]}) at {p[2]}\n")
    f.write("\n=== RIVAL ACTORS ===\n")
    for r in rival_actors:
        f.write(f"  {r[0]} ({r[1]}) at {r[2]}\n")
    f.write("\n=== PLAYER ACTORS ===\n")
    for pl in player_actors:
        f.write(f"  {pl[0]} ({pl[1]}) at {pl[2]}\n")
