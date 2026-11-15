#!/usr/bin/env python3
"""
ApexDriveVR - Official YouTube Thumbnail Generator
Generates YouTube_Thumbnail_ApexDriveVR.jpg (1920x1080) with ultra-clean professional typography.
"""

import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGO_PATH = os.path.join(BASE_DIR, "logo_apex.jpeg")
GAMEPLAY_PATH = os.path.join(BASE_DIR, "scratch", "timeline_check", "t_060.jpg")
OUTPUT_PATH = os.path.join(BASE_DIR, "YouTube_Thumbnail_ApexDriveVR.jpg")

def create_thumbnail():
    width, height = 1920, 1080
    
    # 1. Base Gameplay Image
    if os.path.exists(GAMEPLAY_PATH):
        bg = Image.open(GAMEPLAY_PATH).convert("RGBA").resize((width, height), Image.Resampling.LANCZOS)
        enhancer = ImageEnhance.Contrast(bg)
        bg = enhancer.enhance(1.2)
        # Apply slight blur to background so foreground pops
        bg_blurred = bg.filter(ImageFilter.GaussianBlur(2.5))
    else:
        bg_blurred = Image.new("RGBA", (width, height), (15, 18, 25, 255))
        
    # 2. Dark Vignette / Gradient Overlay
    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw_ov = ImageDraw.Draw(overlay)
    
    # Left dark backing for logo
    for x in range(950):
        alpha = int(245 * (1.0 - (x / 950.0) ** 1.8))
        draw_ov.line([(x, 0), (x, height)], fill=(8, 10, 16, alpha))
        
    # Right dark backing for text callouts
    for x in range(850, width):
        norm = (x - 850) / (width - 850)
        alpha = int(230 * (norm ** 0.8))
        draw_ov.line([(x, 0), (x, height)], fill=(8, 10, 16, alpha))
        
    # Top & bottom borders
    for y in range(120):
        alpha = int(200 * (1.0 - (y / 120.0)))
        draw_ov.line([(0, y), (width, y)], fill=(4, 6, 10, alpha))
    for y in range(height - 130, height):
        alpha = int(240 * ((y - (height - 130)) / 130.0))
        draw_ov.line([(0, y), (width, y)], fill=(4, 6, 10, alpha))
        
    combined = Image.alpha_composite(bg_blurred, overlay)
    
    # 3. Add Logo Emblem on the left
    if os.path.exists(LOGO_PATH):
        logo = Image.open(LOGO_PATH).convert("RGBA")
        logo_size = 780
        logo = logo.resize((logo_size, logo_size), Image.Resampling.LANCZOS)
        
        # Soft cyan glow behind logo
        glow_size = logo_size + 50
        glow = Image.new("RGBA", (glow_size, glow_size), (0, 229, 255, 45))
        mask = Image.new("L", (glow_size, glow_size), 0)
        draw_mask = ImageDraw.Draw(mask)
        draw_mask.rounded_rectangle([15, 15, glow_size - 15, glow_size - 15], radius=50, fill=180)
        glow.putalpha(mask.filter(ImageFilter.GaussianBlur(25)))
        
        logo_pos = (50, (height - logo_size) // 2 - 20)
        combined.paste(glow, (logo_pos[0] - 25, logo_pos[1] - 25), glow)
        combined.paste(logo, logo_pos, logo)
        
    draw = ImageDraw.Draw(combined)
    
    # Fonts
    font_bold = "/System/Library/Fonts/Supplemental/Arial Black.ttf"
    font_impact = "/System/Library/Fonts/Supplemental/Impact.ttf"
    font_arial = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
    
    f_badge = ImageFont.truetype(font_bold, 28)
    f_title = ImageFont.truetype(font_impact, 50)
    f_sub = ImageFont.truetype(font_arial, 24)
    
    # Top-Left Hackathon Badge
    bx, by, bw, bh = 55, 40, 560, 52
    draw.rounded_rectangle([bx, by, bx + bw, by + bh], radius=8, fill=(0, 229, 255, 240))
    draw.text((bx + 20, by + 11), "META QUEST VR START 2026", font=f_badge, fill=(10, 12, 18))
    
    # Right-side Action Callouts
    rx = 910
    rw = 950
    
    # Box 1: 6DOF Interactive Cockpit
    y1 = 150
    draw.rounded_rectangle([rx, y1, rx + rw, y1 + 125], radius=14, fill=(12, 16, 26, 235), outline=(0, 229, 255), width=3)
    draw.text((rx + 30, y1 + 18), "6DOF HANDS-FIRST STEERING", font=f_title, fill=(0, 229, 255))
    draw.text((rx + 32, y1 + 78), "Full physical wheel grab, AI Copilot & real-time OLED telemetry", font=f_sub, fill=(230, 238, 250))
    
    # Box 2: Police Pursuit Combat
    y2 = 305
    draw.rounded_rectangle([rx, y2, rx + rw, y2 + 125], radius=14, fill=(12, 16, 26, 235), outline=(255, 55, 95), width=3)
    draw.text((rx + 30, y2 + 18), "TACTICAL POLICE PURSUIT AI", font=f_title, fill=(255, 65, 105))
    draw.text((rx + 32, y2 + 78), "PIT maneuvers, lane-blocking defense & spatial sirens", font=f_sub, fill=(230, 238, 250))
    
    # Box 3: Performance & Tech Stack
    y3 = 460
    draw.rounded_rectangle([rx, y3, rx + rw, y3 + 125], radius=14, fill=(12, 16, 26, 235), outline=(50, 225, 95), width=3)
    draw.text((rx + 30, y3 + 18), "SOLID 60 FPS • NATIVE C++", font=f_title, fill=(50, 225, 95))
    draw.text((rx + 32, y3 + 78), "Unreal Engine 5.8 • Chaos Physics • Meta XR SDK", font=f_sub, fill=(230, 238, 250))
    
    # Box 4: Nitro Thrusters
    y4 = 615
    draw.rounded_rectangle([rx, y4, rx + rw, y4 + 125], radius=14, fill=(12, 16, 26, 235), outline=(255, 175, 0), width=3)
    draw.text((rx + 30, y4 + 18), "DUAL PLASMA NITRO THRUSTERS", font=f_title, fill=(255, 185, 20))
    draw.text((rx + 32, y4 + 78), "280 km/h speed barrier with real chassis roll dynamics", font=f_sub, fill=(230, 238, 250))
    
    # Bottom Center High-Contrast Bar
    bot_y = height - 120
    draw.rectangle([0, bot_y, width, height], fill=(6, 8, 14, 250))
    draw.line([(0, bot_y), (width, bot_y)], fill=(0, 229, 255), width=4)
    
    f_footer_bold = ImageFont.truetype(font_bold, 34)
    draw.text((60, bot_y + 35), "DOWNLOAD NOW ON META QUEST APP LAB", font=f_footer_bold, fill=(0, 229, 255))
    
    f_footer_link = ImageFont.truetype(font_arial, 30)
    draw.text((1060, bot_y + 38), "https://www.meta.com/s/83yZYIoFL", font=f_footer_link, fill=(255, 255, 255))
    
    # Convert back to RGB and save
    final_img = combined.convert("RGB")
    final_img.save(OUTPUT_PATH, quality=96)
    print(f"[✓] Polished YouTube thumbnail generated -> {OUTPUT_PATH}")

if __name__ == "__main__":
    create_thumbnail()
