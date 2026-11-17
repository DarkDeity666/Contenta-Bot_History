"""
=============================================================================
CHARACTER DESIGNER V2 - REFERENCE-ACCURATE 2D CARTOON PUPPETS
=============================================================================
Generates high-resolution, hand-drawn style cartoon character assets exactly
matching the reference videos:
- Bold, smooth organic outlines (supersampled at 2x)
- Expressive cartoon faces (big round eyes with directional pupils, animated mouth shapes)
- Themed Renaissance costumes (Triboulet's jester tunic & cap, King Francis I's royal robes & crown)
- Clean puppet joints designed for seamless articulation in Blender / 2.5D
=============================================================================
"""

import os
import math
from PIL import Image, ImageDraw, ImageFilter

OUTPUT_DIR = os.path.join("assets", "character_rigs_v2")
os.makedirs(os.path.join(OUTPUT_DIR, "triboulet"), exist_ok=True)
os.makedirs(os.path.join(OUTPUT_DIR, "king_francis"), exist_ok=True)

# Common style constants
STROKE_COLOR = (32, 28, 36, 255)  # Rich comic dark ink
STROKE_W = 10                     # Bold outline (at 2x supersampling = 5px final)

def supersample_save(img_2x, out_path):
    """Downsamples 2x supersampled image with Lanczos for razor-sharp, anti-aliased vector look."""
    w, h = img_2x.size
    final_img = img_2x.resize((w // 2, h // 2), Image.Resampling.LANCZOS)
    final_img.save(out_path)
    return out_path

# =============================================================================
# 1. TRIBOULET (THE ROYAL JESTER)
# =============================================================================

def generate_triboulet_head(expression="smirk"):
    """
    Draws Triboulet's iconic round cartoon head with expressive facial features.
    Expressions: neutral, smirk, laugh, shock, terrified
    """
    w, h = 600, 600
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(im)
    
    cx, cy = w // 2, h // 2 + 30
    radius = 180
    
    # 1. Head Base: Clean circular cartoon face
    skin_fill = (252, 248, 240, 255)  # Warm cartoon skin
    draw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius],
                 fill=skin_fill, outline=STROKE_COLOR, width=STROKE_W)
                 
    # 2. Rosy Cheek Blush
    blush_col = (255, 180, 190, 160)
    draw.ellipse([cx - radius + 40, cy + 20, cx - radius + 110, cy + 70], fill=blush_col)
    draw.ellipse([cx + radius - 110, cy + 20, cx + radius - 40, cy + 70], fill=blush_col)
    
    # 3. Eyes & Eyebrows based on expression
    eye_y = cy - 20
    eye_spacing = 75
    eye_r = 32
    
    if expression in ["smirk", "neutral", "laugh"]:
        # Left eye
        draw.ellipse([cx - eye_spacing - eye_r, eye_y - eye_r, cx - eye_spacing + eye_r, eye_y + eye_r],
                     fill=(255, 255, 255, 255), outline=STROKE_COLOR, width=6)
        # Right eye
        draw.ellipse([cx + eye_spacing - eye_r, eye_y - eye_r, cx + eye_spacing + eye_r, eye_y + eye_r],
                     fill=(255, 255, 255, 255), outline=STROKE_COLOR, width=6)
                     
        # Pupils (looking slightly toward King / upper right)
        pupil_r = 16
        pupil_offset_x = 10 if expression == "smirk" else 0
        draw.ellipse([cx - eye_spacing + pupil_offset_x - pupil_r, eye_y - pupil_r,
                      cx - eye_spacing + pupil_offset_x + pupil_r, eye_y + pupil_r], fill=STROKE_COLOR)
        draw.ellipse([cx + eye_spacing + pupil_offset_x - pupil_r, eye_y - pupil_r,
                      cx + eye_spacing + pupil_offset_x + pupil_r, eye_y + pupil_r], fill=STROKE_COLOR)
        # White twinkle in pupils
        draw.ellipse([cx - eye_spacing + pupil_offset_x - 6, eye_y - 8,
                      cx - eye_spacing + pupil_offset_x + 2, eye_y], fill=(255, 255, 255, 255))
        draw.ellipse([cx + eye_spacing + pupil_offset_x - 6, eye_y - 8,
                      cx + eye_spacing + pupil_offset_x + 2, eye_y], fill=(255, 255, 255, 255))
                      
        # Eyebrows: arched slyly
        if expression == "smirk":
            draw.arc([cx - eye_spacing - 40, eye_y - 65, cx - eye_spacing + 40, eye_y - 35],
                     start=190, end=350, fill=STROKE_COLOR, width=8)
            draw.arc([cx + eye_spacing - 40, eye_y - 75, cx + eye_spacing + 40, eye_y - 45],
                     start=180, end=340, fill=STROKE_COLOR, width=8)
        elif expression == "laugh":
            draw.arc([cx - eye_spacing - 40, eye_y - 60, cx - eye_spacing + 40, eye_y - 30],
                     start=200, end=340, fill=STROKE_COLOR, width=8)
            draw.arc([cx + eye_spacing - 40, eye_y - 60, cx + eye_spacing + 40, eye_y - 30],
                     start=200, end=340, fill=STROKE_COLOR, width=8)
                     
    elif expression in ["shock", "terrified"]:
        # Massive wide eyes with tiny pinpoint pupils
        big_r = 45
        draw.ellipse([cx - eye_spacing - big_r, eye_y - big_r, cx - eye_spacing + big_r, eye_y + big_r],
                     fill=(255, 255, 255, 255), outline=STROKE_COLOR, width=7)
        draw.ellipse([cx + eye_spacing - big_r, eye_y - big_r, cx + eye_spacing + big_r, eye_y + big_r],
                     fill=(255, 255, 255, 255), outline=STROKE_COLOR, width=7)
        # Tiny pupils
        draw.ellipse([cx - eye_spacing - 8, eye_y - 8, cx - eye_spacing + 8, eye_y + 8], fill=STROKE_COLOR)
        draw.ellipse([cx + eye_spacing - 8, eye_y - 8, cx + eye_spacing + 8, eye_y + 8], fill=STROKE_COLOR)
        # Raised high worried eyebrows
        draw.arc([cx - eye_spacing - 45, eye_y - 85, cx - eye_spacing + 45, eye_y - 45],
                 start=160, end=340, fill=STROKE_COLOR, width=8)
        draw.arc([cx + eye_spacing - 45, eye_y - 85, cx + eye_spacing + 45, eye_y - 45],
                 start=200, end=380, fill=STROKE_COLOR, width=8)
        # Comic sweat drop on brow
        sw_x, sw_y = cx + radius - 60, cy - 80
        draw.polygon([(sw_x, sw_y - 25), (sw_x + 18, sw_y + 10), (sw_x - 18, sw_y + 10)], fill=(120, 200, 255, 240))
        draw.ellipse([sw_x - 18, sw_y - 5, sw_x + 18, sw_y + 20], fill=(120, 200, 255, 240))
        
    # 4. Nose: small cute hook
    draw.line([(cx, eye_y + 10), (cx + 8, eye_y + 35)], fill=STROKE_COLOR, width=6)
    draw.line([(cx + 8, eye_y + 35), (cx - 4, eye_y + 40)], fill=STROKE_COLOR, width=6)
    
    # 5. Mouth
    mouth_y = cy + 70
    if expression == "smirk":
        # Asymmetrical confident smirk
        draw.arc([cx - 45, mouth_y - 30, cx + 55, mouth_y + 30], start=10, end=170, fill=STROKE_COLOR, width=8)
        draw.line([(cx + 45, mouth_y), (cx + 58, mouth_y - 12)], fill=STROKE_COLOR, width=7)
    elif expression == "laugh":
        # Big open laughing mouth showing teeth and tongue
        pts = [(cx - 60, mouth_y - 10), (cx + 60, mouth_y - 10), (cx + 45, mouth_y + 60), (cx - 45, mouth_y + 60)]
        draw.polygon(pts, fill=(180, 40, 50, 255), outline=STROKE_COLOR)
        # Upper teeth
        draw.rectangle([cx - 55, mouth_y - 10, cx + 55, mouth_y + 15], fill=(255, 255, 255, 255), outline=STROKE_COLOR, width=5)
        for tx in range(cx - 35, cx + 45, 22):
            draw.line([(tx, mouth_y - 10), (tx, mouth_y + 15)], fill=STROKE_COLOR, width=4)
        # Tongue
        draw.chord([cx - 35, mouth_y + 25, cx + 35, mouth_y + 60], start=0, end=180, fill=(240, 110, 130, 255))
    elif expression in ["shock", "terrified"]:
        # Wide open O mouth
        draw.ellipse([cx - 35, mouth_y - 20, cx + 35, mouth_y + 55],
                     fill=(140, 25, 35, 255), outline=STROKE_COLOR, width=8)
        # Quivering lower lip
        draw.arc([cx - 40, mouth_y + 60, cx + 40, mouth_y + 80], start=200, end=340, fill=STROKE_COLOR, width=6)
        
    out_path = os.path.join(OUTPUT_DIR, "triboulet", f"head_{expression}.png")
    return supersample_save(im, out_path)

def generate_triboulet_jester_cap():
    """
    Draws the three-horned Renaissance jester cap with golden bells and ermine trim.
    """
    w, h = 900, 650
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(im)
    
    cx, cy = w // 2, 450
    
    # Cap Horns (Yellow and Purple parti-colored)
    yellow = (245, 205, 50, 255)
    purple = (115, 45, 140, 255)
    gold_bell = (255, 225, 60, 255)
    
    # Center horn (arching upward-backward)
    center_horn = [
        (cx - 90, cy - 30),
        (cx - 60, cy - 240),
        (cx - 20, cy - 350),
        (cx + 20, cy - 350),
        (cx + 60, cy - 240),
        (cx + 90, cy - 30)
    ]
    draw.polygon(center_horn, fill=yellow, outline=STROKE_COLOR)
    # Split color line down center horn
    draw.line([(cx, cy - 30), (cx, cy - 350)], fill=STROKE_COLOR, width=STROKE_W)
    draw.polygon([(cx, cy - 30), (cx, cy - 350), (cx + 20, cy - 350), (cx + 60, cy - 240), (cx + 90, cy - 30)], fill=purple)
    
    # Left Horn (drooping out and down to the left)
    left_horn = [
        (cx - 120, cy - 10),
        (cx - 220, cy - 120),
        (cx - 360, cy - 150),
        (cx - 390, cy - 90),
        (cx - 340, cy - 30),
        (cx - 200, cy - 20),
        (cx - 100, cy + 30)
    ]
    draw.polygon(left_horn, fill=purple, outline=STROKE_COLOR)
    
    # Right Horn (drooping out and down to the right)
    right_horn = [
        (cx + 120, cy - 10),
        (cx + 220, cy - 120),
        (cx + 360, cy - 150),
        (cx + 390, cy - 90),
        (cx + 340, cy - 30),
        (cx + 200, cy - 20),
        (cx + 100, cy + 30)
    ]
    draw.polygon(right_horn, fill=yellow, outline=STROKE_COLOR)
    
    # Redraw bold outlines around horns
    draw.line(center_horn + [center_horn[0]], fill=STROKE_COLOR, width=STROKE_W)
    draw.line(left_horn + [left_horn[0]], fill=STROKE_COLOR, width=STROKE_W)
    draw.line(right_horn + [right_horn[0]], fill=STROKE_COLOR, width=STROKE_W)
    
    # Golden bells at horn tips
    def draw_bell(bx, by):
        r = 26
        draw.ellipse([bx - r, by - r, bx + r, by + r], fill=gold_bell, outline=STROKE_COLOR, width=STROKE_W)
        draw.line([(bx - r + 6, by + 4), (bx + r - 6, by + 4)], fill=STROKE_COLOR, width=6)
        draw.ellipse([bx - 6, by + 2, bx + 6, by + 14], fill=STROKE_COLOR)
        
    draw_bell(cx, cy - 360)         # Top bell
    draw_bell(cx - 380, cy - 90)     # Left bell
    draw_bell(cx + 380, cy - 90)     # Right bell
    
    # Cap headband/brow band
    band_pts = [
        (cx - 170, cy - 10),
        (cx + 170, cy - 10),
        (cx + 185, cy + 50),
        (cx - 185, cy + 50)
    ]
    draw.polygon(band_pts, fill=(240, 240, 245, 255), outline=STROKE_COLOR)
    draw.line(band_pts + [band_pts[0]], fill=STROKE_COLOR, width=STROKE_W)
    
    # Ermine black tails on headband
    for ex in [-120, -60, 0, 60, 120]:
        draw.polygon([(cx + ex, cy + 5), (cx + ex - 6, cy + 35), (cx + ex + 6, cy + 35)], fill=STROKE_COLOR)
        
    out_path = os.path.join(OUTPUT_DIR, "triboulet", "jester_cap.png")
    return supersample_save(im, out_path)

def generate_triboulet_torso():
    """Draws Triboulet's organic cartoon torso: parti-colored tunic with dagged collar and leather belt."""
    w, h = 600, 750
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(im)
    
    cx = w // 2
    top_y = 100
    bot_y = 620
    half_w = 150
    
    # Main Torso Body (bean / rounded rectangle)
    yellow = (245, 205, 50, 255)
    purple = (115, 45, 140, 255)
    
    # Left half: Yellow
    draw.rectangle([cx - half_w, top_y + 60, cx, bot_y], fill=yellow)
    # Right half: Purple
    draw.rectangle([cx, top_y + 60, cx + half_w, bot_y], fill=purple)
    
    # Central seam line
    draw.line([(cx, top_y + 60), (cx, bot_y)], fill=STROKE_COLOR, width=6)
    
    # Dagged pointed jester collar
    dag_pts = [
        (cx - half_w - 20, top_y),
        (cx - 110, top_y + 110),
        (cx - 50, top_y + 30),
        (cx, top_y + 120),
        (cx + 50, top_y + 30),
        (cx + 110, top_y + 110),
        (cx + half_w + 20, top_y),
        (cx + half_w + 20, top_y - 20),
        (cx - half_w - 20, top_y - 20)
    ]
    # Alternating dag colors
    draw.polygon([(cx - half_w - 20, top_y), (cx - 110, top_y + 110), (cx - 50, top_y + 30), (cx - 50, top_y)], fill=purple, outline=STROKE_COLOR)
    draw.polygon([(cx - 50, top_y + 30), (cx, top_y + 120), (cx, top_y)], fill=yellow, outline=STROKE_COLOR)
    draw.polygon([(cx, top_y + 120), (cx + 50, top_y + 30), (cx + 50, top_y)], fill=purple, outline=STROKE_COLOR)
    draw.polygon([(cx + 50, top_y + 30), (cx + 110, top_y + 110), (cx + half_w + 20, top_y), (cx + half_w + 20, top_y)], fill=yellow, outline=STROKE_COLOR)
    
    # Little gold bells on collar dags
    def mini_bell(bx, by):
        draw.ellipse([bx - 12, by - 12, bx + 12, by + 12], fill=(255, 225, 60, 255), outline=STROKE_COLOR, width=4)
    mini_bell(cx - 110, top_y + 110)
    mini_bell(cx, top_y + 120)
    mini_bell(cx + 110, top_y + 110)
    
    # Leather Belt with brass buckle
    belt_y = bot_y - 120
    draw.rectangle([cx - half_w - 5, belt_y, cx + half_w + 5, belt_y + 45], fill=(70, 42, 28, 255), outline=STROKE_COLOR, width=STROKE_W)
    # Brass buckle
    draw.rectangle([cx - 35, belt_y - 6, cx + 35, belt_y + 51], fill=(235, 190, 45, 255), outline=STROKE_COLOR, width=6)
    draw.rectangle([cx - 18, belt_y + 8, cx + 18, belt_y + 37], fill=(70, 42, 28, 255))
    draw.line([(cx, belt_y + 6), (cx, belt_y + 39)], fill=STROKE_COLOR, width=6)
    
    # Dagged skirt bottom
    skirt_y = bot_y
    draw.polygon([(cx - half_w, skirt_y), (cx - 100, skirt_y + 40), (cx - 50, skirt_y),
                  (cx, skirt_y + 45), (cx + 50, skirt_y), (cx + 100, skirt_y + 40), (cx + half_w, skirt_y)],
                 fill=yellow, outline=STROKE_COLOR)
                 
    # Outer bold contour
    contour = [
        (cx - half_w, top_y + 60),
        (cx + half_w, top_y + 60),
        (cx + half_w + 5, bot_y),
        (cx - half_w - 5, bot_y),
    ]
    draw.line(contour + [contour[0]], fill=STROKE_COLOR, width=STROKE_W)
    
    out_path = os.path.join(OUTPUT_DIR, "triboulet", "torso.png")
    return supersample_save(im, out_path)

def generate_triboulet_limbs():
    """Generates cartoon stick arms, legs, hands, and bell shoes."""
    char_dir = os.path.join(OUTPUT_DIR, "triboulet")
    
    # 1. Arm segment (bold organic rounded capsule)
    def make_segment(w, h, color, name):
        im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(im)
        pad = STROKE_W // 2 + 2
        draw.rounded_rectangle([pad, pad, w - pad, h - pad], radius=w//2, fill=color, outline=STROKE_COLOR, width=STROKE_W)
        supersample_save(im, os.path.join(char_dir, name))
        
    yellow = (245, 205, 50, 255)
    purple = (115, 45, 140, 255)
    
    make_segment(120, 240, yellow, "upper_arm_left.png")
    make_segment(100, 220, yellow, "lower_arm_left.png")
    make_segment(120, 240, purple, "upper_arm_right.png")
    make_segment(100, 220, purple, "lower_arm_right.png")
    
    # Legs (striped or solid)
    make_segment(130, 280, purple, "upper_leg_left.png")
    make_segment(110, 280, purple, "lower_leg_left.png")
    make_segment(130, 280, yellow, "upper_leg_right.png")
    make_segment(110, 280, yellow, "lower_leg_right.png")
    
    # 2. Hands (cute rounded cartoon fists and pointing hands)
    skin = (252, 248, 240, 255)
    # Open / relaxed hand
    im_hand = Image.new("RGBA", (180, 180), (0, 0, 0, 0))
    d_h = ImageDraw.Draw(im_hand)
    d_h.ellipse([30, 30, 150, 150], fill=skin, outline=STROKE_COLOR, width=STROKE_W)
    d_h.ellipse([20, 50, 70, 110], fill=skin, outline=STROKE_COLOR, width=STROKE_W)  # thumb
    supersample_save(im_hand, os.path.join(char_dir, "hand_open.png"))
    
    # Pointing hand
    im_point = Image.new("RGBA", (220, 180), (0, 0, 0, 0))
    d_p = ImageDraw.Draw(im_point)
    d_p.ellipse([40, 40, 140, 140], fill=skin, outline=STROKE_COLOR, width=STROKE_W)
    # Pointing finger
    d_p.rounded_rectangle([110, 60, 200, 105], radius=20, fill=skin, outline=STROKE_COLOR, width=STROKE_W)
    # Thumb
    d_p.ellipse([40, 30, 85, 90], fill=skin, outline=STROKE_COLOR, width=STROKE_W)
    supersample_save(im_point, os.path.join(char_dir, "hand_point.png"))
    
    # 3. Curled Jester Shoes with golden bells
    for side, col in [("left", purple), ("right", yellow)]:
        im_shoe = Image.new("RGBA", (260, 180), (0, 0, 0, 0))
        d_s = ImageDraw.Draw(im_shoe)
        shoe_pts = [
            (30, 50),
            (110, 50),
            (140, 100),
            (210, 90),
            (240, 60),   # curled toe
            (235, 120),
            (40, 130),
            (25, 90)
        ]
        if side == "left":
            # flip horizontal
            shoe_pts = [(260 - x, y) for (x, y) in shoe_pts]
            
        d_s.polygon(shoe_pts, fill=col, outline=STROKE_COLOR)
        d_s.line(shoe_pts + [shoe_pts[0]], fill=STROKE_COLOR, width=STROKE_W)
        
        # Golden bell on toe
        bell_x = 240 if side != "left" else 20
        d_s.ellipse([bell_x - 16, 44, bell_x + 16, 76], fill=(255, 225, 60, 255), outline=STROKE_COLOR, width=6)
        supersample_save(im_shoe, os.path.join(char_dir, f"foot_{side}.png"))

# =============================================================================
# 2. KING FRANCIS I (THE RENAISSANCE MONARCH)
# =============================================================================

def generate_king_head(expression="furious"):
    """
    Draws King Francis I: iconic pointed black beard, dark mustache, heavy brows,
    expressive royal eyes. Expressions: regal, furious, amused_laugh
    """
    w, h = 600, 650
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(im)
    
    cx, cy = w // 2, 280
    radius = 175
    
    # 1. Head Base
    skin_fill = (250, 242, 235, 255)
    draw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius],
                 fill=skin_fill, outline=STROKE_COLOR, width=STROKE_W)
                 
    # 2. Pointed Renaissance Beard
    beard_col = (25, 22, 28, 255)
    beard_pts = [
        (cx - 100, cy + 90),
        (cx - 50, cy + 180),
        (cx, cy + 300),        # long pointed beard tip
        (cx + 50, cy + 180),
        (cx + 100, cy + 90)
    ]
    draw.polygon(beard_pts, fill=beard_col, outline=STROKE_COLOR)
    draw.line(beard_pts + [beard_pts[0]], fill=STROKE_COLOR, width=STROKE_W)
    
    # 3. Renaissance Handlebar Mustache
    mustache_pts = [
        (cx, cy + 70),
        (cx - 60, cy + 45),
        (cx - 110, cy + 85),
        (cx - 50, cy + 95),
        (cx, cy + 82),
        (cx + 50, cy + 95),
        (cx + 110, cy + 85),
        (cx + 60, cy + 45)
    ]
    draw.polygon(mustache_pts, fill=beard_col, outline=STROKE_COLOR)
    draw.line(mustache_pts + [mustache_pts[0]], fill=STROKE_COLOR, width=6)
    
    # 4. Eyes & Eyebrows based on expression
    eye_y = cy - 25
    eye_spacing = 70
    eye_r = 28
    
    if expression == "furious":
        # Fierce, slanted angry eyes
        draw.ellipse([cx - eye_spacing - eye_r, eye_y - eye_r, cx - eye_spacing + eye_r, eye_y + eye_r],
                     fill=(255, 255, 255, 255), outline=STROKE_COLOR, width=7)
        draw.ellipse([cx + eye_spacing - eye_r, eye_y - eye_r, cx + eye_spacing + eye_r, eye_y + eye_r],
                     fill=(255, 255, 255, 255), outline=STROKE_COLOR, width=7)
        # Small intense pupils glaring down-left at Triboulet
        draw.ellipse([cx - eye_spacing - 18, eye_y - 8, cx - eye_spacing + 2, eye_y + 12], fill=STROKE_COLOR)
        draw.ellipse([cx + eye_spacing - 18, eye_y - 8, cx + eye_spacing + 2, eye_y + 12], fill=STROKE_COLOR)
        
        # Heavy slanted angry eyebrows
        draw.polygon([(cx - eye_spacing - 45, eye_y - 45), (cx - 10, eye_y - 15), (cx - eye_spacing - 40, eye_y - 65)], fill=beard_col)
        draw.polygon([(cx + eye_spacing + 45, eye_y - 45), (cx + 10, eye_y - 15), (cx + eye_spacing + 40, eye_y - 65)], fill=beard_col)
        
        # Red vein / angry steam cue on temple
        vx, vy = cx - radius + 40, cy - 80
        draw.line([(vx, vy), (vx + 25, vy - 15)], fill=(220, 40, 40, 255), width=6)
        draw.line([(vx + 12, vy - 7), (vx + 12, vy - 25)], fill=(220, 40, 40, 255), width=6)
        draw.line([(vx + 12, vy - 7), (vx + 30, vy + 5)], fill=(220, 40, 40, 255), width=6)
        
    elif expression == "amused_laugh":
        # Closed crescent laughing eyes
        draw.arc([cx - eye_spacing - 35, eye_y - 25, cx - eye_spacing + 35, eye_y + 25], start=200, end=340, fill=STROKE_COLOR, width=9)
        draw.arc([cx + eye_spacing - 35, eye_y - 25, cx + eye_spacing + 35, eye_y + 25], start=200, end=340, fill=STROKE_COLOR, width=9)
        # Raised happy eyebrows
        draw.arc([cx - eye_spacing - 40, eye_y - 65, cx - eye_spacing + 40, eye_y - 35], start=200, end=340, fill=beard_col, width=10)
        draw.arc([cx + eye_spacing - 40, eye_y - 65, cx + eye_spacing + 40, eye_y - 35], start=200, end=340, fill=beard_col, width=10)
        
        # Open mouth laughing beneath mustache
        draw.chord([cx - 45, cy + 95, cx + 45, cy + 160], start=0, end=180, fill=(160, 30, 40, 255), outline=STROKE_COLOR, width=6)
        
    elif expression == "regal":
        # Dignified, calm sovereign eyes
        draw.ellipse([cx - eye_spacing - eye_r, eye_y - eye_r, cx - eye_spacing + eye_r, eye_y + eye_r],
                     fill=(255, 255, 255, 255), outline=STROKE_COLOR, width=6)
        draw.ellipse([cx + eye_spacing - eye_r, eye_y - eye_r, cx + eye_spacing + eye_r, eye_y + eye_r],
                     fill=(255, 255, 255, 255), outline=STROKE_COLOR, width=6)
        draw.ellipse([cx - eye_spacing - 8, eye_y - 8, cx - eye_spacing + 12, eye_y + 12], fill=STROKE_COLOR)
        draw.ellipse([cx + eye_spacing - 8, eye_y - 8, cx + eye_spacing + 12, eye_y + 12], fill=STROKE_COLOR)
        # Regal straight brows
        draw.line([(cx - eye_spacing - 40, eye_y - 45), (cx - 15, eye_y - 40)], fill=beard_col, width=10)
        draw.line([(cx + 15, eye_y - 40), (cx + eye_spacing + 40, eye_y - 45)], fill=beard_col, width=10)
        
    # Long aristocratic French nose
    draw.line([(cx, eye_y - 10), (cx - 12, eye_y + 35)], fill=STROKE_COLOR, width=7)
    draw.line([(cx - 12, eye_y + 35), (cx + 12, eye_y + 40)], fill=STROKE_COLOR, width=7)
    
    out_path = os.path.join(OUTPUT_DIR, "king_francis", f"head_{expression}.png")
    return supersample_save(im, out_path)

def generate_king_crown():
    """Draws the royal French gold crown with fleur-de-lis peaks and ruby gems."""
    w, h = 600, 350
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(im)
    
    cx, cy = w // 2, 220
    crown_w = 210
    
    gold_fill = (250, 205, 45, 255)
    
    # Crown points (5 peaks: tall center fleur-de-lis, 2 medium, 2 side)
    crown_pts = [
        (cx - crown_w, cy),
        (cx - crown_w - 15, cy - 80),
        (cx - 130, cy - 40),
        (cx - 80, cy - 120),
        (cx - 30, cy - 50),
        (cx, cy - 160),                # Tall central Fleur-de-lis peak
        (cx + 30, cy - 50),
        (cx + 80, cy - 120),
        (cx + 130, cy - 40),
        (cx + crown_w + 15, cy - 80),
        (cx + crown_w, cy),
        (cx + crown_w - 10, cy + 50),
        (cx - crown_w + 10, cy + 50)
    ]
    draw.polygon(crown_pts, fill=gold_fill, outline=STROKE_COLOR)
    draw.line(crown_pts + [crown_pts[0]], fill=STROKE_COLOR, width=STROKE_W)
    
    # Velvet cap inside crown
    draw.arc([cx - crown_w + 30, cy - 110, cx + crown_w - 30, cy + 40], start=180, end=360, fill=(140, 20, 35, 255), width=24)
    
    # Jewels on crown band (rubies, sapphires, emeralds)
    jewel_colors = [(220, 30, 40, 255), (30, 80, 200, 255), (30, 180, 70, 255), (220, 30, 40, 255)]
    for idx, jx in enumerate(range(cx - crown_w + 50, cx + crown_w - 30, 75)):
        col = jewel_colors[idx % len(jewel_colors)]
        draw.ellipse([jx - 14, cy + 10, jx + 14, cy + 38], fill=col, outline=STROKE_COLOR, width=5)
        
    out_path = os.path.join(OUTPUT_DIR, "king_francis", "royal_crown.png")
    return supersample_save(im, out_path)

def generate_king_torso():
    """Draws King Francis I's massive royal doublet with broad ermine fur collar and golden chain."""
    w, h = 800, 800
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(im)
    
    cx = w // 2
    top_y = 120
    bot_y = 700
    half_w = 220
    
    # Crimson velvet doublet body
    velvet_red = (165, 25, 40, 255)
    draw.rectangle([cx - half_w, top_y + 120, cx + half_w, bot_y], fill=velvet_red, outline=STROKE_COLOR, width=STROKE_W)
    
    # Golden buttons down center placket
    draw.rectangle([cx - 25, top_y + 120, cx + 25, bot_y], fill=(225, 180, 40, 255), outline=STROKE_COLOR, width=6)
    for by in range(top_y + 160, bot_y - 40, 70):
        draw.ellipse([cx - 14, by - 14, cx + 14, by + 14], fill=(70, 45, 15, 255), outline=STROKE_COLOR, width=4)
        
    # Massive broad White Ermine Fur Collar (Renaissance royal cape collar)
    ermine_white = (245, 245, 250, 255)
    collar_pts = [
        (cx - half_w - 50, top_y + 30),
        (cx - 80, top_y),
        (cx, top_y + 60),
        (cx + 80, top_y),
        (cx + half_w + 50, top_y + 30),
        (cx + half_w + 30, top_y + 190),
        (cx + 100, top_y + 240),
        (cx, top_y + 260),
        (cx - 100, top_y + 240),
        (cx - half_w - 30, top_y + 190)
    ]
    draw.polygon(collar_pts, fill=ermine_white, outline=STROKE_COLOR)
    draw.line(collar_pts + [collar_pts[0]], fill=STROKE_COLOR, width=STROKE_W)
    
    # Black ermine tails dotted across fur
    tails = [
        (cx - 180, top_y + 120),
        (cx - 120, top_y + 160),
        (cx - 50, top_y + 190),
        (cx + 50, top_y + 190),
        (cx + 120, top_y + 160),
        (cx + 180, top_y + 120),
    ]
    for tx, ty in tails:
        draw.polygon([(tx, ty), (tx - 8, ty + 28), (tx + 8, ty + 28)], fill=STROKE_COLOR)
        draw.line([(tx, ty + 28), (tx, ty + 42)], fill=STROKE_COLOR, width=4)
        
    # Heavy Gold Chain of the Order of Saint Michael
    draw.arc([cx - 140, top_y + 120, cx + 140, top_y + 350], start=10, end=170, fill=(245, 210, 50, 255), width=20)
    # Saint Michael Medallion
    draw.ellipse([cx - 35, top_y + 330, cx + 35, top_y + 400], fill=(255, 225, 60, 255), outline=STROKE_COLOR, width=6)
    
    out_path = os.path.join(OUTPUT_DIR, "king_francis", "torso.png")
    return supersample_save(im, out_path)

def generate_king_limbs():
    """Draws King Francis I's puffed crimson velvet sleeves and gesturing hands."""
    char_dir = os.path.join(OUTPUT_DIR, "king_francis")
    
    # Puffed velvet sleeve (wide Renaissance upper arm)
    im_up = Image.new("RGBA", (220, 280), (0, 0, 0, 0))
    d_u = ImageDraw.Draw(im_up)
    d_u.ellipse([20, 20, 200, 260], fill=(165, 25, 40, 255), outline=STROKE_COLOR, width=STROKE_W)
    # Gold slashes across puff sleeve
    for sy in range(60, 220, 45):
        d_u.polygon([(70, sy), (150, sy), (135, sy + 25), (55, sy + 25)], fill=(245, 210, 50, 255))
    supersample_save(im_up, os.path.join(char_dir, "upper_arm_left.png"))
    supersample_save(im_up, os.path.join(char_dir, "upper_arm_right.png"))
    
    # Forearm with white lace cuff
    im_low = Image.new("RGBA", (150, 260), (0, 0, 0, 0))
    d_l = ImageDraw.Draw(im_low)
    d_l.rounded_rectangle([25, 20, 125, 220], radius=40, fill=(165, 25, 40, 255), outline=STROKE_COLOR, width=STROKE_W)
    # White lace cuff at wrist
    d_l.rectangle([15, 180, 135, 240], fill=(250, 250, 255, 255), outline=STROKE_COLOR, width=6)
    supersample_save(im_low, os.path.join(char_dir, "lower_arm_left.png"))
    supersample_save(im_low, os.path.join(char_dir, "lower_arm_right.png"))
    
    # Hands (one pointing authority, one gripping throne)
    skin = (250, 242, 235, 255)
    im_point = Image.new("RGBA", (220, 180), (0, 0, 0, 0))
    d_p = ImageDraw.Draw(im_point)
    d_p.ellipse([30, 30, 130, 130], fill=skin, outline=STROKE_COLOR, width=STROKE_W)
    d_p.rounded_rectangle([110, 50, 200, 95], radius=20, fill=skin, outline=STROKE_COLOR, width=STROKE_W)
    supersample_save(im_point, os.path.join(char_dir, "hand_left.png"))
    
    im_grip = Image.new("RGBA", (180, 180), (0, 0, 0, 0))
    d_g = ImageDraw.Draw(im_grip)
    d_g.ellipse([30, 30, 150, 150], fill=skin, outline=STROKE_COLOR, width=STROKE_W)
    # Gold signet ring on finger
    d_g.ellipse([90, 70, 130, 110], fill=(245, 210, 50, 255), outline=STROKE_COLOR, width=5)
    supersample_save(im_grip, os.path.join(char_dir, "hand_right.png"))

if __name__ == "__main__":
    print("[*] Generating reference-accurate V2 cartoon character parts...")
    for expr in ["neutral", "smirk", "laugh", "shock", "terrified"]:
        generate_triboulet_head(expr)
    generate_triboulet_jester_cap()
    generate_triboulet_torso()
    generate_triboulet_limbs()
    print("[+] Triboulet V2 parts generated.")
    
    for expr in ["regal", "furious", "amused_laugh"]:
        generate_king_head(expr)
    generate_king_crown()
    generate_king_torso()
    generate_king_limbs()
    print("[+] King Francis I V2 parts generated.")
    print("[+] All reference-accurate V2 character assets ready!")
