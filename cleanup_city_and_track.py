import unreal
import math

def run():
    print("=== LIMPIANDO MAPA L_RaceTrack_VR Y PISTA DE CARRERAS ===", flush=True)

    # 1. Cargar nivel L_RaceTrack_VR
    print("Cargando nivel /Game/Maps/L_RaceTrack_VR...", flush=True)
    unreal.EditorLevelLibrary.load_level("/Game/Maps/L_RaceTrack_VR")
    all_actors = unreal.EditorLevelLibrary.get_all_level_actors()
    print(f"Total actores en nivel: {len(all_actors)}", flush=True)

    # 2. Encontrar actor de pista
    track_actor = None
    for a in all_actors:
        label = a.get_actor_label()
        cls_name = a.get_class().get_name()
        if "RaceTrack" in label or "RaceTrack" in cls_name:
            track_actor = a
            break

    if not track_actor:
        print("ERROR: Pista RaceTrack no encontrada!", flush=True)
        return

    spline = track_actor.get_component_by_class(unreal.SplineComponent)
    spline_len = spline.get_spline_length() if spline else 50000.0
    print(f"Pista encontrada: {track_actor.get_actor_label()} | Longitud: {spline_len:.0f} cm", flush=True)

    # 3. Eliminar TODOS los edificios intrusivos que tapan la carretera y las curvas
    existing_buildings = [a for a in all_actors if "City_Building" in a.get_actor_label() or "Building" in a.get_actor_label() or "Skyline_Tower" in a.get_actor_label()]
    print(f"Eliminando {len(existing_buildings)} edificios cercanos para despejar totalmente la pista...", flush=True)
    for b in existing_buildings:
        unreal.EditorLevelLibrary.destroy_actor(b)

    # 4. Cargar materiales profesionales limpios y descansados para la vista
    asphalt_mat = unreal.EditorAssetLibrary.load_asset("/Game/LevelPrototyping/Materials/M_City_Highway_Asphalt")
    barrier_mat = unreal.EditorAssetLibrary.load_asset("/Game/LevelPrototyping/Materials/MI_PrototypeGrid_TopDark")
    cube_mesh = unreal.EditorAssetLibrary.load_asset("/Engine/BasicShapes/Cube")

    # 5. Generar un skyline lejano en el horizonte (> 180 a 280 metros de distancia)
    # Ningún edificio toca ni se acerca a la carretera; están en el horizonte como una ciudad de fondo real
    num_towers = 14
    for i in range(num_towers):
        frac = i / float(num_towers)
        dist = (frac * spline_len) % spline_len
        side = 1.0 if (i % 2 == 0) else -1.0
        # Distancia al horizonte: 180 metros a 260 metros lejos de la pista
        lateral_offset = side * (18000.0 + (i % 4) * 2000.0)

        loc = spline.get_location_at_distance_along_spline(dist, unreal.SplineCoordinateSpace.WORLD)
        direction = spline.get_direction_at_distance_along_spline(dist, unreal.SplineCoordinateSpace.WORLD)
        right = spline.get_right_vector_at_distance_along_spline(dist, unreal.SplineCoordinateSpace.WORLD)

        # Alturas y proporciones de torres estilizadas de fondo
        h_scale = 32.0 + (i % 4) * 10.0
        w_scale = 14.0 + (i % 3) * 4.0
        d_scale = 14.0 + (i % 3) * 4.0

        spawn_pos = loc + (right * lateral_offset) + unreal.Vector(0, 0, (h_scale * 50.0) - 200.0)
        yaw = math.degrees(math.atan2(direction.y, direction.x))
        spawn_rot = unreal.Rotator(pitch=0.0, yaw=yaw, roll=0.0)

        tower = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.StaticMeshActor, spawn_pos, spawn_rot)
        if tower:
            tower.set_actor_label(f"Skyline_Tower_{i:02d}")
            tower.set_actor_scale3d(unreal.Vector(w_scale, d_scale, h_scale))
            smc = tower.get_component_by_class(unreal.StaticMeshComponent)
            if smc and cube_mesh:
                smc.set_static_mesh(cube_mesh)
                if barrier_mat:
                    smc.set_material(0, barrier_mat)

    # 6. Configurar la pista: asfalto negro nítido y guardarraíles oscuros GT3 (sin destellos cegadores)
    track_actor.set_editor_property("TrackWidth", 1400.0)
    track_actor.set_editor_property("WallHeight", 70.0)
    track_actor.set_editor_property("WallThickness", 35.0)
    track_actor.set_editor_property("bGenerateGuardrails", True)
    if asphalt_mat:
        track_actor.set_editor_property("RoadMaterial", asphalt_mat)
    if barrier_mat:
        track_actor.set_editor_property("WallMaterial", barrier_mat)

    # Actualizar todos los SplineMeshComponent existentes para que tomen el asfalto y muro oscuro de inmediato
    spline_meshes = track_actor.get_components_by_class(unreal.SplineMeshComponent)
    for sm in spline_meshes:
        current_mat = sm.get_material(0)
        if current_mat:
            mat_name = current_mat.get_name()
            if "Neon" in mat_name or "Wall" in mat_name:
                if barrier_mat:
                    sm.set_material(0, barrier_mat)
            elif "Asphalt" in mat_name or "Road" in mat_name:
                if asphalt_mat:
                    sm.set_material(0, asphalt_mat)

    # 7. Guardar nivel
    unreal.EditorLevelLibrary.save_current_level()
    print("=== ¡NIVEL L_RaceTrack_VR TOTALMENTE DESPEJADO Y GUARDADO CON ÉXITO! ===", flush=True)

if __name__ == "__main__":
    run()
