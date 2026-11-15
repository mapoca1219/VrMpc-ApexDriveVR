#!/usr/bin/env python3
"""
ApexDriveVR - Final Master Video Producer
Generates ApexDriveVR_Final_Master.mp4 for YouTube and Hackathon Submission.

Applies 5 key automated post-production corrections:
1. Clean Initial Cut: Trims first 1.2s (-ss 00:00:01.200) to remove UE editor artifacts.
2. Debug HUD Cleanup: Localized boxblur over top-left debug texts (x=0:y=0:w=420:h=95).
3. 6DOF VR Cockpit Callout: Futuristic HUD callout banner at t=30s-48s:
   "HANDS-FIRST 6DOF STEERING & DIEGETIC OLED TELEMETRY"
4. Official Logo Integration:
   - 2.0s intro card with smooth fade in/out centered.
   - Persistent clean watermark (120x120px, 85% opacity) top-right.
5. Burned Subtitles & 1080p 60fps Master Export:
   - Synchronized English subtitles from apex_drive_vr_shifted.srt.
   - Encoded with libx264 (-crf 18, -preset fast, 60fps, yuv420p).
   - Audio: AAC 192k 48kHz stereo, full timeline preserved.
"""

import os
import sys
import subprocess
import shutil
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_VIDEO = os.path.join(BASE_DIR, "ApexDriveVR.mp4")
INPUT_LOGO = os.path.join(BASE_DIR, "logo_apex.jpeg")
SUBTITLES_FILE = os.path.join(BASE_DIR, "scratch", "apex_drive_vr_shifted.srt")
OUTPUT_VIDEO = os.path.join(BASE_DIR, "ApexDriveVR_Final_Master.mp4")

def check_prerequisites():
    if not shutil.which("ffmpeg"):
        print("[!] FFmpeg not found in PATH! Please install via 'brew install ffmpeg'.", file=sys.stderr)
        sys.exit(1)
    if not os.path.exists(INPUT_VIDEO):
        alt = os.path.join(BASE_DIR, "ApexDriveVR_Winning_Trailer.mp4")
        if os.path.exists(alt):
            os.symlink(alt, INPUT_VIDEO)
        else:
            print(f"[!] Input video not found: {INPUT_VIDEO}", file=sys.stderr)
            sys.exit(1)
    if not os.path.exists(INPUT_LOGO):
        alt = os.path.join(BASE_DIR, "logo.jpeg")
        if os.path.exists(alt):
            os.symlink(alt, INPUT_LOGO)
        else:
            print(f"[!] Input logo not found: {INPUT_LOGO}", file=sys.stderr)
            sys.exit(1)
    if not os.path.exists(SUBTITLES_FILE):
        print(f"[!] Subtitles file not found: {SUBTITLES_FILE}", file=sys.stderr)
        sys.exit(1)
    print("[✓] Prerequisites verified successfully.")

def build_filtergraph():
    # Filter complex chain
    # 1. Clean debug hud on top-left (420x95)
    f_hud = (
        "[0:v]split=2[v_orig][c_hud];"
        "[c_hud]crop=420:95:0:0,boxblur=8:1[hud_blurred];"
        "[v_orig][hud_blurred]overlay=0:0[v_clean_hud];"
    )
    
    # 2. Intro Logo (first 2.0s with smooth fade in/out)
    f_intro = (
        "[1:v]format=rgba,scale=700:700,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:black,"
        "loop=loop=120:size=1:start=0,setpts=N/60/TB,"
        "fade=in:st=0:d=0.4:alpha=1,fade=out:st=1.6:d=0.4:alpha=1[logo_intro];"
        "[v_clean_hud][logo_intro]overlay=0:0:enable='between(t,0,2.0)':eof_action=pass[v_step1];"
    )
    
    # 3. Persistent Watermark Logo (top-right, 120x120, 85% opacity, active after intro t>=2.0)
    f_wm = (
        "[1:v]scale=120:120,format=rgba,colorchannelmixer=aa=0.85,"
        "loop=loop=10000:size=1:start=0,setpts=N/60/TB[logo_wm];"
        "[v_step1][logo_wm]overlay=W-w-25:18:enable='gte(t,2.0)':eof_action=pass[v_step2];"
    )
    
    # 4. 6DOF VR Cockpit Callout banner (t=30s to 48s) + Burned Subtitles
    callout_text = "HANDS-FIRST 6DOF STEERING & DIEGETIC OLED TELEMETRY"
    sub_style = (
        "PlayResX=1920,PlayResY=1080,Fontname=Arial,FontSize=24,"
        "PrimaryColour=&H00FFFFFF,OutlineColour=&H80000000,BorderStyle=3,Outline=2,Shadow=0,MarginV=115"
    )
    f_callout_and_subs = (
        f"[v_step2]drawbox=x=(iw-920)/2:y=108:w=920:h=56:color=black@0.85:t=fill:enable='between(t,30,48)',"
        f"drawbox=x=(iw-920)/2:y=108:w=920:h=56:color=0x00E5FF@0.9:t=2:enable='between(t,30,48)',"
        f"drawtext=text='{callout_text}':fontcolor=0x00E5FF:fontsize=26:x=(w-text_w)/2:y=122:enable='between(t,30,48)',"
        f"subtitles='{SUBTITLES_FILE}':force_style='{sub_style}'[v_out]"
    )
    
    return f_hud + f_intro + f_wm + f_callout_and_subs

def render_master():
    print(f"[*] Starting render of master video -> {OUTPUT_VIDEO}")
    filtergraph = build_filtergraph()
    
    cmd = [
        "ffmpeg", "-y",
        "-ss", "00:00:01.200",
        "-i", INPUT_VIDEO,
        "-i", INPUT_LOGO,
        "-filter_complex", filtergraph,
        "-map", "[v_out]",
        "-map", "0:a",
        "-c:v", "libx264",
        "-crf", "18",
        "-preset", "fast",
        "-pix_fmt", "yuv420p",
        "-r", "60",
        "-c:a", "aac",
        "-b:a", "192k",
        "-ar", "48000",
        "-t", "156.80",
        "-movflags", "+faststart",
        OUTPUT_VIDEO
    ]
    
    print(f"[*] Executing FFmpeg command...")
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    
    for line in iter(process.stdout.readline, ""):
        if "frame=" in line or "time=" in line:
            print(f"\r{line.strip()}", end="", flush=True)
    process.stdout.close()
    return_code = process.wait()
    print()
    
    if return_code != 0:
        print(f"[!] FFmpeg failed with return code {return_code}", file=sys.stderr)
        sys.exit(return_code)
        
    print(f"[✓] Render finished successfully: {OUTPUT_VIDEO}")

def verify_output():
    print("[*] Verifying output file metadata...")
    probe_cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration,size,bit_rate:stream=codec_type,codec_name,width,height,r_frame_rate,duration",
        "-of", "json",
        OUTPUT_VIDEO
    ]
    res = subprocess.run(probe_cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print("[!] FFprobe failed:", res.stderr, file=sys.stderr)
        return
    data = json.loads(res.stdout)
    streams = data.get("streams", [])
    format_info = data.get("format", {})
    
    print("=== Master File Verification ===")
    print(f"Path: {OUTPUT_VIDEO}")
    print(f"Size: {int(format_info.get('size', 0)) / (1024*1024):.2f} MB")
    print(f"Duration: {float(format_info.get('duration', 0)):.2f}s")
    for s in streams:
        if s.get("codec_type") == "video":
            print(f"Video: {s.get('codec_name')} {s.get('width')}x{s.get('height')} @ {s.get('r_frame_rate')} fps")
        elif s.get("codec_type") == "audio":
            print(f"Audio: {s.get('codec_name')} duration: {float(s.get('duration', 0)):.2f}s")
    print("================================")

if __name__ == "__main__":
    check_prerequisites()
    render_master()
    verify_output()
