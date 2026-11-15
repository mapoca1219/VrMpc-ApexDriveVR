#!/usr/bin/env python3
"""
Apex Drive VR: Cockpit Pursuit - Smooth Master Competition Video Producer
Removes all paused/frozen frames from the raw recording (at 42.3s and 64.9s)
to create a 100% fluid, continuous, zero-stutter 60fps masterpiece.
"""

import os
import sys
import wave
import struct
import subprocess
import time

FFMPEG = "/opt/homebrew/bin/ffmpeg"
if not os.path.exists(FFMPEG):
    FFMPEG = "ffmpeg"

INPUT_VIDEO = "VrMpc.mov"
OUTPUT_VIDEO = "ApexDriveVR_Winning_Trailer_Smooth.mp4"
TOTAL_SMOOTH_DURATION = 149.2  # 139.2s race + 10s outro

print("==================================================================")
print(">>> GENERATING APEX DRIVE VR SMOOTH MASTER TRAILER (ZERO PAUSES)")
print("==================================================================")

# Step 1: Re-assemble narration audio with adjusted timestamps
sample_rate = 48000
channels = 2
total_duration_sec = 152
total_samples = total_duration_sec * sample_rate
buffer = bytearray(total_samples * channels * 2)

clips_schedule = [
    ('scratch/narration_01_intro.wav', 0.8),
    ('scratch/narration_02_nitro.wav', 12.0),
    ('scratch/narration_03_cockpit.wav', 30.0),
    ('scratch/narration_04_rivals.wav', 47.0),
    ('scratch/narration_05_police.wav', 68.0),
    ('scratch/narration_06_circuit.wav', 101.0),
    ('scratch/narration_07_victory.wav', 130.5),
    ('scratch/narration_08_outro.wav', 139.5)
]

for clip_path, start_time in clips_schedule:
    if not os.path.exists(clip_path):
        continue
    with wave.open(clip_path, 'rb') as wf:
        n_frames = wf.getnframes()
        raw_bytes = wf.readframes(n_frames)
        start_sample = int(start_time * sample_rate)
        for i in range(n_frames):
            dest_sample = start_sample + i
            if dest_sample >= total_samples:
                break
            for c in range(2):
                src_val = struct.unpack_from('<h', raw_bytes, (i * 2 + c) * 2)[0]
                dest_offset = (dest_sample * 2 + c) * 2
                dest_val = struct.unpack_from('<h', buffer, dest_offset)[0]
                mixed = max(-32768, min(32767, dest_val + src_val))
                struct.pack_into('<h', buffer, dest_offset, mixed)

SMOOTH_NARRATION = "scratch/narration_smooth_timeline.wav"
with wave.open(SMOOTH_NARRATION, 'wb') as out_wf:
    out_wf.setnchannels(channels)
    out_wf.setsampwidth(2)
    out_wf.setframerate(sample_rate)
    out_wf.writeframes(buffer)

print(f">>> Reassembled smooth narration: {SMOOTH_NARRATION}")

# Filter complex: cut freezes, concat, format, overlay, mix
filter_complex = (
    # Cut out Pause 1 (42.27s - 47.73s) and Pause 2 (64.87s - 68.27s)
    "[0:v]trim=start=0:end=42.267,setpts=PTS-STARTPTS[v1];"
    "[0:a]atrim=start=0:end=42.267,asetpts=PTS-STARTPTS[a1];"
    
    "[0:v]trim=start=47.733:end=64.867,setpts=PTS-STARTPTS[v2];"
    "[0:a]atrim=start=47.733:end=64.867,asetpts=PTS-STARTPTS[a2];"
    
    "[0:v]trim=start=68.267:end=148.0,setpts=PTS-STARTPTS[v3];"
    "[0:a]atrim=start=68.267:end=148.0,asetpts=PTS-STARTPTS[a3];"
    
    "[v1][a1][v2][a2][v3][a3]concat=n=3:v=1:a=1[v_raw][a_raw];"
    
    # Scale, pad to 1080p, 60fps, 10s outro freeze at end
    "[v_raw]scale=1920:886,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:black,fps=60,"
    "tpad=stop_mode=clone:stop_duration=10.0,"
    
    # Persistent Top Header Bar (6.5s to 139.2s)
    "drawbox=y=0:color=black@0.92:width=iw:height=96:t=fill:enable='between(t,6.5,139.2)',"
    "drawtext=text='APEX DRIVE VR \\: COCKPIT PURSUIT':fontcolor=0x40C4FF:fontsize=30:x=60:y=34:enable='between(t,6.5,139.2)',"
    "drawtext=text='META VR START DEVELOPER COMPETITION 2026':fontcolor=0xFFD54F:fontsize=22:x=w-text_w-60:y=38:enable='between(t,6.5,139.2)',"
    
    # Persistent Bottom Background Bar (6.5s to 139.2s)
    "drawbox=y=h-96:color=black@0.92:width=iw:height=96:t=fill:enable='between(t,6.5,139.2)',"
    
    # 1. Intro Card (0.5s - 6.5s)
    "drawbox=x=0:y=0:w=iw:h=ih:color=black@0.85:t=fill:enable='between(t,0.5,6.5)',"
    "drawbox=x=160:y=180:w=iw-320:h=ih-360:color=0x00E5FF@0.7:t=2:enable='between(t,0.5,6.5)',"
    "drawtext=text='APEX DRIVE VR \\: COCKPIT PURSUIT':fontcolor=0x00E5FF:fontsize=56:x=(w-text_w)/2:y=260:enable='between(t,0.5,6.5)',"
    "drawtext=text='HIGH-SPEED COMBAT RACING  •  HANDS-FIRST VR PRESENCE':fontcolor=white:fontsize=26:x=(w-text_w)/2:y=345:enable='between(t,0.5,6.5)',"
    "drawbox=x=300:y=405:w=iw-600:h=2:color=white@0.3:t=fill:enable='between(t,0.5,6.5)',"
    "drawtext=text='META VR START DEVELOPER COMPETITION 2026':fontcolor=0xFFD54F:fontsize=32:x=(w-text_w)/2:y=440:enable='between(t,0.5,6.5)',"
    "drawtext=text='Built with Unreal Engine 5.8  •  Meta XR SDK  •  Chaos Physics':fontcolor=0xB0BEC5:fontsize=24:x=(w-text_w)/2:y=500:enable='between(t,0.5,6.5)',"
    "drawtext=text='FULL 5-LAP CHAMPIONSHIP PLAYTHROUGH':fontcolor=0x69F0AE:fontsize=24:x=(w-text_w)/2:y=560:enable='between(t,0.5,6.5)',"
    
    # 2. Lower-Third 1: Nitro & Speed Barrier (10.0s - 26.0s)
    "drawtext=text='01 // DUAL PLASMA NITRO THRUSTERS • 280 KM/H SPEED BARRIER':fontcolor=0x40C4FF:fontsize=28:x=60:y=h-78:enable='between(t,10.0,26.0)',"
    "drawtext=text='Real cornering inertia, active dynamic chassis roll, and zero-latency driver authority':fontcolor=white:fontsize=20:x=60:y=h-42:enable='between(t,10.0,26.0)',"
    
    # 3. Lower-Third 2: 6DOF Cockpit Presence (27.0s - 45.0s)
    "drawtext=text='02 // 6DOF HANDS-FIRST COCKPIT PRESENCE & DIEGETIC OLED HUD':fontcolor=0xFFD54F:fontsize=28:x=60:y=h-78:enable='between(t,27.0,45.0)',"
    "drawtext=text='Touch steering wheel control, tactical AI copilot, and real-time battery telemetry':fontcolor=white:fontsize=20:x=60:y=h-42:enable='between(t,27.0,45.0)',"
    
    # 4. Lower-Third 3: AI Rivals & Drafting (46.0s - 66.0s)
    "drawtext=text='03 // ORGANIC AI RACING PERSONALITIES & SLIPSTREAM DRAFTING':fontcolor=0x69F0AE:fontsize=28:x=60:y=h-78:enable='between(t,46.0,66.0)',"
    "drawtext=text='Apex specialists, momentum sweepers, and aggressive center slalom overtakers':fontcolor=white:fontsize=20:x=60:y=h-42:enable='between(t,46.0,66.0)',"
    
    # 5. Lower-Third 4: Police Interceptors Combat (67.0s - 96.0s)
    "drawtext=text='04 // HIGH-SPEED COMBAT POLICE INTERCEPTORS':fontcolor=0xFF5252:fontsize=28:x=60:y=h-78:enable='between(t,67.0,96.0)',"
    "drawtext=text='Tactical lane-blocking defense, PIT collision maneuvers, and 3D spatial emergency sirens':fontcolor=white:fontsize=20:x=60:y=h-42:enable='between(t,67.0,96.0)',"
    
    # 6. Lower-Third 5: 5-Lap Championship Circuit (97.0s - 127.0s)
    "drawtext=text='05 // 5-LAP URBAN CHAMPIONSHIP CIRCUIT & METROPOLIS':fontcolor=0x00E5FF:fontsize=28:x=60:y=h-78:enable='between(t,97.0,127.0)',"
    "drawtext=text='Procedural multi-tier architecture, windowed towers, and asphalt tire adhesion':fontcolor=white:fontsize=20:x=60:y=h-42:enable='between(t,97.0,127.0)',"
    
    # 7. Lower-Third 6: 1st Place Victory (128.0s - 139.2s)
    "drawtext=text='06 // CHECKERED FLAG VICTORY • 1ST PLACE CHAMPION':fontcolor=0xFFD54F:fontsize=28:x=60:y=h-78:enable='between(t,128.0,139.2)',"
    "drawtext=text='Seated VR comfort rating • Rock-solid 60+ FPS performance on Meta Quest':fontcolor=white:fontsize=20:x=60:y=h-42:enable='between(t,128.0,139.2)',"
    
    # 8. Outro Card (139.2s - 149.2s)
    "drawbox=x=0:y=0:w=iw:h=ih:color=black@0.92:t=fill:enable='gte(t,139.2)',"
    "drawbox=x=120:y=80:w=iw-240:h=ih-160:color=0x00E5FF@0.7:t=2:enable='gte(t,139.2)',"
    "drawtext=text='APEX DRIVE VR \\: COCKPIT PURSUIT':fontcolor=0x00E5FF:fontsize=52:x=(w-text_w)/2:y=130:enable='gte(t,139.2)',"
    "drawtext=text='[ OFFICIAL ENTRY ] META VR START DEVELOPER COMPETITION 2026':fontcolor=0xFFD54F:fontsize=26:x=(w-text_w)/2:y=205:enable='gte(t,139.2)',"
    "drawbox=x=250:y=255:w=iw-500:h=2:color=white@0.3:t=fill:enable='gte(t,139.2)',"
    "drawbox=x=220:y=285:w=iw-440:h=120:color=white@0.08:t=fill:enable='gte(t,139.2)',"
    "drawtext=text='META QUEST RELEASE CHANNEL (APP LAB INVITE URL)':fontcolor=0x80D8FF:fontsize=22:x=(w-text_w)/2:y=310:enable='gte(t,139.2)',"
    "drawtext=text='https\\://www.meta.com/s/83yZYIoFL':fontcolor=white:fontsize=32:x=(w-text_w)/2:y=350:enable='gte(t,139.2)',"
    "drawbox=x=220:y=435:w=iw-440:h=120:color=white@0.08:t=fill:enable='gte(t,139.2)',"
    "drawtext=text='OPEN SOURCE C++ REPOSITORY & ARCHITECTURE':fontcolor=0xB9F6CA:fontsize=22:x=(w-text_w)/2:y=460:enable='gte(t,139.2)',"
    "drawtext=text='github.com/mapoca1219/VrMpc-ApexDriveVR':fontcolor=white:fontsize=32:x=(w-text_w)/2:y=500:enable='gte(t,139.2)',"
    "drawtext=text='Unreal Engine 5.8  •  Meta XR SDK  •  Chaos Physics  •  Native C++':fontcolor=0xB0BEC5:fontsize=24:x=(w-text_w)/2:y=620:enable='gte(t,139.2)',"
    "drawtext=text='6DOF Virtual Steering  •  Diegetic OLED HUD  •  Dynamic AI & Police Combat':fontcolor=0xB0BEC5:fontsize=22:x=(w-text_w)/2:y=665:enable='gte(t,139.2)',"
    "drawtext=text='THANK YOU JUDGES & META EVALUATION TEAM!':fontcolor=0xFFD54F:fontsize=30:x=(w-text_w)/2:y=760:enable='gte(t,139.2)'"
    "[v_out];"
    
    # 3-Track Master Audio Mixing:
    # Game Audio @ 65%, Narrator @ 145%, Synthwave @ 70%
    "[a_raw]volume=0.65[a_game];"
    "[1:a]volume=1.45[a_narrator];"
    "[2:a]volume=0.70[a_music];"
    "[a_game][a_narrator][a_music]amix=inputs=3:duration=first:dropout_transition=2[a_out]"
)

cmd = [
    FFMPEG,
    "-y",
    "-i", INPUT_VIDEO,
    "-i", SMOOTH_NARRATION,
    "-i", "scratch/synthwave_racing_soundtrack.wav",
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
    "-t", str(TOTAL_SMOOTH_DURATION),
    OUTPUT_VIDEO
]

print(">>> Starting FFmpeg render...")
t_start = time.time()
res = subprocess.run(cmd, capture_output=True, text=True)
t_elapsed = time.time() - t_start

if res.returncode == 0:
    file_size_mb = os.path.getsize(OUTPUT_VIDEO) / (1024 * 1024)
    print(f">>> [SUCCESS] Smooth video rendered in {t_elapsed:.1f}s at: {OUTPUT_VIDEO}")
    print(f">>> File size: {file_size_mb:.2f} MB")
else:
    print(f">>> [ERROR] FFmpeg failed:\n{res.stderr[-1200:]}")
    sys.exit(1)
