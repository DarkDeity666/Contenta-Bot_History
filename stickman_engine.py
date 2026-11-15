import math
import random
from typing import Dict, Any, List, Optional
from PIL import Image, ImageDraw
import imageio_ffmpeg
from config import VIDEO_WIDTH, VIDEO_HEIGHT, FPS

# Aesthetic Palette
BG_PAPER = (248, 244, 235)         # Clean sketch paper
INK = (25, 25, 28)                 # Hand-drawn ink line
ROYAL_GOLD = (235, 185, 35)        # Crowns, medals, gavels
CRIMSON = (215, 45, 45)            # Blood, danger, banners
WOOD_BROWN = (125, 75, 40)         # Ships, desks, barrels, gavels
BRICK_RED = (175, 65, 55)          # Victorian buildings
BEER_AMBER = (195, 125, 25)        # Beer & Molasses tidal waves
WATER_BLUE = (50, 130, 200)        # Ocean waves
STONE_GRAY = (190, 185, 175)       # Castle stone & dungeons

# ====================================================================
# 1. CORE ARTICULATED 2D STICKMAN WITH MULTI-POSE PHYSICS
# ====================================================================
def draw_stickman(
    draw: ImageDraw.ImageDraw,
    x: float,
    y: float,
    action: str = "walk",      # walk, run, panic, talk, sword_strike, gavel_slam, dead, dance, drive, cheer
    emotion: str = "normal",   # normal, shock, angry, panic, dead, smug, laughing
    facing: int = 1,           # 1 = right, -1 = left
    scale: float = 1.0,
    t: float = 0.0,
    hat: Optional[str] = None, # 'crown', 'pope_hat', 'tophat', 'pirate_hat', 'helm', None
    prop: Optional[str] = None # 'sword', 'gavel', 'mug', 'cutlass', 'bucket', None
):
    """
    Draws an expressive, live articulated stickman with joints, physics, and emotion.
    """
    head_r = int(36 * scale)
    torso_len = int(115 * scale)
    arm_len = int(65 * scale)
    leg_len = int(80 * scale)
    line_w = max(4, int(6.5 * scale))

    head_cx = int(x)
    head_cy = int(y - torso_len - head_r)
    neck = (head_cx, int(y - torso_len))
    hip = (head_cx, int(y))

    body_tilt = 0.0
    mouth_open = 0.0
    l_arm_angle, r_arm_angle = 0.4, -0.4
    l_leg_angle, r_leg_angle = 0.0, 0.0

    if action == "walk":
        cycle = math.sin(t * 7.5)
        l_leg_angle = cycle * 0.45
        r_leg_angle = -cycle * 0.45
        l_arm_angle = -cycle * 0.5
        r_arm_angle = cycle * 0.5
        mouth_open = max(0.0, math.sin(t * 11.0) * 0.5)
        head_cy += int(abs(cycle) * 6 * scale)
        hip = (hip[0], int(hip[1] + abs(cycle) * 6 * scale))

    elif action == "run":
        cycle = math.sin(t * 15.0)
        body_tilt = 0.3 * facing
        l_leg_angle = cycle * 0.85
        r_leg_angle = -cycle * 0.85
        l_arm_angle = -cycle * 0.95
        r_arm_angle = cycle * 0.95
        head_cy += int(abs(cycle) * 12 * scale)

    elif action == "panic":
        cycle = math.sin(t * 22.0)
        body_tilt = cycle * 0.12
        l_arm_angle = -2.2 + math.sin(t * 24.0) * 0.6
        r_arm_angle = 2.2 + math.cos(t * 24.0) * 0.6
        l_leg_angle = math.sin(t * 16.0) * 0.7
        r_leg_angle = -math.sin(t * 16.0) * 0.7
        mouth_open = 0.85
        head_cy += int(cycle * 10 * scale)

    elif action == "dance":
        cycle = math.sin(t * 12.0)
        body_tilt = cycle * 0.25
        l_arm_angle = -1.8 + math.sin(t * 10.0) * 0.8
        r_arm_angle = 1.8 - math.cos(t * 10.0) * 0.8
        l_leg_angle = math.sin(t * 12.0) * 0.6
        r_leg_angle = -math.sin(t * 12.0) * 0.6
        head_cy += int(abs(cycle) * 15 * scale)
        hip = (hip[0], int(hip[1] - abs(cycle) * 10 * scale))
        mouth_open = 0.6

    elif action == "sword_strike":
        strike = math.sin(t * 7.0)
        r_arm_angle = -1.3 + strike * 1.6 * facing
        l_arm_angle = 0.6 * facing
        l_leg_angle = -0.4 * facing
        r_leg_angle = 0.6 * facing

    elif action == "gavel_slam":
        slam = max(0.0, math.sin(t * 8.5))
        r_arm_angle = -2.1 + slam * 2.3 * facing
        l_arm_angle = 0.5 * facing

    elif action == "talk":
        mouth_open = abs(math.sin(t * 9.0))
        r_arm_angle = -0.8 + math.sin(t * 4.0) * 0.4 * facing
        l_arm_angle = 0.4 * facing
        body_tilt = math.sin(t * 3.0) * 0.05

    elif action == "cheer":
        cycle = math.sin(t * 10.0)
        l_arm_angle = -2.4 + cycle * 0.3
        r_arm_angle = 2.4 - cycle * 0.3
        mouth_open = 0.8
        head_cy += int(abs(cycle) * 10 * scale)

    elif action == "dead":
        body_tilt = 1.4 * facing
        l_arm_angle, r_arm_angle = 1.0, 0.8
        l_leg_angle, r_leg_angle = 0.2, 0.4
        emotion = "dead"

    # --- Torso ---
    neck_x = neck[0] + int(body_tilt * 40)
    neck = (neck_x, neck[1])
    head_cx += int(body_tilt * 50)
    draw.line([neck, hip], fill=INK, width=line_w)

    # --- Legs ---
    for leg_angle, side in [(l_leg_angle, -1), (r_leg_angle, 1)]:
        knee_x = hip[0] + int(math.sin(leg_angle) * leg_len * 0.5)
        knee_y = hip[1] + int(math.cos(leg_angle) * leg_len * 0.5)
        foot_x = knee_x + int(math.sin(leg_angle * 0.7) * leg_len * 0.5)
        foot_y = knee_y + int(math.cos(leg_angle * 0.7) * leg_len * 0.5)
        draw.line([hip, (knee_x, knee_y)], fill=INK, width=line_w)
        draw.line([(knee_x, knee_y), (foot_x, foot_y)], fill=INK, width=line_w)

    # --- Arms ---
    shoulder = (neck[0], neck[1] + int(14 * scale))
    hand_r_pos = None

    for arm_angle, side in [(l_arm_angle, -1), (r_arm_angle, 1)]:
        elbow_x = shoulder[0] + int(math.sin(arm_angle) * arm_len * 0.55 * facing)
        elbow_y = shoulder[1] + int(math.cos(arm_angle) * arm_len * 0.55)
        hand_x = elbow_x + int(math.sin(arm_angle + 0.3 * side) * arm_len * 0.55 * facing)
        hand_y = elbow_y + int(math.cos(arm_angle + 0.3 * side) * arm_len * 0.55)
        draw.line([shoulder, (elbow_x, elbow_y)], fill=INK, width=line_w)
        draw.line([(elbow_x, elbow_y), (hand_x, hand_y)], fill=INK, width=line_w)
        if side == 1:
            hand_r_pos = (hand_x, hand_y)

    # --- Head ---
    draw.ellipse([head_cx - head_r, head_cy - head_r, head_cx + head_r, head_cy + head_r], fill=(255, 255, 255), outline=INK, width=line_w)

    # --- Face Expression ---
    eye_offset_x = int(10 * scale * facing)
    eye_y = head_cy - int(6 * scale)
    eye_r = int(5 * scale)

    if emotion == "dead":
        for ex in [head_cx - 14 * scale + eye_offset_x, head_cx + 14 * scale + eye_offset_x]:
            draw.line([(ex - 6, eye_y - 6), (ex + 6, eye_y + 6)], fill=INK, width=3)
            draw.line([(ex + 6, eye_y - 6), (ex - 6, eye_y + 6)], fill=INK, width=3)
        draw.arc([head_cx - 15, head_cy + 10, head_cx + 15, head_cy + 25], 190, 350, fill=INK, width=4)

    elif emotion == "shock":
        big_eye_r = int(11 * scale)
        draw.ellipse([head_cx - 16 + eye_offset_x - big_eye_r, eye_y - big_eye_r, head_cx - 16 + eye_offset_x + big_eye_r, eye_y + big_eye_r], fill=(255, 255, 255), outline=INK, width=3)
        draw.ellipse([head_cx + 16 + eye_offset_x - big_eye_r, eye_y - big_eye_r, head_cx + 16 + eye_offset_x + big_eye_r, eye_y + big_eye_r], fill=(255, 255, 255), outline=INK, width=3)
        draw.ellipse([head_cx - 16 + eye_offset_x - 3, eye_y - 3, head_cx - 16 + eye_offset_x + 3, eye_y + 3], fill=INK)
        draw.ellipse([head_cx + 16 + eye_offset_x - 3, eye_y - 3, head_cx + 16 + eye_offset_x + 3, eye_y + 3], fill=INK)
        draw.ellipse([head_cx - 10 + eye_offset_x, head_cy + 10, head_cx + 10 + eye_offset_x, head_cy + 28], fill=(180, 30, 30), outline=INK, width=3)

    elif emotion == "panic":
        draw.ellipse([head_cx - 13 + eye_offset_x, eye_y - eye_r, head_cx - 3 + eye_offset_x, eye_y + eye_r], fill=INK)
        draw.ellipse([head_cx + 3 + eye_offset_x, eye_y - eye_r, head_cx + 13 + eye_offset_x, eye_y + eye_r], fill=INK)
        draw.ellipse([head_cx - 12, head_cy + 8, head_cx + 12, head_cy + 24], fill=(160, 20, 20), outline=INK, width=3)
        sw_x = head_cx - int(30 * scale * facing)
        sw_y = head_cy - int(24 * scale)
        draw.ellipse([sw_x - 5, sw_y - 5, sw_x + 5, sw_y + 5], fill=(60, 160, 250))

    else:  # normal / talking / laughing
        draw.ellipse([head_cx - 13 + eye_offset_x, eye_y - eye_r, head_cx - 3 + eye_offset_x, eye_y + eye_r], fill=INK)
        draw.ellipse([head_cx + 3 + eye_offset_x, eye_y - eye_r, head_cx + 13 + eye_offset_x, eye_y + eye_r], fill=INK)
        if mouth_open > 0.2:
            mh = int(14 * scale * mouth_open)
            draw.chord([head_cx - 11 + eye_offset_x, head_cy + 8, head_cx + 11 + eye_offset_x, head_cy + 8 + mh], 0, 180, fill=(140, 20, 20), outline=INK, width=3)
        else:
            draw.line([(head_cx - 8 + eye_offset_x, head_cy + 13), (head_cx + 8 + eye_offset_x, head_cy + 13)], fill=INK, width=3)

    # --- Hats & Costumes ---
    if hat == "crown":
        cx, cy = head_cx, head_cy - head_r
        pts = [(cx - 26, cy), (cx - 30, cy - 32), (cx - 10, cy - 16), (cx, cy - 38), (cx + 10, cy - 16), (cx + 30, cy - 32), (cx + 26, cy)]
        draw.polygon(pts, fill=ROYAL_GOLD, outline=INK, width=3)
    elif hat == "pope_hat":
        cx, cy = head_cx, head_cy - head_r
        pts = [(cx - 22, cy), (cx - 18, cy - 50), (cx, cy - 66), (cx + 18, cy - 50), (cx + 22, cy)]
        draw.polygon(pts, fill=(245, 245, 245), outline=INK, width=3)
        draw.line([(cx, cy - 50), (cx, cy - 14)], fill=ROYAL_GOLD, width=4)
        draw.line([(cx - 10, cy - 32), (cx + 10, cy - 32)], fill=ROYAL_GOLD, width=4)
    elif hat == "tophat":
        cx, cy = head_cx, head_cy - head_r
        draw.line([(cx - 35, cy), (cx + 35, cy)], fill=INK, width=6)
        draw.rectangle([cx - 22, cy - 50, cx + 22, cy], fill=(35, 35, 40), outline=INK, width=3)
        draw.line([(cx - 22, cy - 10), (cx + 22, cy - 10)], fill=CRIMSON, width=4)
    elif hat == "pirate_hat":
        cx, cy = head_cx, head_cy - head_r
        pts = [(cx - 40, cy), (cx - 25, cy - 35), (cx, cy - 25), (cx + 25, cy - 35), (cx + 40, cy)]
        draw.polygon(pts, fill=(30, 30, 35), outline=INK, width=3)
        draw.ellipse([cx - 5, cy - 18, cx + 5, cy - 8], fill=(255, 255, 255))
    elif hat == "helm":
        cx, cy = head_cx, head_cy - head_r
        draw.arc([cx - 38, cy - 20, cx + 38, cy + 40], 180, 360, fill=STONE_GRAY, width=10)
        draw.line([(cx, cy - 20), (cx, cy + 20)], fill=ROYAL_GOLD, width=4)

    # --- Props in Hand ---
    if hand_r_pos and prop:
        hx, hy = hand_r_pos
        if prop in ["sword", "cutlass"]:
            tip_x = hx + int(70 * scale * facing)
            tip_y = hy - int(60 * scale)
            draw.line([(hx, hy), (tip_x, tip_y)], fill=(210, 220, 235), width=int(8 * scale))
            draw.line([(hx, hy), (tip_x, tip_y)], fill=INK, width=2)
            draw.line([(hx - 10, hy - 10), (hx + 10, hy + 10)], fill=ROYAL_GOLD, width=6)
        elif prop == "gavel":
            gx, gy = hx + int(40 * scale * facing), hy - int(30 * scale)
            draw.line([(hx, hy), (gx, gy)], fill=WOOD_BROWN, width=6)
            draw.line([(gx - 15, gy + 15), (gx + 15, gy - 15)], fill=WOOD_BROWN, width=14)
        elif prop == "bucket":
            draw.polygon([(hx - 20, hy), (hx + 20, hy), (hx + 15, hy + 35), (hx - 15, hy + 35)], fill=WOOD_BROWN, outline=INK, width=3)
            draw.arc([hx - 18, hy - 15, hx + 18, hy + 5], 180, 360, fill=INK, width=3)
        elif prop == "mug":
            draw.rectangle([hx, hy - 25, hx + 30, hy], fill=(220, 220, 220), outline=INK, width=3)
            draw.ellipse([hx + 5, hy - 32, hx + 25, hy - 22], fill=BEER_AMBER)


# ====================================================================
# 2. STORY-SPECIFIC ANIMATED BACKGROUNDS & SCENERY
# ====================================================================

def draw_setting_victorian_disaster(draw: ImageDraw.ImageDraw, t: float, p: float):
    """
    Victorian London / Boston: Brick brewery buildings, cobblestones, gas lamps.
    INTERACTION: Giant vat rupturing, unleashing a tsunami beer/molasses wave!
    """
    floor_y = 1380
    # 1. Victorian Brick Buildings in background
    for idx, (bx, bw, bh) in enumerate([(40, 300, 750), (360, 380, 850), (760, 280, 700)]):
        draw.rectangle([bx, floor_y - bh, bx + bw, floor_y], fill=BRICK_RED, outline=INK, width=5)
        # Windows
        for wy in range(floor_y - bh + 60, floor_y - 100, 110):
            for wx in range(bx + 40, bx + bw - 40, 80):
                draw.rectangle([wx, wy, wx + 45, wy + 70], fill=(255, 240, 190), outline=INK, width=3)
                draw.line([(wx + 22, wy), (wx + 22, wy + 70)], fill=INK, width=2)
                draw.line([(wx, wy + 35), (wx + 45, wy + 35)], fill=INK, width=2)
        # Chimney smoke puffs
        cx = bx + 60
        for smk in range(3):
            sy = floor_y - bh - 40 - smk * 35 - int((t * 40) % 50)
            sx = cx + int(math.sin(t * 3.0 + smk) * 20)
            draw.ellipse([sx - 15, sy - 15, sx + 15, sy + 15], fill=(220, 220, 220))

    # Cobblestone ground
    draw.line([(0, floor_y), (VIDEO_WIDTH, floor_y)], fill=INK, width=6)
    for c in range(0, VIDEO_WIDTH, 45):
        draw.line([(c, floor_y + 10), (c + 30, floor_y + 10)], fill=(160, 155, 145), width=3)

    # Gas Street Lamp
    draw.line([(180, floor_y), (180, floor_y - 280)], fill=INK, width=8)
    draw.polygon([(160, floor_y - 280), (200, floor_y - 280), (190, floor_y - 330), (170, floor_y - 330)], fill=(255, 235, 120), outline=INK, width=4)

    # Giant Ruptured Brewery Vat (on the left)
    vat_w = 420
    draw.rounded_rectangle([-120, floor_y - 500, vat_w, floor_y], radius=30, fill=WOOD_BROWN, outline=INK, width=7)
    # Iron hoops on vat
    for vy in [floor_y - 420, floor_y - 280, floor_y - 140]:
        draw.line([(-120, vy), (vat_w, vy)], fill=(60, 60, 65), width=10)

    # Dynamic ruptured crack with amber liquid bursting!
    if p > 0.25:
        draw.line([(180, floor_y - 420), (220, floor_y - 250), (190, floor_y - 100)], fill=(255, 240, 120), width=8)
        # Tsunami Wave rushing across screen!
        wave_front = int((p - 0.25) * 1.6 * VIDEO_WIDTH)
        wave_pts = [(0, floor_y + 400), (0, floor_y - 280)]
        for wx in range(0, min(VIDEO_WIDTH, wave_front), 30):
            wy = floor_y - 260 + int(math.sin(wx * 0.02 + t * 8.0) * 45)
            wave_pts.append((wx, wy))
        # Wave crest curling
        if wave_front > 0:
            wave_pts.append((min(VIDEO_WIDTH, wave_front), floor_y + 400))
            draw.polygon(wave_pts, fill=BEER_AMBER, outline=(140, 80, 10), width=6)
            # Foaming bubbles on crest
            for b in range(12):
                bx = wave_front - b * 35
                by = floor_y - 270 + int(math.sin(b + t * 6) * 30)
                draw.ellipse([bx - 12, by - 12, bx + 12, by + 12], fill=(255, 250, 230), outline=(130, 75, 10), width=2)


def draw_setting_medieval_castle(draw: ImageDraw.ImageDraw, t: float, p: float):
    """
    Medieval Italy / Castle Walls: Battlement stone towers, torches, city well.
    INTERACTION: Knights clashing, stealing bucket from the well, torches flickering!
    """
    floor_y = 1380
    # Stone Castle Towers
    for tx in [0, VIDEO_WIDTH - 280]:
        draw.rectangle([tx, floor_y - 650, tx + 280, floor_y], fill=STONE_GRAY, outline=INK, width=6)
        # Battlements (crenels)
        for cx in range(tx, tx + 280, 70):
            draw.rectangle([cx, floor_y - 700, cx + 45, floor_y - 650], fill=STONE_GRAY, outline=INK, width=4)
        # Arrow slits
        draw.rectangle([tx + 120, floor_y - 450, tx + 140, floor_y - 350], fill=(40, 40, 45), outline=INK, width=3)

    # Castle wall curtain in center
    draw.rectangle([280, floor_y - 420, VIDEO_WIDTH - 280, floor_y], fill=(175, 170, 160), outline=INK, width=5)

    # Flickering Wall Torches
    for torch_x in [340, VIDEO_WIDTH - 340]:
        draw.line([(torch_x, floor_y - 300), (torch_x + 20, floor_y - 340)], fill=WOOD_BROWN, width=8)
        # Animated fire
        flicker = math.sin(t * 18.0 + torch_x) * 6
        draw.ellipse([torch_x + 12 + flicker, floor_y - 370, torch_x + 32 + flicker, floor_y - 340], fill=ROYAL_GOLD)
        draw.ellipse([torch_x + 16, floor_y - 365, torch_x + 28, floor_y - 345], fill=CRIMSON)

    # Floor line
    draw.line([(0, floor_y), (VIDEO_WIDTH, floor_y)], fill=INK, width=6)

    # The Legendary City Well (Centerpiece of the War of the Bucket!)
    well_x = VIDEO_WIDTH // 2 - 120
    draw.rectangle([well_x, floor_y - 140, well_x + 240, floor_y], fill=STONE_GRAY, outline=INK, width=5)
    # Well roof posts
    draw.line([(well_x + 20, floor_y - 140), (well_x + 20, floor_y - 280)], fill=WOOD_BROWN, width=6)
    draw.line([(well_x + 220, floor_y - 140), (well_x + 220, floor_y - 280)], fill=WOOD_BROWN, width=6)
    draw.polygon([(well_x, floor_y - 280), (well_x + 120, floor_y - 360), (well_x + 240, floor_y - 280)], fill=WOOD_BROWN, outline=INK, width=4)
    # Hanging bucket rope
    draw.line([(well_x + 120, floor_y - 280), (well_x + 120, floor_y - 200)], fill=(70, 50, 30), width=4)


def draw_setting_courtroom(draw: ImageDraw.ImageDraw, t: float, p: float):
    """
    Gothic Vatican Basilica / Courtroom: Stone arches, stained glass, judicial bench.
    INTERACTION: Judge pounding gavel, shockwave rings, throne.
    """
    floor_y = 1380
    # Vaulted Gothic Pillars
    for px in [100, 340, VIDEO_WIDTH - 340, VIDEO_WIDTH - 100]:
        draw.rectangle([px - 35, 180, px + 35, floor_y], fill=(225, 220, 210), outline=INK, width=4)
        # Arch crowns
        draw.arc([px - 140, 150, px + 140, 350], 180, 360, fill=INK, width=4)

    # Stained Glass Window in center
    cx, cy = VIDEO_WIDTH // 2, 420
    draw.ellipse([cx - 160, cy - 160, cx + 160, cy + 160], fill=(240, 245, 255), outline=ROYAL_GOLD, width=6)
    draw.line([(cx - 160, cy), (cx + 160, cy)], fill=INK, width=3)
    draw.line([(cx, cy - 160), (cx, cy + 160)], fill=INK, width=3)

    # Stone Floor Checkerboard
    draw.line([(0, floor_y), (VIDEO_WIDTH, floor_y)], fill=INK, width=6)
    for fx in range(0, VIDEO_WIDTH, 80):
        draw.line([(fx, floor_y), (fx - 50, floor_y + 120)], fill=(210, 205, 195), width=2)


def draw_setting_pirate_sea(draw: ImageDraw.ImageDraw, t: float, p: float):
    """
    High Seas / Pirate Fleet: Wooden pirate ship deck, mast, skull flag, rolling ocean.
    INTERACTION: Cannons smoking and firing cannonballs across the waves!
    """
    floor_y = 1380
    # Rolling Blue Ocean Waves in background
    for layer, (col, speed, offset_y) in enumerate([(WATER_BLUE, 3.0, 100), ((30, 90, 160), 4.5, 50)]):
        wave_pts = [(0, floor_y + 300)]
        for x in range(0, VIDEO_WIDTH + 40, 40):
            y = floor_y - 200 + offset_y + int(math.sin(x * 0.01 + t * speed) * 35)
            wave_pts.append((x, y))
        wave_pts.append((VIDEO_WIDTH, floor_y + 300))
        draw.polygon(wave_pts, fill=col)

    # Wooden Pirate Ship Deck
    ship_pts = [(0, floor_y - 80), (VIDEO_WIDTH, floor_y - 120), (VIDEO_WIDTH, floor_y + 200), (0, floor_y + 200)]
    draw.polygon(ship_pts, fill=WOOD_BROWN, outline=INK, width=6)
    # Wooden deck planks
    for py in range(floor_y - 60, floor_y + 150, 40):
        draw.line([(0, py), (VIDEO_WIDTH, py - 40)], fill=(85, 45, 20), width=3)

    # Ship Mast & Rigging
    mast_x = 220
    draw.line([(mast_x, floor_y - 80), (mast_x, 240)], fill=(80, 45, 20), width=18)
    # Yardarm
    draw.line([(mast_x - 140, 360), (mast_x + 140, 360)], fill=(80, 45, 20), width=10)
    # Skull and Crossbones Jolly Roger Flag fluttering
    flag_wave = math.sin(t * 12.0) * 8
    draw.polygon([(mast_x, 260), (mast_x + 150 + flag_wave, 280), (mast_x + 130 + flag_wave, 360), (mast_x, 340)], fill=(20, 20, 25), outline=INK, width=3)
    # White skull
    draw.ellipse([mast_x + 55, 285, mast_x + 85, 315], fill=(255, 255, 255))
    draw.line([(mast_x + 45, 325), (mast_x + 95, 285)], fill=(255, 255, 255), width=3)
    draw.line([(mast_x + 45, 285), (mast_x + 95, 325)], fill=(255, 255, 255), width=3)

    # Firing Cannon (on the right deck)
    cannon_x = VIDEO_WIDTH - 240
    draw.rectangle([cannon_x, floor_y - 140, cannon_x + 80, floor_y - 80], fill=(50, 50, 55), outline=INK, width=4)
    # Wooden wheels
    draw.ellipse([cannon_x - 15, floor_y - 100, cannon_x + 35, floor_y - 50], fill=WOOD_BROWN, outline=INK, width=4)
    # Cannon smoke & flying cannonball!
    smoke_t = (t * 4.0) % 1.0
    for s in range(5):
        smx = cannon_x - 40 - s * 25 - int(smoke_t * 60)
        smy = floor_y - 150 - int(math.sin(s + t * 4) * 15)
        draw.ellipse([smx - 18, smy - 18, smx + 18, smy + 18], fill=(230, 230, 230))
    # Flying cannonball
    cb_x = cannon_x - 120 - int(smoke_t * 300)
    cb_y = floor_y - 150 - int(smoke_t * 50)
    draw.ellipse([cb_x - 14, cb_y - 14, cb_x + 14, cb_y + 14], fill=(30, 30, 35))


def draw_setting_chaotic_marathon(draw: ImageDraw.ImageDraw, t: float, p: float):
    """
    1904 St. Louis Olympic Marathon: Dusty dirt road, finish line ribbon, vintage jalopy car!
    INTERACTION: Stickman running, vintage car driving past with exhaust puffs!
    """
    floor_y = 1380
    # Dusty dirt road and hills
    draw.line([(0, floor_y), (VIDEO_WIDTH, floor_y)], fill=(160, 130, 90), width=8)
    draw.rectangle([0, floor_y, VIDEO_WIDTH, VIDEO_HEIGHT], fill=(225, 205, 165))

    # Finish Line Banner (on right)
    draw.line([(VIDEO_WIDTH - 120, floor_y), (VIDEO_WIDTH - 120, floor_y - 420)], fill=(50, 50, 50), width=8)
    draw.rectangle([VIDEO_WIDTH - 300, floor_y - 420, VIDEO_WIDTH - 120, floor_y - 340], fill=CRIMSON, outline=INK, width=4)
    draw.text((VIDEO_WIDTH - 210, floor_y - 380), "ST. LOUIS 1904", fill=(255, 255, 255), anchor="mm", font_size=24)

    # Vintage 1904 Jalopy Car Driving across screen!
    car_x = int((t * 220) % (VIDEO_WIDTH + 400)) - 200
    car_y = floor_y - 80
    # Car body
    draw.rectangle([car_x, car_y - 80, car_x + 220, car_y], fill=(35, 75, 45), outline=INK, width=5)
    draw.rectangle([car_x + 60, car_y - 150, car_x + 180, car_y - 80], fill=(200, 220, 240), outline=INK, width=4)
    # Spoked wheels rotating
    for wx in [car_x + 40, car_x + 180]:
        draw.ellipse([wx - 35, car_y - 35, wx + 35, car_y + 35], fill=(30, 30, 30), outline=ROYAL_GOLD, width=5)
        # Wheel spokes
        spoke_angle = t * 14.0
        draw.line([(wx - 30 * math.cos(spoke_angle), car_y - 30 * math.sin(spoke_angle)), (wx + 30 * math.cos(spoke_angle), car_y + 30 * math.sin(spoke_angle))], fill=(255, 255, 255), width=3)
    # Exhaust smoke puffs trailing behind car
    for exp in range(4):
        esx = car_x - 30 - exp * 35 - int((t * 50) % 40)
        esy = car_y - 30 - exp * 10
        draw.ellipse([esx - 15, esy - 15, esx + 15, esy + 15], fill=(210, 210, 210))


# ====================================================================
# 3. STORY ARCHETYPE ROUTER
# ====================================================================
def detect_story_archetype(topic_title: str) -> str:
    """
    Detects the best historical visual setting and action archetype based on the topic.
    """
    title_lower = topic_title.lower()
    if any(k in title_lower for k in ["beer", "molasses", "flood", "disaster", "london"]):
        return "victorian_disaster"
    elif any(k in title_lower for k in ["synod", "pope", "court", "trial", "corpse", "judge", "vatican"]):
        return "courtroom_macabre"
    elif any(k in title_lower for k in ["pirate", "ching", "ship", "sea", "navy", "sailor", "fleet"]):
        return "pirate_naval"
    elif any(k in title_lower for k in ["marathon", "olympic", "race", "runner", "st. louis"]):
        return "chaotic_sports"
    elif any(k in title_lower for k in ["dance", "dancing", "plague"]):
        return "dancing_plague"
    else:
        return "medieval_war"


# ====================================================================
# 4. MASTER STORY-DRIVEN FRAME RENDERER
# ====================================================================
def render_stickman_frame(t: float, total_duration: float, topic_title: str) -> Image.Image:
    """
    Generates a live, animated 2D stickman frame where the background, characters,
    and interactions adapt 100% to the specific historical story!
    """
    img = Image.new("RGB", (VIDEO_WIDTH, VIDEO_HEIGHT), BG_PAPER)
    draw = ImageDraw.Draw(img)

    archetype = detect_story_archetype(topic_title)
    p = t / total_duration
    floor_y = 1380

    # -------------------------------------------------------------
    # 1. Render Story-Adaptive Background
    # -------------------------------------------------------------
    if archetype == "victorian_disaster":
        draw_setting_victorian_disaster(draw, t, p)
    elif archetype == "medieval_war":
        draw_setting_medieval_castle(draw, t, p)
    elif archetype == "pirate_naval":
        draw_setting_pirate_sea(draw, t, p)
    elif archetype == "chaotic_sports":
        draw_setting_chaotic_marathon(draw, t, p)
    else:  # courtroom_macabre or default
        draw_setting_courtroom(draw, t, p)

    # -------------------------------------------------------------
    # 2. Dynamic Banner & Category Header
    # -------------------------------------------------------------
    draw.rectangle([60, 160, VIDEO_WIDTH - 60, 260], fill=(20, 20, 25), outline=ROYAL_GOLD, width=4)
    # Category icon based on setting
    cat_icons = {
        "victorian_disaster": "🌊 BIZARRE HISTORICAL DISASTER",
        "medieval_war": "⚔️ THE WAR OF ABSURDITY",
        "courtroom_macabre": "⚖️ THE MACABRE TRIAL",
        "pirate_naval": "🏴‍☠️ HISTORICAL PIRATE OVERLORD",
        "chaotic_sports": "🏃 THE MOST CHAOTIC RACE IN HISTORY"
    }
    banner_text = cat_icons.get(archetype, "📜 HISTORICAL ANOMALY")
    draw.text((VIDEO_WIDTH // 2, 210), banner_text, fill=ROYAL_GOLD, anchor="mm", font_size=38)

    # -------------------------------------------------------------
    # 3. Dynamic Story-Adaptive Characters & Live Interactions
    # -------------------------------------------------------------
    if archetype == "victorian_disaster":
        # Scene 1 (0-30%): Brewer whistling, holding mug
        if p < 0.30:
            main_x = 420
            draw_stickman(draw, x=main_x, y=floor_y, action="talk", emotion="smug", facing=1, scale=1.3, t=t, hat="tophat", prop="mug")
            # Citizen walking past
            draw_stickman(draw, x=main_x + 280, y=floor_y, action="walk", emotion="normal", facing=-1, scale=1.0, t=t, hat="tophat")
        # Scene 2 (30-65%): Tsunami wave bursting! Citizens screaming and fleeing in panic!
        elif p < 0.65:
            # Panicked citizens running away from the wave!
            run_x1 = 450 + int((t * 280) % 550)
            draw_stickman(draw, x=run_x1, y=floor_y, action="panic", emotion="panic", facing=1, scale=1.2, t=t, hat="tophat")
            run_x2 = 280 + int((t * 320) % 650)
            draw_stickman(draw, x=run_x2, y=floor_y, action="run", emotion="panic", facing=1, scale=1.0, t=t)
        # Scene 3 (65-100%): Citizen climbed on street lamp, another swimming with beer mug!
        else:
            # Citizen clinging to street lamp
            draw_stickman(draw, x=180, y=floor_y - 120, action="panic", emotion="shock", facing=1, scale=1.0, t=t)
            # Guy swimming in beer wave
            swim_x = VIDEO_WIDTH // 2 + int(math.sin(t * 3) * 60)
            draw_stickman(draw, x=swim_x, y=floor_y - 20, action="dance", emotion="laughing", facing=1, scale=1.1, t=t, prop="mug")

    elif archetype == "medieval_war":
        # Scene 1 (0-30%): Knight walking toward the city well
        if p < 0.30:
            draw_stickman(draw, x=280 + int(t * 80), y=floor_y, action="walk", emotion="normal", facing=1, scale=1.2, t=t, hat="helm")
            # Citizen near well
            draw_stickman(draw, x=VIDEO_WIDTH // 2, y=floor_y, action="talk", emotion="normal", facing=-1, scale=1.0, t=t)
        # Scene 2 (30-65%): Soldier stealing the bucket and sprinting away!
        elif p < 0.65:
            # Thief sprinting with bucket in hand
            thief_x = int((t * 350) % (VIDEO_WIDTH + 300)) - 150
            draw_stickman(draw, x=thief_x, y=floor_y, action="run", emotion="smug", facing=1, scale=1.2, t=t, hat="helm", prop="bucket")
            # Knight chasing with sword!
            draw_stickman(draw, x=thief_x - 180, y=floor_y, action="run", emotion="angry", facing=1, scale=1.2, t=t, hat="helm", prop="sword")
        # Scene 3 (65-100%): Full medieval sword battle!
        else:
            duel_x = VIDEO_WIDTH // 2
            draw_stickman(draw, x=duel_x - 140, y=floor_y, action="sword_strike", emotion="angry", facing=1, scale=1.3, t=t, hat="helm", prop="sword")
            draw_stickman(draw, x=duel_x + 140, y=floor_y, action="sword_strike", emotion="angry", facing=-1, scale=1.3, t=t + 0.3, hat="helm", prop="sword")
            # Bucket sitting triumphantly on the floor
            draw_stickman(draw, x=duel_x, y=floor_y, action="dead", emotion="dead", facing=1, scale=0.8, t=t)

    elif archetype == "pirate_naval":
        # Scene 1 (0-35%): Pirate Queen Ching Shih pacing deck with cutlass
        if p < 0.35:
            draw_stickman(draw, x=VIDEO_WIDTH // 2 - 80, y=floor_y - 80, action="talk", emotion="smug", facing=1, scale=1.3, t=t, hat="pirate_hat", prop="cutlass")
            # Lookout pirate cheering in background
            draw_stickman(draw, x=220, y=floor_y - 280, action="cheer", emotion="laughing", facing=1, scale=0.8, t=t)
        # Scene 2 (35-70%): Cannon battle! Firing at enemy ship!
        elif p < 0.70:
            # Pirate Queen commanding fire!
            draw_stickman(draw, x=340, y=floor_y - 80, action="sword_strike", emotion="angry", facing=1, scale=1.3, t=t, hat="pirate_hat", prop="cutlass")
            # Enemy officer with hands up surrendering!
            draw_stickman(draw, x=VIDEO_WIDTH - 380, y=floor_y - 80, action="panic", emotion="shock", facing=-1, scale=1.1, t=t, hat="helm")
        # Scene 3 (70-100%): Pirate Queen counting gold, cheering crew!
        else:
            draw_stickman(draw, x=VIDEO_WIDTH // 2, y=floor_y - 80, action="cheer", emotion="laughing", facing=1, scale=1.4, t=t, hat="pirate_hat", prop="cutlass")
            draw_stickman(draw, x=280, y=floor_y - 80, action="dance", emotion="laughing", facing=1, scale=1.0, t=t)
            draw_stickman(draw, x=VIDEO_WIDTH - 280, y=floor_y - 80, action="dance", emotion="laughing", facing=-1, scale=1.0, t=t)

    elif archetype == "chaotic_sports":
        # Scene 1 (0-35%): Marathon runner trotting exhausted in trousers
        if p < 0.35:
            draw_stickman(draw, x=380, y=floor_y, action="run", emotion="panic", facing=1, scale=1.2, t=t)
            # Other runner trotting behind
            draw_stickman(draw, x=180, y=floor_y, action="walk", emotion="shock", facing=1, scale=1.0, t=t)
        # Scene 2 (35-70%): Winner hitchhiking in a vintage car waving!
        elif p < 0.70:
            car_x = int((t * 220) % (VIDEO_WIDTH + 400)) - 200
            # Stickman inside the car waving out the window!
            draw_stickman(draw, x=car_x + 120, y=floor_y - 120, action="cheer", emotion="laughing", facing=1, scale=0.9, t=t)
            # Exhausted runner on foot looking shocked!
            draw_stickman(draw, x=VIDEO_WIDTH - 240, y=floor_y, action="panic", emotion="shock", facing=-1, scale=1.1, t=t)
        # Scene 3 (70-100%): Breaking the finish line tape!
        else:
            draw_stickman(draw, x=VIDEO_WIDTH - 150, y=floor_y, action="run", emotion="smug", facing=1, scale=1.3, t=t)
            # Second runner flat on floor exhausted
            draw_stickman(draw, x=380, y=floor_y, action="dead", emotion="dead", facing=1, scale=1.0, t=t)

    else:  # courtroom_macabre (Corpse Synod)
        # Scene 1 (0-30%): Pope walking in talking
        if p < 0.30:
            draw_stickman(draw, x=380, y=floor_y, action="talk", emotion="normal", facing=1, scale=1.3, t=t, hat="pope_hat")
            panic_x = -150 + int((t * 450) % (VIDEO_WIDTH + 300))
            draw_stickman(draw, x=panic_x, y=floor_y - 10, action="panic", emotion="panic", facing=1, scale=0.8, t=t)
        # Scene 2 (30-65%): Guard dragging corpse
        elif p < 0.65:
            drag_x = VIDEO_WIDTH - int(((t - total_duration * 0.3) * 90) % (VIDEO_WIDTH + 200))
            # Corpse
            draw_stickman(draw, x=drag_x - 180, y=floor_y + 40, action="dead", emotion="dead", facing=1, scale=1.1, t=t, hat="crown")
            # Guard pulling
            draw_stickman(draw, x=drag_x, y=floor_y, action="run", emotion="angry", facing=1, scale=1.2, t=t)
            draw.line([(drag_x - 50, floor_y - 120), (drag_x - 120, floor_y)], fill=(90, 60, 30), width=6)
        # Scene 3 (65-100%): Judge Pope violently slamming gavel!
        else:
            # Corpse on throne
            draw.rectangle([180, floor_y - 260, 320, floor_y], fill=(90, 30, 30), outline=ROYAL_GOLD, width=5)
            draw_stickman(draw, x=250, y=floor_y - 30, action="dead", emotion="dead", facing=1, scale=1.1, t=t, hat="crown")
            # Shaking defense deacon
            draw_stickman(draw, x=380, y=floor_y, action="panic", emotion="panic", facing=-1, scale=1.0, t=t)
            # Judge on desk
            desk_x = VIDEO_WIDTH - 420
            draw.rectangle([desk_x, floor_y - 140, desk_x + 320, floor_y], fill=WOOD_BROWN, outline=INK, width=6)
            draw_stickman(draw, x=desk_x + 160, y=floor_y - 140, action="gavel_slam", emotion="angry", facing=-1, scale=1.3, t=t, hat="pope_hat", prop="gavel")
            # Gavel impact shockwaves
            if (t * 8.5) % 3.14 > 2.2:
                ix = desk_x + 50
                draw.arc([ix - 60, floor_y - 180, ix + 60, floor_y - 100], 180, 360, fill=ROYAL_GOLD, width=5)
                draw.text((ix - 30, floor_y - 200), "SLAM!", fill=CRIMSON, font_size=32)

    # -------------------------------------------------------------
    # 4. Animated Kinetic Progress Bar at Bottom
    # -------------------------------------------------------------
    prog_w = int(VIDEO_WIDTH * p)
    draw.rectangle([0, VIDEO_HEIGHT - 16, prog_w, VIDEO_HEIGHT], fill=ROYAL_GOLD)

    return img
