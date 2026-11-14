#!/usr/bin/env python3
"""
Apex Drive VR: Cockpit Pursuit - Automated Competition Trailer Generator
Meta VR Start Developer Competition 2026

Transforms raw screen/headset gameplay recordings into an edited, high-impact trailer
with animated technical lower-thirds, title branding, and audio mastering using FFmpeg.
"""

import os
import sys
import subprocess
import argparse

FFMPEG_BIN = "/opt/homebrew/bin/ffmpeg"
if not os.path.exists(FFMPEG_BIN):
    FFMPEG_BIN = "ffmpeg"

def generate_trailer(input_video, output_video="ApexDriveVR_Competition_Trailer.mp4", duration=75):
    if not os.path.exists(input_video):
        print(f"Error: Input video '{input_video}' not found!")
        print("Please record your gameplay in VR or Unreal Editor and provide the file path.")
        return False

    print("==================================================================")
    print(">>> GENERATING APEX DRIVE VR COMPETITION TRAILER")
    print(f">>> Input:  {input_video}")
    print(f">>> Output: {output_video}")
    print("==================================================================")

    # Complex filtergraph with title card, lower thirds, and professional typography
    # Using drawbox and drawtext filters native to FFmpeg
    filter_complex = (
        # 1. Escalar a 1080p 60fps nítido
        "[0:v]scale=1920:1080:force_original_aspect_ratio=decrease,"
        "pad=1920:1080:(ow-iw)/2:(oh-ih)/2,fps=60,"
        
        # 2. Intro Branding (0 a 4.5 seg)
        "drawbox=y=ih-200:color=black@0.75:width=iw:height=160:t=fill:enable='between(t,0.5,4.5)',"
        "drawtext=text='APEX DRIVE VR \\: COCKPIT PURSUIT':fontcolor=white:fontsize=46:x=(w-text_w)/2:y=h-180:enable='between(t,0.5,4.5)',"
        "drawtext=text='Meta VR Start Developer Competition 2026':fontcolor=0x40C4FF:fontsize=28:x=(w-text_w)/2:y=h-110:enable='between(t,0.5,4.5)',"
        
        # 3. Banner 1: Cockpit e Inmersión VR (5 a 16 seg)
        "drawbox=y=ih-140:color=black@0.7:width=iw:height=100:t=fill:enable='between(t,5,16)',"
        "drawtext=text='1\\:1 INTERACTIVE VR STEERING & COCKPIT HUD':fontcolor=0xFFD54F:fontsize=36:x=80:y=h-125:enable='between(t,5,16)',"
        "drawtext=text='Real-time physics, mirror reflections, and responsive hand-first driving':fontcolor=white:fontsize=22:x=80:y=h-75:enable='between(t,5,16)',"
        
        # 4. Banner 2: IA Táctica Policial (17 a 30 seg)
        "drawbox=y=ih-140:color=black@0.7:width=iw:height=100:t=fill:enable='between(t,17,30)',"
        "drawtext=text='DYNAMIC PURSUIT AI & POLICE INTERCEPTORS':fontcolor=0xFF5252:fontsize=36:x=80:y=h-125:enable='between(t,17,30)',"
        "drawtext=text='Multi-lane AI interception, pit maneuvers, and 3D spatial siren audio':fontcolor=white:fontsize=22:x=80:y=h-75:enable='between(t,17,30)',"
        
        # 5. Banner 3: Metrópolis Urbana y Gráficos (31 a 45 seg)
        "drawbox=y=ih-140:color=black@0.7:width=iw:height=100:t=fill:enable='between(t,31,45)',"
        "drawtext=text='PROCEDURAL WINDOWED METROPOLIS':fontcolor=0x00E5FF:fontsize=36:x=80:y=h-125:enable='between(t,31,45)',"
        "drawtext=text='Residential districts, commercial towers, and atmospheric sunset reflections':fontcolor=white:fontsize=22:x=80:y=h-75:enable='between(t,31,45)',"
        
        # 6. Banner 4: Rendimiento y Confort (46 a 62 seg)
        "drawbox=y=ih-140:color=black@0.7:width=iw:height=100:t=fill:enable='between(t,46,62)',"
        "drawtext=text='SEATED VR COMFORT • ROCK-SOLID 60+ FPS':fontcolor=0x69F0AE:fontsize=36:x=80:y=h-125:enable='between(t,46,62)',"
        "drawtext=text='Engineered with Unreal Engine 5.8 for Meta Quest platform excellence':fontcolor=white:fontsize=22:x=80:y=h-75:enable='between(t,46,62)',"
        
        # 7. Outro (63 seg hasta el final)
        "drawbox=y=ih-180:color=black@0.8:width=iw:height=140:t=fill:enable='between(t,63,120)',"
        "drawtext=text='PLAY NOW ON META QUEST RELEASE CHANNEL':fontcolor=white:fontsize=38:x=(w-text_w)/2:y=h-160:enable='between(t,63,120)',"
        "drawtext=text='github.com/mapoca1219/VrMpc-ApexDriveVR':fontcolor=0x40C4FF:fontsize=26:x=(w-text_w)/2:y=h-95:enable='between(t,63,120)'"
        "[v_out]"
    )

    cmd = [
        FFMPEG_BIN,
        "-y",
        "-i", input_video,
        "-filter_complex", filter_complex,
        "-map", "[v_out]",
        "-map", "0:a?",
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "18",
        "-c:a", "aac",
        "-b:a", "192k",
        "-t", str(duration),
        output_video
    ]

    print(f">>> Executing FFmpeg rendering...")
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode == 0:
        print(f">>> [SUCCESS] Trailer generated cleanly at: {output_video}")
        return True
    else:
        print(f">>> [FFMPEG ERROR]:\n{res.stderr[-1000:]}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Apex Drive VR Trailer Generator")
    parser.add_argument("--input", "-i", default="Raw_Gameplay.mov", help="Path to raw recorded gameplay")
    parser.add_argument("--output", "-o", default="ApexDriveVR_Competition_Trailer.mp4", help="Output trailer path")
    parser.add_argument("--duration", "-d", type=int, default=75, help="Max duration in seconds")
    args = parser.parse_args()

    generate_trailer(args.input, args.output, args.duration)
