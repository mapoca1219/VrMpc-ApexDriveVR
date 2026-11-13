# Apex Drive VR: Cockpit Pursuit
### *Meta VR Start Developer Competition 2026 Submission*

[![Unreal Engine 5](https://img.shields.io/badge/Unreal_Engine-5.8-0E1128?logo=unrealengine&logoColor=white)](https://www.unrealengine.com/)
[![Target Platform](https://img.shields.io/badge/Platform-Meta_Quest_2_%2F_3_%2F_Pro-0668E1?logo=meta&logoColor=white)](https://developer.oculus.com/)
[![Language](https://img.shields.io/badge/Language-C%2B%2B20-00599C?logo=c%2B%2B&logoColor=white)](https://isocpp.org/)
[![Physics](https://img.shields.io/badge/Physics-Chaos_Wheeled_Vehicle-FF6F00)](https://docs.unrealengine.com/5.0/en-US/chaos-physics-overview/)
[![Status](https://img.shields.io/badge/Build-Passing-brightgreen)]()

An immersive, hands-first Virtual Reality arcade racing simulator built natively in **Unreal Engine 5** for the **Meta VR Start Developer Competition 2026**. Experience full 6DOF physical cockpit presence, battle 3 human-like AI supercar rivals, and survive aggressive police interceptor units that actively block lanes, sideswipe you, and execute high-speed PIT maneuvers.

---

## 🏎️ Key Features

### 1. Hands-First 6DOF VR Cockpit
* **Direct Interactive Steering:** Grab and rotate the sports steering wheel directly with Meta Quest Touch motion controllers (1:1 angular correspondence) without expensive sim-rig peripherals.
* **Physical Cockpit Controls:** Press the center-console push-button for **Nitro Boost**, actuate the sequential gear shift lever, and view live diegetic OLED telemetry.
* **Anti-Cinetosis Ergonomics:** Cockpit windshield framing, A-pillars, and dashboard geometry provide stable visual anchor references, preventing VR motion sickness at speeds exceeding 215 km/h.

### 2. Relentless Police Interceptor AI
* **Parked Ambush Mechanics:** Patrol units stay silent on road shoulders until speeding racers approach within detection range.
* **Tactical Lane Blocking:** Police actively mirror overtaking lines, cutting across to defend the lane and tapping brakes to challenge overtakes.
* **Combat Sideswiping & PIT Maneuvers:** Rushing alongside triggers hard lateral rams into the player's chassis. Releasing police triggers high-speed drafting up to 215 km/h with rear-quarter PIT retaliation.

### 3. Procedural Circuit & Rival Drivers
* **Spline-Based Procedural Track:** Closed-loop circuit with elevation changes, banking, dynamic guardrail physics, and multi-lane road geometry.
* **Dynamic AI Racing Lines:** 3 distinct computer-controlled supercars with organic driving personalities:
  * **Cyan Rival (Apex Hunter):** Cuts inside corners tightly and accelerates early out of turns.
  * **Green Rival (Momentum Sweeper):** Takes wide outside lines to maximize speed carry.
  * **Purple Rival (Aggressive Slalom):** High-aggression center slaloming and overtaking.
* **Proactive Collision Avoidance:** Rivals identify blocking vehicles up to 25 meters ahead and proactively execute smooth lane changes.

### 4. 3-Lap Race Progression & Spatial Audio
* **Complete Lap System:** Automatic finish line detection (`VUELTA: 1 / 3` up to 3 laps), dynamic race ranking (`P1` to `P7`), and checkered flag finish sequence.
* **Refined Engine Acoustic Design:** Low-frequency supercar rumble modulated between 0.68x–1.20x pitch, eliminating high-RPM screeching and ear fatigue during extended VR sessions.
* **Positional 3D Sirens:** Doppler-effect emergency sirens culled and distance-attenuated.

---

## 🎮 Controls

| Action | VR Meta Quest Controller | Desktop / PIE Fallback |
| :--- | :--- | :--- |
| **Accelerate** | Right Trigger (Grip to Drive) | `W` or `Up Arrow` |
| **Brake / Reverse** | Left Trigger | `S` or `Down Arrow` |
| **Steer Left / Right** | Grab Steering Wheel (Motion) | `A` / `D` or `Left` / `Right` |
| **Nitro Boost (100%)** | Press Console Nitro Button | `SpaceBar` or `N` |
| **Cycle Camera View** | Cockpit / Chase / Hood Button | `C` |
| **Restart Race Grid** | Menu Button | `R` |

---

## 📁 Architecture Overview

```
Source/VrMpc/
├── VrVehiclePawn.h/.cpp           # Player & AI supercar controller, 6DOF cockpit, 3-lap logic, telemetry
├── PoliceVehiclePawn.h/.cpp       # Interceptor AI, ambush states, lane blocking, PIT ramming, sirens
├── RaceTrackSpline.h/.cpp         # Procedural closed-loop 3D spline circuit, road generation & collision
├── RaceTrackFollowerComponent.*   # Waypoint & spline navigation for autonomous vehicles
├── VirtualSteeringWheelComponent.*# Hands-first VR angular interaction & haptic feedback binding
├── CarAIAgentComponent.h/.cpp     # Copilot tactical tactical advice & radar dispatch
└── VrMpc.Build.cs                 # Engine module rules (ChaosVehicles, HeadMountedDisplay, AudioMixer)
```

---

## 🚀 Getting Started

### Prerequisites
* **Unreal Engine 5.6+** (Developed and tested with UE 5.8)
* **Xcode 16+** (for macOS Apple Silicon) or **Visual Studio 2022** (Windows)
* **Meta Quest Developer Hub (MQDH)** & Meta XR Plugin

### Building the Project
1. Clone this repository:
   ```bash
   git clone https://github.com/mapoca1219/VrMpc-ApexDriveVR.git
   cd VrMpc-ApexDriveVR
   ```
2. Generate project files:
   * Right-click `VrMpc.uproject` -> *Generate Xcode / Visual Studio Project Files*.
3. Open `VrMpc.xcworkspace` (or `.sln`) and build the `VrMpcEditor` target in **Development** configuration.
4. Launch Unreal Editor and open map `Content/Maps/L_RaceTrack_VR.umap`.
5. Click **Play** (or select **VR Preview** with Quest Link / Air Link connected).

---

## 🏆 Meta VR Start Developer Competition 2026
* **Track:** Gaming
* **Division:** New Experience
* **Submission Date:** November 2026
* **Developer:** Marco Polo (mapoca1219)

---

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
