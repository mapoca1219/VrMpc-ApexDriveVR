import unreal

def run():
    level_path = "/Game/Maps/L_RaceTrack_VR"
    unreal.EditorLevelLibrary.load_level(level_path)
    world = unreal.EditorLevelLibrary.get_editor_world()
    actors = unreal.EditorLevelLibrary.get_all_level_actors()

    print(f">>> Found {len(actors)} actors in {level_path}")

    # 1. Asegurar Sol (DirectionalLight)
    sun = None
    for a in actors:
        if a.get_class().get_name() == "DirectionalLight":
            sun = a
            break
    if not sun:
        sun = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.DirectionalLight, unreal.Vector(0, 0, 1500))
        sun.set_actor_label("Sun_Daylight")
        print(">>> [LIGHTING] Spawneado DirectionalLight Sun_Daylight.")

    if sun:
        sun.set_actor_rotation(unreal.Rotator(pitch=-38.0, yaw=55.0, roll=0.0), False)
        for c in sun.get_components_by_class(unreal.DirectionalLightComponent):
            c.set_editor_property("intensity", 8.0)
            c.set_editor_property("light_color", unreal.Color(255, 245, 230, 255))
            c.set_editor_property("cast_shadows", True)
            try:
                c.set_editor_property("atmosphere_sun_light", True)
            except:
                pass

    # 2. Asegurar Luz del Cielo (SkyLight)
    skylight = None
    for a in actors:
        if a.get_class().get_name() == "SkyLight":
            skylight = a
            break
    if not skylight:
        skylight = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.SkyLight, unreal.Vector(0, 0, 1500))
        skylight.set_actor_label("SkyLight_Ambient")
        print(">>> [LIGHTING] Spawneado SkyLight SkyLight_Ambient.")

    if skylight:
        for c in skylight.get_components_by_class(unreal.SkyLightComponent):
            c.set_editor_property("intensity", 1.8)
            try:
                c.set_editor_property("real_time_capture", True)
            except:
                pass

    # 3. Asegurar Atmósfera Celeste (SkyAtmosphere)
    skyatmo = None
    for a in actors:
        if a.get_class().get_name() == "SkyAtmosphere":
            skyatmo = a
            break
    if not skyatmo:
        skyatmo = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.SkyAtmosphere, unreal.Vector(0, 0, 0))
        skyatmo.set_actor_label("SkyAtmosphere_Day")
        print(">>> [LIGHTING] Spawneado SkyAtmosphere_Day (Cielo azul radiante).")

    # 4. Asegurar Nubes Volumétricas (VolumetricCloud)
    clouds = None
    for a in actors:
        if a.get_class().get_name() == "VolumetricCloud":
            clouds = a
            break
    if not clouds:
        try:
            clouds = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.VolumetricCloud, unreal.Vector(0, 0, 0))
            clouds.set_actor_label("Clouds_Volumetric")
            print(">>> [LIGHTING] Spawneado VolumetricCloud.")
        except Exception as e:
            print(f">>> [LIGHTING] Aviso VolumetricCloud: {e}")

    # 5. Asegurar Niebla (ExponentialHeightFog)
    fog = None
    for a in actors:
        if a.get_class().get_name() == "ExponentialHeightFog":
            fog = a
            break
    if not fog:
        fog = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.ExponentialHeightFog, unreal.Vector(0, 0, 0))
        fog.set_actor_label("Fog_Horizon")
        print(">>> [LIGHTING] Spawneado ExponentialHeightFog.")

    if fog:
        for c in fog.get_components_by_class(unreal.ExponentialHeightFogComponent):
            try:
                c.set_editor_property("fog_density", 0.0002)
                c.set_editor_property("volumetric_fog", False)
            except:
                pass

    # 6. Guardar Nivel
    unreal.EditorLevelLibrary.save_current_level()
    print(">>> [LIGHTING] Nivel guardado con iluminación diurna completa y cielo azul.")

if __name__ == "__main__":
    run()
