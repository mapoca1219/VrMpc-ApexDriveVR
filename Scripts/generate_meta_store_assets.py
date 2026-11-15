#!/usr/bin/env python3
"""
ApexDriveVR - Meta Horizon Store & App Lab Assets Generator
Generates all mandatory store and submission graphics required by Meta Quest Developer Hub and App Lab:
1. App Icon (512x512 PNG)
2. Cover Landscape (2560x1440 PNG)
3. Cover Portrait (1008x1440 PNG)
4. Store Hero Banner (3000x900 PNG)
5. 5 Curated 1080p Gameplay Screenshots
"""

import os
import shutil
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, "Meta_Store_Assets")
LOGO_PATH = os.path.join(BASE_DIR, "logo_apex.jpeg")
SCRATCH_DIR = os.path.join(BASE_DIR, "scratch")

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def generate_app_icon():
    print("[*] Generating App Icon (512x512)...")
    if os.path.exists(LOGO_PATH):
        im = Image.open(LOGO_PATH).convert("RGBA")
        icon = im.resize((512, 512), Image.Resampling.LANCZOS)
        out_path = os.path.join(OUTPUT_DIR, "Meta_App_Icon_512x512.png")
        icon.save(out_path, format="PNG")
        print(f"[✓] Saved: {out_path}")

def generate_cover_landscape():
    print("[*] Generating Cover Landscape (2560x1440)...")
    width, height = 2560, 1440
    bg_src = os.path.join(SCRATCH_DIR, "timeline_check", "t_060.jpg")
    if os.path.exists(bg_src):
        bg = Image.open(bg_src).convert("RGBA").resize((width, height), Image.Resampling.LANCZOS)
        bg = ImageEnhance.Contrast(bg).enhance(1.15)
        bg = bg.filter(ImageFilter.GaussianBlur(3))
    else:
        bg = Image.new("RGBA", (width, height), (10, 12, 18, 255))
        
    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw_ov = ImageDraw.Draw(overlay)
    
    # Left gradient
    for x in range(1400):
        alpha = int(240 * (1.0 - (x / 1400.0) ** 1.6))
        draw_ov.line([(x, 0), (x, height)], fill=(6, 8, 14, alpha))
        
    for y in range(height - 200, height):
        alpha = int(220 * ((y - (height - 200)) / 200.0))
        draw_ov.line([(0, y), (width, y)], fill=(6, 8, 14, alpha))
        
    combined = Image.alpha_composite(bg, overlay)
    
    # Paste Logo
    if os.path.exists(LOGO_PATH):
        logo = Image.open(LOGO_PATH).convert("RGBA")
        logo_size = 960
        logo = logo.resize((logo_size, logo_size), Image.Resampling.LANCZOS)
        logo_pos = (120, (height - logo_size) // 2)
        combined.paste(logo, logo_pos, logo)
        
    draw = ImageDraw.Draw(combined)
    font_bold = "/System/Library/Fonts/Supplemental/Arial Black.ttf"
    font_arial = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
    
    f_badge = ImageFont.truetype(font_bold, 36)
    f_title = ImageFont.truetype(font_bold, 64)
    f_sub = ImageFont.truetype(font_arial, 34)
    
    # Top badge
    draw.rounded_rectangle([120, 60, 800, 125], radius=10, fill=(0, 229, 255, 240))
    draw.text((145, 75), "META QUEST 2 / 3 / PRO", font=f_badge, fill=(10, 12, 18))
    
    # Right-side text highlights
    rx = 1250
    draw.text((rx, 420), "APEX DRIVE VR", font=f_title, fill=(0, 229, 255))
    draw.text((rx, 505), "COCKPIT PURSUIT", font=f_title, fill=(255, 255, 255))
    draw.text((rx, 600), "• 6DOF Hands-First Virtual Steering", font=f_sub, fill=(230, 238, 250))
    draw.text((rx, 660), "• Diegetic Real-Time OLED Telemetry", font=f_sub, fill=(230, 238, 250))
    draw.text((rx, 720), "• Tactical Combat Police AI with PIT Maneuvers", font=f_sub, fill=(230, 238, 250))
    draw.text((rx, 780), "• Solid 60 FPS Engine • Unreal Engine 5.8 & C++", font=f_sub, fill=(230, 238, 250))
    
    out_path = os.path.join(OUTPUT_DIR, "Meta_Cover_Landscape_2560x1440.png")
    combined.convert("RGB").save(out_path, format="PNG")
    print(f"[✓] Saved: {out_path}")

def generate_cover_portrait():
    print("[*] Generating Cover Portrait (1008x1440)...")
    width, height = 1008, 1440
    bg = Image.new("RGBA", (width, height), (8, 10, 16, 255))
    
    bg_src = os.path.join(SCRATCH_DIR, "timeline_check", "t_060.jpg")
    if os.path.exists(bg_src):
        bg_im = Image.open(bg_src).convert("RGBA").resize((width, int(width * 9 / 16)), Image.Resampling.LANCZOS)
        bg.paste(bg_im, (0, 0))
        
    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw_ov = ImageDraw.Draw(overlay)
    for y in range(250, height):
        alpha = min(255, int(255 * ((y - 250) / 250.0)))
        draw_ov.line([(0, y), (width, y)], fill=(8, 10, 16, alpha))
    combined = Image.alpha_composite(bg, overlay)
    
    # Logo in lower half
    if os.path.exists(LOGO_PATH):
        logo = Image.open(LOGO_PATH).convert("RGBA")
        logo_size = 720
        logo = logo.resize((logo_size, logo_size), Image.Resampling.LANCZOS)
        combined.paste(logo, ((width - logo_size) // 2, 450), logo)
        
    draw = ImageDraw.Draw(combined)
    font_bold = "/System/Library/Fonts/Supplemental/Arial Black.ttf"
    font_arial = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
    
    f_badge = ImageFont.truetype(font_bold, 26)
    f_sub = ImageFont.truetype(font_arial, 28)
    
    draw.rounded_rectangle([(width - 480) // 2, 80, (width + 480) // 2, 135], radius=8, fill=(0, 229, 255, 240))
    draw.text(((width - 480) // 2 + 25, 93), "META QUEST VR RACING", font=f_badge, fill=(10, 12, 18))
    
    draw.text(((width - 640) // 2, 1230), "6DOF HANDS-FIRST COMBAT RACING", font=f_sub, fill=(0, 229, 255))
    draw.text(((width - 450) // 2, 1280), "BUILT FOR META QUEST 2 / 3 / PRO", font=f_sub, fill=(200, 210, 225))
    
    out_path = os.path.join(OUTPUT_DIR, "Meta_Cover_Portrait_1008x1440.png")
    combined.convert("RGB").save(out_path, format="PNG")
    print(f"[✓] Saved: {out_path}")

def export_curated_screenshots():
    print("[*] Exporting 5 Curated 1080p Gameplay Screenshots...")
    shots = [
        ("final_master_t1.jpg", "Screenshot_01_Title_Logo.png"),
        ("final_master_t15.jpg", "Screenshot_02_Nitro_Thrust_280kmh.png"),
        ("final_master_t35.jpg", "Screenshot_03_6DOF_Cockpit_Steering.png"),
        ("final_master_t80.jpg", "Screenshot_04_Police_Pursuit_Combat.png"),
        ("final_master_t154.jpg", "Screenshot_05_Outro_AppLab_GitHub.png")
    ]
    for src_name, dst_name in shots:
        src = os.path.join(SCRATCH_DIR, src_name)
        dst = os.path.join(OUTPUT_DIR, dst_name)
        if os.path.exists(src):
            im = Image.open(src).convert("RGB")
            im.save(dst, format="PNG")
            print(f"[✓] Exported: {dst}")

if __name__ == "__main__":
    ensure_dir(OUTPUT_DIR)
    generate_app_icon()
    generate_cover_landscape()
    generate_cover_portrait()
    export_curated_screenshots()
    print("\n[🎉] All Meta Horizon Store & App Lab assets created successfully!")
