"""
=============================================================================
ENVIRONMENT DESIGNER - 2.5D MULTIPLANE STAGING GENERATOR
=============================================================================
Generates layered, illustrated, high-resolution textures for multiplane
Renaissance staging in Blender 4.2.
Layers:
  1. Deep Background (y=20): Stained glass gothic rose window & distant tapestries
  2. Midground Wall (y=10): Grand stone archways with royal Fleur-de-lis banners
  3. Throne Dais (y=2): Ornate gilded throne on elevated dais with crimson rug
  4. Floor (y=0): Polished diamond-tile Renaissance marble floor with reflections
  5. Foreground Framing (y=-3.5): Fluted marble pillars and hanging velvet drapes
=============================================================================
"""

import os
import math
from PIL import Image, ImageDraw, ImageFilter

OUTPUT_DIR = os.path.join("assets", "environments", "renaissance_court")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def generate_deep_background():
    """Generates deep atmospheric gothic stained glass and back wall (1920x1080)."""
    w, h = 1920, 1080
    im = Image.new("RGBA", (w, h), (18, 14, 28, 255))
    draw = ImageDraw.Draw(im)
    
    # Gradient wall
    for y in range(h):
        r = int(18 + 15 * (y / h))
        g = int(14 + 10 * (y / h))
        b = int(28 + 20 * (y / h))
        draw.line([(0, y), (w, y)], fill=(r, g, b, 255))
        
    # Large Central Gothic Rose Window
    cx, cy = w // 2, 380
    radius = 280
    
    # Outer stone ring
    draw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius], outline=(70, 65, 80, 255), width=18)
    draw.ellipse([cx - radius + 15, cy - radius + 15, cx + radius - 15, cy + radius - 15], outline=(40, 35, 50, 255), width=6)
    
    # Stained glass luminous petals
    colors = [
        (40, 90, 180, 180),   # Royal azure
        (180, 40, 60, 180),   # Ruby red
        (220, 170, 40, 180),  # Golden amber
        (50, 140, 90, 180),   # Emerald
    ]
    num_spokes = 12
    for i in range(num_spokes):
        ang1 = math.radians(i * (360 / num_spokes))
        ang2 = math.radians((i + 1) * (360 / num_spokes))
        x1 = cx + int((radius - 30) * math.cos(ang1))
        y1 = cy + int((radius - 30) * math.sin(ang1))
        x2 = cx + int((radius - 30) * math.cos(ang2))
        y2 = cy + int((radius - 30) * math.sin(ang2))
        
        col = colors[i % len(colors)]
        draw.polygon([(cx, cy), (x1, y1), (x2, y2)], fill=col, outline=(30, 25, 40, 255))
        
    # Inner rosette
    draw.ellipse([cx - 80, cy - 80, cx + 80, cy + 80], fill=(240, 200, 60, 220), outline=(50, 40, 60, 255), width=8)
    draw.ellipse([cx - 30, cy - 30, cx + 30, cy + 30], fill=(180, 30, 40, 255))
    
    # Soft window glow filter
    glow = im.filter(ImageFilter.GaussianBlur(radius=6))
    im = Image.alpha_composite(im, glow)
    
    out_path = os.path.join(OUTPUT_DIR, "deep_background.png")
    im.save(out_path)
    print(f"[+] Saved Deep Background to {out_path}")
    return out_path

def generate_midground_wall():
    """Generates grand stone archways and royal fleur-de-lis banners (2160x1440)."""
    w, h = 2160, 1440
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(im)
    
    # Grand stone masonry wall with cutouts for windows
    stone_dark = (42, 38, 52, 255)
    stone_mid = (65, 60, 78, 255)
    stone_light = (88, 82, 104, 255)
    
    # Large arches framing the windows
    # Left arch, center arch, right arch
    arch_specs = [
        (360, 260, 420),
        (w // 2, 240, 480),
        (w - 360, 260, 420),
    ]
    
    # Draw solid upper masonry wall
    draw.rectangle([0, 0, w, 400], fill=stone_mid)
    
    # Draw stone piers / pillars
    pier_positions = [100, 640, w // 2 - 270, w // 2 + 270, w - 640, w - 100]
    for px in pier_positions:
        draw.rectangle([px - 50, 200, px + 50, h], fill=stone_dark, outline=stone_light, width=4)
        # Decorative capitals
        draw.polygon([(px - 70, 200), (px + 70, 200), (px + 50, 240), (px - 50, 240)], fill=stone_light)
        
    # Hanging Royal Banners (Royal Blue and Crimson Velvet with Gold Fleur-de-lis)
    banner_specs = [
        (480, 280, 160, 520, (25, 45, 110, 245)),    # Left Royal Azure
        (w - 480, 280, 160, 520, (130, 20, 35, 245)), # Right Crimson Velvet
    ]
    for bx, by, bw, bh, bcol in banner_specs:
        # Hanging pole
        draw.rectangle([bx - bw // 2 - 20, by, bx + bw // 2 + 20, by + 16], fill=(190, 150, 40, 255))
        # Banner cloth with swallowtail bottom
        pts = [
            (bx - bw // 2, by + 16),
            (bx + bw // 2, by + 16),
            (bx + bw // 2, by + bh),
            (bx, by + bh - 60),
            (bx - bw // 2, by + bh),
        ]
        draw.polygon(pts, fill=bcol, outline=(220, 180, 50, 255), width=6)
        
        # Gold Fleur-de-lis motif on banner
        gold = (245, 210, 60, 255)
        # Center petal
        draw.ellipse([bx - 12, by + 160, bx + 12, by + 230], fill=gold)
        # Side petals
        draw.ellipse([bx - 36, by + 185, bx, by + 225], fill=gold)
        draw.ellipse([bx, by + 185, bx + 36, by + 225], fill=gold)
        # Horizontal cross tie
        draw.rectangle([bx - 30, by + 220, bx + 30, by + 232], fill=(210, 160, 30, 255))
        # Lower base
        draw.polygon([(bx - 16, by + 232), (bx + 16, by + 232), (bx, by + 265)], fill=gold)
        
        # Fringes at bottom
        for fx in range(bx - bw // 2 + 10, bx + bw // 2 - 10, 12):
            fy = by + bh if fx < bx else by + bh
            draw.line([(fx, by + bh - 20), (fx, by + bh + 15)], fill=gold, width=3)
            
    out_path = os.path.join(OUTPUT_DIR, "midground_wall.png")
    im.save(out_path)
    print(f"[+] Saved Midground Wall to {out_path}")
    return out_path

def generate_throne_dais():
    """Generates the King's ornate elevated throne and dais (1200x1200)."""
    w, h = 1200, 1200
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(im)
    
    cx = w // 2
    
    # 1. Stone Dais Steps (elevated platform)
    step_y = 900
    # Step 3 (base)
    draw.polygon([(cx - 450, step_y + 160), (cx + 450, step_y + 160), (cx + 400, step_y + 100), (cx - 400, step_y + 100)],
                 fill=(60, 55, 70, 255), outline=(90, 85, 105, 255), width=3)
    # Step 2
    draw.polygon([(cx - 380, step_y + 100), (cx + 380, step_y + 100), (cx + 340, step_y + 40), (cx - 340, step_y + 40)],
                 fill=(70, 65, 82, 255), outline=(100, 95, 118, 255), width=3)
    # Step 1 (top platform)
    draw.polygon([(cx - 320, step_y + 40), (cx + 320, step_y + 40), (cx + 280, step_y - 20), (cx - 280, step_y - 20)],
                 fill=(80, 75, 95, 255), outline=(115, 110, 130, 255), width=3)
                 
    # 2. Crimson Royal Carpet flowing down steps
    carpet_pts = [
        (cx - 140, step_y - 20),
        (cx + 140, step_y - 20),
        (cx + 200, step_y + 160),
        (cx - 200, step_y + 160),
    ]
    draw.polygon(carpet_pts, fill=(160, 22, 40, 255), outline=(225, 185, 55, 255), width=6)
    
    # 3. Gilded Renaissance Throne
    throne_base_y = step_y - 20
    gold_dark = (175, 130, 25, 255)
    gold_mid = (225, 180, 45, 255)
    gold_bright = (255, 220, 85, 255)
    velvet_red = (145, 18, 35, 255)
    
    # High gothic carved backrest
    back_w, back_h = 240, 540
    back_top_y = throne_base_y - back_h
    
    # Throne Outer Gold Frame with ornate crest
    draw.rectangle([cx - back_w // 2, back_top_y, cx + back_w // 2, throne_base_y], fill=gold_mid, outline=gold_dark, width=8)
    # Top arch crown on throne
    draw.polygon([
        (cx - back_w // 2 - 20, back_top_y),
        (cx, back_top_y - 90),
        (cx + back_w // 2 + 20, back_top_y)
    ], fill=gold_mid, outline=gold_bright, width=6)
    
    # Carved Fleur-de-lis finial at pinnacle
    draw.ellipse([cx - 25, back_top_y - 120, cx + 25, back_top_y - 70], fill=gold_bright)
    
    # Deep Tufted Velvet Backrest Cushion
    cushion_inset = 24
    draw.rectangle([cx - back_w // 2 + cushion_inset, back_top_y + cushion_inset,
                    cx + back_w // 2 - cushion_inset, throne_base_y - 120],
                   fill=velvet_red, outline=gold_dark, width=4)
                   
    # Quilted diamond pattern on velvet
    for qy in range(back_top_y + cushion_inset + 40, throne_base_y - 140, 50):
        for qx in range(cx - back_w // 2 + cushion_inset + 35, cx + back_w // 2 - cushion_inset, 50):
            draw.ellipse([qx - 4, qy - 4, qx + 4, qy + 4], fill=gold_mid)
            
    # Seat Cushion
    draw.rectangle([cx - 150, throne_base_y - 140, cx + 150, throne_base_y - 80],
                   fill=(180, 25, 45, 255), outline=gold_mid, width=6)
                   
    # Carved Armrests (lion heads / scrollwork)
    draw.rectangle([cx - 170, throne_base_y - 200, cx - 140, throne_base_y - 70], fill=gold_mid, outline=gold_bright, width=4)
    draw.ellipse([cx - 180, throne_base_y - 220, cx - 130, throne_base_y - 180], fill=gold_bright, outline=gold_dark, width=3)
    
    draw.rectangle([cx + 140, throne_base_y - 200, cx + 170, throne_base_y - 70], fill=gold_mid, outline=gold_bright, width=4)
    draw.ellipse([cx + 130, throne_base_y - 220, cx + 180, throne_base_y - 180], fill=gold_bright, outline=gold_dark, width=3)
    
    # Heavy throne legs
    draw.rectangle([cx - 150, throne_base_y - 80, cx - 120, throne_base_y], fill=gold_mid)
    draw.rectangle([cx + 120, throne_base_y - 80, cx + 150, throne_base_y], fill=gold_mid)
    
    out_path = os.path.join(OUTPUT_DIR, "throne_dais.png")
    im.save(out_path)
    print(f"[+] Saved Throne Dais to {out_path}")
    return out_path

def generate_marble_floor():
    """Generates seamless polished diamond-pattern Renaissance marble floor (2048x2048)."""
    w, h = 2048, 2048
    im = Image.new("RGBA", (w, h), (40, 36, 48, 255))
    draw = ImageDraw.Draw(im)
    
    tile_size = 128
    cols = w // tile_size + 2
    rows = h // tile_size + 2
    
    marble_white = (215, 210, 222, 255)
    marble_black = (30, 26, 38, 255)
    vein_grey = (170, 165, 178, 255)
    mortar_gold = (110, 95, 60, 255)
    
    for r in range(rows):
        for c in range(cols):
            x = c * tile_size
            y = r * tile_size
            # Diamond coordinate
            is_dark = (r + c) % 2 == 0
            base_col = marble_black if is_dark else marble_white
            
            # Diamond polygon
            pts = [
                (x, y + tile_size // 2),
                (x + tile_size // 2, y),
                (x + tile_size, y + tile_size // 2),
                (x + tile_size // 2, y + tile_size)
            ]
            draw.polygon(pts, fill=base_col, outline=mortar_gold, width=2)
            
            # Subtle veins
            if not is_dark:
                draw.line([(x + 25, y + 40), (x + 75, y + 90)], fill=vein_grey, width=2)
                
    out_path = os.path.join(OUTPUT_DIR, "marble_floor.png")
    im.save(out_path)
    print(f"[+] Saved Marble Floor to {out_path}")
    return out_path

def generate_foreground_framing():
    """Generates left and right foreground fluted marble columns and upper velvet drape (1920x1080)."""
    w, h = 1920, 1080
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(im)
    
    pillar_w = 260
    
    # Left Massive Pillar
    col_dark = (48, 44, 58, 255)
    col_mid = (78, 72, 92, 255)
    col_light = (115, 108, 134, 255)
    
    # Pillar body
    draw.rectangle([0, 0, pillar_w, h], fill=col_mid, outline=(25, 22, 32, 255), width=8)
    # Fluting vertical grooves
    for fx in range(35, pillar_w - 20, 32):
        draw.line([(fx, 0), (fx, h)], fill=col_dark, width=6)
        draw.line([(fx + 8, 0), (fx + 8, h)], fill=col_light, width=4)
        
    # Right Massive Pillar
    rx = w - pillar_w
    draw.rectangle([rx, 0, w, h], fill=col_mid, outline=(25, 22, 32, 255), width=8)
    for fx in range(rx + 35, w - 20, 32):
        draw.line([(fx, 0), (fx, h)], fill=col_dark, width=6)
        draw.line([(fx + 8, 0), (fx + 8, h)], fill=col_light, width=4)
        
    # Hanging Velvet Valances (Theater Curtains Framing top)
    drape_red = (120, 15, 28, 245)
    drape_gold = (215, 175, 45, 255)
    
    # Scalloped valance
    num_scallops = 6
    scallop_w = w // num_scallops
    for i in range(num_scallops):
        sx = i * scallop_w
        # Arch downward
        draw.chord([sx - 10, -80, sx + scallop_w + 10, 160], start=0, end=180, fill=drape_red, outline=drape_gold, width=6)
        # Gold tassel at scallop junction
        draw.ellipse([sx + scallop_w - 12, 110, sx + scallop_w + 12, 134], fill=drape_gold)
        draw.line([(sx + scallop_w, 134), (sx + scallop_w, 170)], fill=drape_gold, width=4)
        
    out_path = os.path.join(OUTPUT_DIR, "foreground_framing.png")
    im.save(out_path)
    print(f"[+] Saved Foreground Framing to {out_path}")
    return out_path

if __name__ == "__main__":
    print("[*] Generating 2.5D Multiplane Renaissance Environment Layers...")
    generate_deep_background()
    generate_midground_wall()
    generate_throne_dais()
    generate_marble_floor()
    generate_foreground_framing()
    print("[+] All environment layers generated successfully!")
