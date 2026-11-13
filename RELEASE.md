# Release Notes: Apex Drive VR v1.0.0
### *Meta VR Start Developer Competition 2026 Edition*

**Release Tag:** `v1.0.0-competition`  
**Date:** November 13, 2026  
**Target:** Meta Quest 2 / 3 / Pro (Unreal Engine 5)

---

## 🌟 What's New in v1.0.0

### 🏎️ Vehicle Physics & Cockpit Presence
* **6DOF Hands-First Interactive Steering:** Direct touch interaction with the sports steering wheel using Meta Quest Touch controllers (`UVirtualSteeringWheelComponent`).
* **Diegetic OLED Dashboard:** Integrated real-time digital speedometer (`KM/H`), gear indicator (`GEAR: 1-6`), dynamic lap counter (`VTA 1/3`), and AI tactical Copilot alerts.
* **Interactive Nitro Boost:** Functional push-button and motion controller triggers for high-thrust rocket acceleration with haptic feedback.
* **Refined Acoustic Engine Profile:** Deep, resonant supercar exhaust hum (0.68x–1.20x pitch clamp) designed for extended VR comfort without auditory fatigue.

### 🚨 Police Interceptor Pursuit AI
* **Parked Ambush Patrols:** Patrol units positioned along track shoulders waiting in low-power stealth mode until triggered by approaching racers within 65m.
* **Tactical Lane-Blocking Defense:** When racers attempt to overtake from behind, police dynamically mirror the target's lateral lane and tap brakes to contest passage.
* **High-Speed PIT Maneuvers & Sideswipes:** Lateral wheel-to-wheel ramming when alongside and aggressive 215 km/h pursuit drafting with rear-quarter bumper contact upon overtake.
* **Spatialized Siren Audio:** Distance-culled, 3D-attenuated Doppler emergency sirens.

### 🏁 Circuit Racing & Rival AI
* **Dynamic 3-Lap Race Loop:** Full lap crossing detection on procedural 3D spline circuit with checkered-flag victory celebration and race reset shortcut (`[R]`).
* **Organic AI Rival Personalities:**
  * Rival 1 (Cyan): Apex specialist clipping inside corners.
  * Rival 2 (Green): High-speed outside sweeper carrying maximum momentum.
  * Rival 3 (Purple): Aggressive center slalom overtaker.
* **Non-Sticky Lateral Collision Dynamics:** Physics-based repulsion and momentum transfer on vehicle contact without vehicle lockups or track de-syncing.

---

## 📦 Verified Artifacts
* `Source/VrMpc/`: Native C++ source code compatible with UE 5.8 and Clang 21.
* `Content/Maps/L_RaceTrack_VR.umap`: Master VR circuit level with urban skyline, guardrails, and lighting.
* `VrMpc.uproject`: Configured for Meta XR plugin, OpenXR, and Chaos Vehicle movement.
