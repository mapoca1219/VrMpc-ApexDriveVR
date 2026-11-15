#!/usr/bin/env python3
"""
Apex Drive VR: Cockpit Pursuit - Master Competition Video Producer (with Music Soundtrack)
Meta VR Start Developer Competition 2026 Edition

Produces the definitive winning hackathon showcase video:
- 1080p 60fps cinematic widescreen master (156.5 seconds)
- Professional English narrator voiceover synchronized with race events
- 128 BPM Cyberpunk Synthwave electronic racing soundtrack
- Rebalanced original gameplay engine audio + tire skids
- Intro card & Outro submission card with Meta Release Channel URL & GitHub repo
- Dynamic technical lower-third banners explaining all 6 core technical pillars
"""

import os
import sys
import subprocess
import time

FFMPEG = "/opt/homebrew/bin/ffmpeg"
if not os.path.exists(FFMPEG):
    FFMPEG = "ffmpeg"

INPUT_VIDEO = "VrMpcfinal.mov"
NARRATION_AUDIO = "scratch/narration_full_timeline.wav"
MUSIC_AUDIO = "scratch/synthwave_racing_soundtrack.wav"
OUTPUT_VIDEO = "ApexDriveVR_Winning_Trailer.mp4"

print("==================================================================")
print(">>> PRODUCING APEX DRIVE VR MASTER COMPETITION VIDEO WITH MUSIC")
print(f">>> Input Video:     {INPUT_VIDEO}")
print(f">>> Narration Audio: {NARRATION_AUDIO}")
print(f">>> Music Audio:     {MUSIC_AUDIO}")
print(f">>> Output Master:   {OUTPUT_VIDEO}")
print("==================================================================")

# Construct complex filtergraph
filter_complex = (
    # Video pipeline: trim at 148.0s (end of race with Victory banner), freeze winning frame for 10s outro
    "[0:v]trim=start=0:end=148.0,setpts=PTS-STARTPTS,"
    "scale=1920:886,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:black,fps=60,"
    "tpad=stop_mode=clone:stop_duration=10.0,"
    
    # Persistent Top Header Bar (6.5s to 148.0s)
    "drawbox=y=0:color=black@0.92:width=iw:height=96:t=fill:enable='between(t,6.5,148.0)',"
    "drawtext=text='APEX DRIVE VR \\: COCKPIT PURSUIT':fontcolor=0x40C4FF:fontsize=30:x=60:y=34:enable='between(t,6.5,148.0)',"
    "drawtext=text='META VR START DEVELOPER COMPETITION 2026':fontcolor=0xFFD54F:fontsize=22:x=w-text_w-60:y=38:enable='between(t,6.5,148.0)',"
    
    # Persistent Bottom Background Bar (6.5s to 148.0s)
    "drawbox=y=h-96:color=black@0.92:width=iw:height=96:t=fill:enable='between(t,6.5,148.0)',"
    
    # 1. Intro Card (0.5s - 6.5s)
    "drawbox=x=0:y=0:w=iw:h=ih:color=black@0.85:t=fill:enable='between(t,0.5,6.5)',"
    "drawbox=x=160:y=180:w=iw-320:h=ih-360:color=0x00E5FF@0.7:t=2:enable='between(t,0.5,6.5)',"
    "drawtext=text='APEX DRIVE VR \\: COCKPIT PURSUIT':fontcolor=0x00E5FF:fontsize=56:x=(w-text_w)/2:y=260:enable='between(t,0.5,6.5)',"
    "drawtext=text='HIGH-SPEED COMBAT RACING  •  HANDS-FIRST VR PRESENCE':fontcolor=white:fontsize=26:x=(w-text_w)/2:y=345:enable='between(t,0.5,6.5)',"
    "drawbox=x=300:y=405:w=iw-600:h=2:color=white@0.3:t=fill:enable='between(t,0.5,6.5)',"
    "drawtext=text='META VR START DEVELOPER COMPETITION 2026':fontcolor=0xFFD54F:fontsize=32:x=(w-text_w)/2:y=440:enable='between(t,0.5,6.5)',"
    "drawtext=text='Built with Unreal Engine 5.8  •  Meta XR SDK  •  Chaos Physics':fontcolor=0xB0BEC5:fontsize=24:x=(w-text_w)/2:y=500:enable='between(t,0.5,6.5)',"
    "drawtext=text='FULL 5-LAP CHAMPIONSHIP PLAYTHROUGH':fontcolor=0x69F0AE:fontsize=24:x=(w-text_w)/2:y=560:enable='between(t,0.5,6.5)',"
    
    # 2. Lower-Third 1: Nitro & Speed Barrier (10.0s - 28.0s)
    "drawtext=text='01 // DUAL PLASMA NITRO THRUSTERS • 280 KM/H SPEED BARRIER':fontcolor=0x40C4FF:fontsize=28:x=60:y=h-78:enable='between(t,10.0,28.0)',"
    "drawtext=text='Real cornering inertia, active dynamic chassis roll, and zero-latency driver authority':fontcolor=white:fontsize=20:x=60:y=h-42:enable='between(t,10.0,28.0)',"
    
    # 3. Lower-Third 2: 6DOF Cockpit Presence (29.0s - 50.0s)
    "drawtext=text='02 // 6DOF HANDS-FIRST COCKPIT PRESENCE & DIEGETIC OLED HUD':fontcolor=0xFFD54F:fontsize=28:x=60:y=h-78:enable='between(t,29.0,50.0)',"
    "drawtext=text='Touch steering wheel control, tactical AI copilot, and real-time battery telemetry':fontcolor=white:fontsize=20:x=60:y=h-42:enable='between(t,29.0,50.0)',"
    
    # 4. Lower-Third 3: AI Rivals & Drafting (51.0s - 72.0s)
    "drawtext=text='03 // ORGANIC AI RACING PERSONALITIES & SLIPSTREAM DRAFTING':fontcolor=0x69F0AE:fontsize=28:x=60:y=h-78:enable='between(t,51.0,72.0)',"
    "drawtext=text='Apex specialists, momentum sweepers, and aggressive center slalom overtakers':fontcolor=white:fontsize=20:x=60:y=h-42:enable='between(t,51.0,72.0)',"
    
    # 5. Lower-Third 4: Police Interceptors Combat (73.0s - 105.0s)
    "drawtext=text='04 // HIGH-SPEED COMBAT POLICE INTERCEPTORS':fontcolor=0xFF5252:fontsize=28:x=60:y=h-78:enable='between(t,73.0,105.0)',"
    "drawtext=text='Tactical lane-blocking defense, PIT collision maneuvers, and 3D spatial emergency sirens':fontcolor=white:fontsize=20:x=60:y=h-42:enable='between(t,73.0,105.0)',"
    
    # 6. Lower-Third 5: 5-Lap Championship Circuit (106.0s - 136.0s)
    "drawtext=text='05 // 5-LAP URBAN CHAMPIONSHIP CIRCUIT & METROPOLIS':fontcolor=0x00E5FF:fontsize=28:x=60:y=h-78:enable='between(t,106.0,136.0)',"
    "drawtext=text='Procedural multi-tier architecture, windowed towers, and asphalt tire adhesion':fontcolor=white:fontsize=20:x=60:y=h-42:enable='between(t,106.0,136.0)',"
    
    # 7. Lower-Third 6: 1st Place Victory (137.0s - 148.0s)
    "drawtext=text='06 // CHECKERED FLAG VICTORY • 1ST PLACE CHAMPION':fontcolor=0xFFD54F:fontsize=28:x=60:y=h-78:enable='between(t,137.0,148.0)',"
    "drawtext=text='Seated VR comfort rating • Rock-solid 60+ FPS performance on Meta Quest':fontcolor=white:fontsize=20:x=60:y=h-42:enable='between(t,137.0,148.0)',"
    
    # 8. Outro Card (148.0s - 158.0s)
    "drawbox=x=0:y=0:w=iw:h=ih:color=black@0.92:t=fill:enable='gte(t,148.0)',"
    "drawbox=x=120:y=80:w=iw-240:h=ih-160:color=0x00E5FF@0.7:t=2:enable='gte(t,148.0)',"
    "drawtext=text='APEX DRIVE VR \\: COCKPIT PURSUIT':fontcolor=0x00E5FF:fontsize=52:x=(w-text_w)/2:y=130:enable='gte(t,148.0)',"
    "drawtext=text='[ OFFICIAL ENTRY ] META VR START DEVELOPER COMPETITION 2026':fontcolor=0xFFD54F:fontsize=26:x=(w-text_w)/2:y=205:enable='gte(t,148.0)',"
    "drawbox=x=250:y=255:w=iw-500:h=2:color=white@0.3:t=fill:enable='gte(t,148.0)',"
    "drawbox=x=220:y=285:w=iw-440:h=120:color=white@0.08:t=fill:enable='gte(t,148.0)',"
    "drawtext=text='META QUEST RELEASE CHANNEL (APP LAB INVITE URL)':fontcolor=0x80D8FF:fontsize=22:x=(w-text_w)/2:y=310:enable='gte(t,148.0)',"
    "drawtext=text='https\\://www.meta.com/s/83yZYIoFL':fontcolor=white:fontsize=32:x=(w-text_w)/2:y=350:enable='gte(t,148.0)',"
    "drawbox=x=220:y=435:w=iw-440:h=120:color=white@0.08:t=fill:enable='gte(t,148.0)',"
    "drawtext=text='OPEN SOURCE C++ REPOSITORY & ARCHITECTURE':fontcolor=0xB9F6CA:fontsize=22:x=(w-text_w)/2:y=460:enable='gte(t,148.0)',"
    "drawtext=text='github.com/mapoca1219/VrMpc-ApexDriveVR':fontcolor=white:fontsize=32:x=(w-text_w)/2:y=500:enable='gte(t,148.0)',"
    "drawtext=text='Unreal Engine 5.8  •  Meta XR SDK  •  Chaos Physics  •  Native C++':fontcolor=0xB0BEC5:fontsize=24:x=(w-text_w)/2:y=620:enable='gte(t,148.0)',"
    "drawtext=text='6DOF Virtual Steering  •  Diegetic OLED HUD  •  Dynamic AI & Police Combat':fontcolor=0xB0BEC5:fontsize=22:x=(w-text_w)/2:y=665:enable='gte(t,148.0)',"
    "drawtext=text='THANK YOU JUDGES & META EVALUATION TEAM!':fontcolor=0xFFD54F:fontsize=30:x=(w-text_w)/2:y=760:enable='gte(t,148.0)'"
    "[v_out];"
    
    # 3-Track Master Audio Mixing:
    # 0: Game Audio (Engine, Tires, Sirens) @ 65%
    # 1: Narrator Voice @ 145%
    # 2: 128 BPM Synthwave Music @ 70%
    "[0:a]volume=0.65[a_game];"
    "[1:a]volume=1.45[a_narrator];"
    "[2:a]volume=0.70[a_music];"
    "[a_game][a_narrator][a_music]amix=inputs=3:duration=first:dropout_transition=2[a_out]"
)

cmd = [
    FFMPEG,
    "-y",
    "-i", INPUT_VIDEO,
    "-i", NARRATION_AUDIO,
    "-i", MUSIC_AUDIO,
    "-filter_complex", filter_complex,
    "-map", "[v_out]",
    "-map", "[a_out]",
    "-c:v", "libx264",
    "-preset", "slow",
    "-crf", "18",
    "-pix_fmt", "yuv420p",
    "-movflags", "+faststart",
    "-c:a", "aac",
    "-b:a", "320k",
    "-ar", "48000",
    "-t", "158.0",
    OUTPUT_VIDEO
]

print(">>> Launching FFmpeg render process with 3-track audio mix...")
t_start = time.time()
res = subprocess.run(cmd, capture_output=True, text=True)
t_elapsed = time.time() - t_start

if res.returncode == 0:
    print(f">>> [SUCCESS] Master trailer rendered in {t_elapsed:.1f}s at: {OUTPUT_VIDEO}")
    file_size_mb = os.path.getsize(OUTPUT_VIDEO) / (1024 * 1024)
    print(f">>> File size: {file_size_mb:.2f} MB")
else:
    print(f">>> [ERROR] FFmpeg failed:\n{res.stderr[-1200:]}")
    sys.exit(1)
