import unreal
import math

def run():
    print("=== LIMPIANDO PISTA Y CREANDO SKYLINE DISTANTE ELEGANTE ===", flush=True)
    unreal.EditorLevelLibrary.load_level("/Game/Maps/L_RaceTrack_VR")
    all_actors = unreal.EditorLevelLibrary.get_all_level_actors()

    # 1. Encontrar pista
    track_actor = None
    for a in all_actors:
        if "RaceTrack" in a.get_actor_label() or "RaceTrack" in a.get_class().get_name():
            track_actor = a
            break

    spline = track_actor.get_component_by_class(unreal.SplineComponent) if track_actor else None
    if not spline:
        print("ERROR: Spline no encontrado!", flush=True)
        return

    spline_len = spline.get_spline_length()
    print(f"Longitud de la pista: {spline_len:.0f} cm", flush=True)

    # 2. Eliminar o reubicar todos los edificios que estorban la pista
    buildings = [a for a in all_actors if "City_" in a.get_actor_label() or "Building" in a.get_actor_label() or "Skyscraper" in a.get_actor_label()]
    print(f"Encontrados {len(buildings)} edificios existentes.", flush=True)

    # Materiales elegantes y oscuros para el horizonte lejano (NO resplandor de colores planos)
    mat_dark_tower = unreal.EditorAssetLibrary.load_asset("/Game/LevelPrototyping/Materials/M_City_Tower_Modern")
    mat_amber_tower = unreal.EditorAssetLibrary.load_asset("/Game/LevelPrototyping/Materials/M_City_Tower_Amber")
    asphalt_mat = unreal.EditorAssetLibrary.load_asset("/Game/LevelPrototyping/Materials/M_City_Highway_Asphalt")
    guardrail_mat = unreal.EditorAssetLibrary.load_asset("/Game/LevelPrototyping/Materials/M_City_NeonCyan")

    # Reconfigurar los edificios para que sean un SKYLINE LEJANO (a 120 - 220 metros de la pista)
    # y que NUNCA tapen la carretera ni se vean como pantallas gigantes
    for i, b in enumerate(buildings):
        if i >= 20:
            # Eliminar los excedentes para dejar la pista totalmente despejada y veloz
            unreal.EditorLevelLibrary.destroy_actor(b)
            continue

        # Ubicar solo 20 rascacielos lejanos en el horizonte
        frac = i / 20.0
        dist = frac * spline_len
        side = 1.0 if (i % 2 == 0) else -1.0
        # Distancia lejana: 140 metros a 220 metros de la pista
        lateral = side * (14000.0 + (i % 5) * 1800.0)

        d = dist % spline_len
        loc = spline.get_location_at_distance_along_spline(d, unreal.SplineCoordinateSpace.WORLD)
        direction = spline.get_direction_at_distance_along_spline(d, unreal.SplineCoordinateSpace.WORLD)
        right = spline.get_right_vector_at_distance_along_spline(d, unreal.SplineCoordinateSpace.WORLD)

        # Altura del edificio en el horizonte
        h_scale = 50.0 + (i % 6) * 15.0
        w_scale = 22.0 + (i % 4) * 6.0
        d_scale = 22.0 + (i % 3) * 6.0

        target_pos = loc + (right * lateral) + unreal.Vector(0, 0, (h_scale * 50.0) - 200.0)
        yaw = math.degrees(math.atan2(direction.y, direction.x))
        target_rot = unreal.Rotator(pitch=0.0, yaw=yaw, roll=0.0)

        b.set_actor_location_and_rotation(target_pos, target_rot, False, False)
        b.set_actor_scale3d(unreal.Vector(w_scale, d_scale, h_scale))

        comp = b.get_component_by_class(unreal.StaticMeshComponent)
        if comp:
            chosen_mat = mat_dark_tower if (i % 2 == 0) else mat_amber_tower
            if chosen_mat:
                comp.set_material(0, chosen_mat)

    # 3. Configurar la pista para que esté limpia y con asfalto real
    if track_actor:
        track_actor.set_editor_property("TrackWidth", 1400.0)
        track_actor.set_editor_property("WallHeight", 65.0)
        track_actor.set_editor_property("WallThickness", 30.0)
        track_actor.set_editor_property("bGenerateGuardrails", True)
        if asphalt_mat:
            track_actor.set_editor_property("RoadMaterial", asphalt_mat)
        if guardrail_mat:
            track_actor.set_editor_property("WallMaterial", guardrail_mat)
        track_actor.rerun_construction_scripts()

    # 4. Guardar nivel
    unreal.EditorLevelLibrary.save_current_level()
    print("=== PISTA DESPEJADA Y NIVEL GUARDADO CON ÉXITO ===", flush=True)

if __name__ == "__main__":
    run()
