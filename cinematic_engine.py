import math
import random
from typing import Dict, Any, List, Optional
from PIL import Image, ImageDraw
from config import VIDEO_WIDTH, VIDEO_HEIGHT, FPS

PALETTE = {
    "bg_wall": (238, 233, 222),
    "bg_dark": (26, 25, 30),
    "stone": (165, 160, 150),
    "stone_dark": (95, 90, 85),
    "brick": (175, 70, 55),
    "wood": (120, 75, 40),
    "wood_dark": (70, 40, 20),
    "skin": (255, 222, 190),
    "gold": (245, 195, 35),
    "crimson": (220, 45, 45),
    "beer_amber": (205, 130, 25),
    "outline": (25, 25, 30),
    "shadow": (0, 0, 0, 55)
}

# ====================================================================
# 1. DYNAMIC CAMERA (ZOOM, PAN, SCREEN SHAKE)
# ====================================================================
def apply_camera(world_img: Image.Image, target_x: float, target_y: float, zoom: float, shake: float = 0.0) -> Image.Image:
    """Crops and zooms the world image smoothly toward the focal point."""
    w, h = world_img.size
    cw = int(VIDEO_WIDTH / zoom)
    ch = int(VIDEO_HEIGHT / zoom)

    sx = (random.random() * 2 - 1) * shake if shake > 0 else 0
    sy = (random.random() * 2 - 1) * shake if shake > 0 else 0

    left = int(target_x - cw // 2 + sx)
    top = int(target_y - ch // 2 + sy)

    left = max(0, min(left, w - cw))
    top = max(0, min(top, h - ch))
    right = left + cw
    bottom = top + ch

    cropped = world_img.crop((left, top, right, bottom))
    return cropped.resize((VIDEO_WIDTH, VIDEO_HEIGHT), Image.Resampling.BILINEAR)

# ====================================================================
# 2. POLISHED COSTUMED CHARACTER RIG
# ====================================================================
def draw_costumed_character(
    draw: ImageDraw.ImageDraw,
    x: float,
    y: float,
    costume: str = "prisoner",   # 'prisoner', 'soldier', 'pope', 'worker', 'citizen'
    action: str = "idle",        # 'idle', 'walk', 'run', 'water_wall', 'slam', 'shock', 'dead'
    facing: int = 1,
    scale: float = 1.0,
    t: float = 0.0,
    prop: Optional[str] = None   # 'cup', 'brush', 'gavel', 'rifle', 'bread'
):
    head_r = int(38 * scale)
    torso_h = int(125 * scale)
    limb_w = max(6, int(10 * scale))
    outline_w = max(3, int(4 * scale))

    head_x = int(x)
    head_y = int(y - torso_h - head_r)
    neck = (head_x, int(y - torso_h))
    hip = (head_x, int(y))

    mouth_open = 0.0
    body_angle = 0.0
    l_arm_ang, r_arm_ang = 0.3, -0.3
    l_leg_ang, r_leg_ang = 0.0, 0.0

    if action == "walk":
        cyc = math.sin(t * 8.0)
        l_leg_ang = cyc * 0.5
        r_leg_ang = -cyc * 0.5
        l_arm_ang = -cyc * 0.55
        r_arm_ang = cyc * 0.55
        head_y += int(abs(cyc) * 8 * scale)
        hip = (hip[0], int(hip[1] + abs(cyc) * 8 * scale))
        mouth_open = max(0.0, math.sin(t * 10.0) * 0.4)

    elif action == "run":
        cyc = math.sin(t * 16.0)
        body_angle = 0.28 * facing
        l_leg_ang = cyc * 0.9
        r_leg_ang = -cyc * 0.9
        l_arm_ang = -cyc * 1.0
        r_arm_ang = cyc * 1.0
        head_y += int(abs(cyc) * 14 * scale)

    elif action == "water_wall":
        pour_cyc = math.sin(t * 5.0)
        r_arm_ang = -1.4 + pour_cyc * 0.3 * facing
        l_arm_ang = 0.4 * facing
        body_angle = 0.1 * facing

    elif action == "shock":
        l_arm_ang = -2.1
        r_arm_ang = 2.1
        body_angle = -0.1 * facing
        mouth_open = 0.9

    elif action == "slam":
        slam_cyc = max(0.0, math.sin(t * 8.0))
        r_arm_ang = -2.2 + slam_cyc * 2.4 * facing
        l_arm_ang = 0.4 * facing
        body_angle = slam_cyc * 0.15 * facing

    # Soft drop shadow under feet
    draw.ellipse([x - 50 * scale, y - 10, x + 50 * scale, y + 10], fill=PALETTE["shadow"])

    # --- Legs ---
    pants_color = (45, 45, 55)
    if costume == "prisoner":
        pants_color = (235, 235, 240)
    elif costume in ["soldier", "wwii"]:
        pants_color = (85, 95, 60)
    elif costume == "worker":
        pants_color = (50, 75, 115)

    for leg_ang, side in [(l_leg_ang, -1), (r_leg_ang, 1)]:
        knee_x = hip[0] + int(math.sin(leg_ang) * 45 * scale)
        knee_y = hip[1] + int(math.cos(leg_ang) * 45 * scale)
        foot_x = knee_x + int(math.sin(leg_ang * 0.8) * 45 * scale)
        foot_y = knee_y + int(math.cos(leg_ang * 0.8) * 45 * scale)

        draw.line([hip, (knee_x, knee_y)], fill=pants_color, width=limb_w)
        draw.line([(knee_x, knee_y), (foot_x, foot_y)], fill=pants_color, width=limb_w)
        x0 = min(foot_x - 12 * scale, foot_x + 18 * scale * facing)
        x1 = max(foot_x - 12 * scale, foot_x + 18 * scale * facing)
        draw.ellipse([x0, foot_y - 6 * scale, x1, foot_y + 10 * scale], fill=(20, 20, 20))

    # --- Torso ---
    neck_x = neck[0] + int(body_angle * 35)
    neck = (neck_x, neck[1])
    head_x += int(body_angle * 45)

    torso_rect = [neck[0] - 28 * scale, neck[1], neck[0] + 28 * scale, hip[1]]
    if costume == "prisoner":
        draw.rounded_rectangle(torso_rect, radius=8, fill=(245, 245, 250), outline=PALETTE["outline"], width=outline_w)
        for sy in range(neck[1] + 15, hip[1] - 10, int(22 * scale)):
            draw.rectangle([neck[0] - 28 * scale, sy, neck[0] + 28 * scale, sy + 10 * scale], fill=(30, 30, 35))
    elif costume in ["soldier", "wwii"]:
        draw.rounded_rectangle(torso_rect, radius=8, fill=(95, 105, 70), outline=PALETTE["outline"], width=outline_w)
        draw.rectangle([neck[0] - 28 * scale, hip[1] - 25 * scale, neck[0] + 28 * scale, hip[1] - 10 * scale], fill=(65, 40, 20))
        draw.rectangle([neck[0] - 6 * scale, hip[1] - 27 * scale, neck[0] + 6 * scale, hip[1] - 8 * scale], fill=PALETTE["gold"])
    elif costume == "pope":
        draw.rounded_rectangle(torso_rect, radius=8, fill=(250, 250, 255), outline=PALETTE["outline"], width=outline_w)
        draw.line([(neck[0] - 12 * scale, neck[1]), (neck[0] - 12 * scale, hip[1])], fill=PALETTE["gold"], width=6)
        draw.line([(neck[0] + 12 * scale, neck[1]), (neck[0] + 12 * scale, hip[1])], fill=PALETTE["gold"], width=6)
    else:  # worker / citizen
        draw.rounded_rectangle(torso_rect, radius=8, fill=(230, 230, 235), outline=PALETTE["outline"], width=outline_w)
        draw.line([(neck[0] - 18 * scale, neck[1]), (neck[0] - 18 * scale, hip[1])], fill=(45, 70, 110), width=6)
        draw.line([(neck[0] + 18 * scale, neck[1]), (neck[0] + 18 * scale, hip[1])], fill=(45, 70, 110), width=6)

    # --- Arms ---
    shoulder = (neck[0], neck[1] + int(12 * scale))
    hand_r_pos = None

    for arm_ang, side in [(l_arm_ang, -1), (r_arm_ang, 1)]:
        el_x = shoulder[0] + int(math.sin(arm_ang) * 36 * scale * facing)
        el_y = shoulder[1] + int(math.cos(arm_ang) * 36 * scale)
        h_x = el_x + int(math.sin(arm_ang + 0.3 * side) * 36 * scale * facing)
        h_y = el_y + int(math.cos(arm_ang + 0.3 * side) * 36 * scale)

        draw.line([shoulder, (el_x, el_y)], fill=pants_color if costume == "prisoner" else (85, 95, 60), width=limb_w)
        draw.line([(el_x, el_y), (h_x, h_y)], fill=pants_color if costume == "prisoner" else (85, 95, 60), width=limb_w)
        draw.ellipse([h_x - 8 * scale, h_y - 8 * scale, h_x + 8 * scale, h_y + 8 * scale], fill=PALETTE["skin"], outline=PALETTE["outline"], width=2)
        if side == 1:
            hand_r_pos = (h_x, h_y)

    # --- Head & Face ---
    draw.ellipse([head_x - head_r, head_y - head_r, head_x + head_r, head_y + head_r], fill=PALETTE["skin"], outline=PALETTE["outline"], width=outline_w)
    eye_ox = int(12 * scale * facing)
    eye_y = head_y - int(4 * scale)

    if action == "shock":
        draw.ellipse([head_x - 18 + eye_ox, eye_y - 12, head_x - 2 + eye_ox, eye_y + 12], fill=(255, 255, 255), outline=PALETTE["outline"], width=3)
        draw.ellipse([head_x + 4 + eye_ox, eye_y - 12, head_x + 20 + eye_ox, eye_y + 12], fill=(255, 255, 255), outline=PALETTE["outline"], width=3)
        draw.ellipse([head_x - 12 + eye_ox, eye_y - 3, head_x - 8 + eye_ox, eye_y + 3], fill=PALETTE["outline"])
        draw.ellipse([head_x + 10 + eye_ox, eye_y - 3, head_x + 14 + eye_ox, eye_y + 3], fill=PALETTE["outline"])
        draw.ellipse([head_x - 10 + eye_ox, head_y + 10, head_x + 10 + eye_ox, head_y + 28], fill=PALETTE["crimson"], outline=PALETTE["outline"], width=3)
    else:
        draw.ellipse([head_x - 14 + eye_ox, eye_y - 6, head_x - 2 + eye_ox, eye_y + 6], fill=PALETTE["outline"])
        draw.ellipse([head_x + 4 + eye_ox, eye_y - 6, head_x + 16 + eye_ox, eye_y + 6], fill=PALETTE["outline"])
        if mouth_open > 0.2:
            mh = int(15 * scale * mouth_open)
            draw.chord([head_x - 10 + eye_ox, head_y + 10, head_x + 10 + eye_ox, head_y + 10 + mh], 0, 180, fill=PALETTE["crimson"], outline=PALETTE["outline"], width=2)
        else:
            draw.line([(head_x - 8 + eye_ox, head_y + 14), (head_x + 8 + eye_ox, head_y + 14)], fill=PALETTE["outline"], width=3)

    # --- Hats ---
    if costume == "prisoner":
        draw.chord([head_x - head_r, head_y - head_r - 6, head_x + head_r, head_y], 180, 360, fill=(245, 245, 250), outline=PALETTE["outline"], width=3)
        draw.line([(head_x - head_r + 6, head_y - head_r // 2), (head_x + head_r - 6, head_y - head_r // 2)], fill=(30, 30, 35), width=6)
    elif costume in ["soldier", "wwii"]:
        draw.chord([head_x - head_r - 4, head_y - head_r - 8, head_x + head_r + 4, head_y + 4], 180, 360, fill=(80, 90, 55), outline=PALETTE["outline"], width=3)
        draw.polygon([(head_x + head_r * facing, head_y - 10), (head_x + (head_r + 20) * facing, head_y), (head_x + head_r * facing, head_y + 5)], fill=(65, 75, 45))
    elif costume == "pope":
        pts = [(head_x - 22, head_y - head_r), (head_x - 18, head_y - head_r - 55), (head_x, head_y - head_r - 70), (head_x + 18, head_y - head_r - 55), (head_x + 22, head_y - head_r)]
        draw.polygon(pts, fill=(255, 255, 255), outline=PALETTE["outline"], width=3)
        draw.line([(head_x, head_y - head_r - 55), (head_x, head_y - head_r - 10)], fill=PALETTE["gold"], width=4)

    # --- Interactive Props ---
    if hand_r_pos and prop:
        hx, hy = hand_r_pos
        if prop == "cup":
            draw.polygon([(hx, hy - 15), (hx + 28 * facing, hy - 25), (hx + 35 * facing, hy - 5), (hx + 6 * facing, hy + 5)], fill=(185, 190, 200), outline=PALETTE["outline"], width=2)
            # Water splash stream!
            draw.line([(hx + 30 * facing, hy - 10), (hx + 90 * facing, hy + 60)], fill=(70, 160, 245), width=5)
            for d in range(4):
                sp_x = hx + (90 + d * 15) * facing
                sp_y = hy + 60 + int(math.sin(d + t * 8) * 12)
                draw.ellipse([sp_x - 4, sp_y - 4, sp_x + 4, sp_y + 4], fill=(120, 190, 255))
        elif prop == "gavel":
            draw.line([(hx, hy), (hx + 40 * facing, hy - 30)], fill=PALETTE["wood"], width=6)
            draw.line([(hx + 25 * facing, hy - 45), (hx + 55 * facing, hy - 15)], fill=PALETTE["wood_dark"], width=14)
        elif prop == "rifle":
            draw.line([(hx - 20 * facing, hy + 40), (hx + 40 * facing, hy - 60)], fill=(90, 60, 30), width=6)
            draw.line([(hx + 30 * facing, hy - 50), (hx + 60 * facing, hy - 90)], fill=(45, 45, 50), width=4)

# ====================================================================
# 3. INTERACTIVE STORY SCENES & LIVING BACKGROUNDS
# ====================================================================

def render_scene_prison_wall(draw: ImageDraw.ImageDraw, t: float, p: float):
    """STORY: The Prisoner Who Watered His Wall (Water softens mortar -> daylight escape hole)"""
    floor_y = 1420
    block_h = 90
    block_w = 180
    for row, y in enumerate(range(180, floor_y, block_h)):
        offset = (row % 2) * (block_w // 2)
        for x in range(-offset, VIDEO_WIDTH + block_w, block_w):
            is_target = (row == 7 and 600 < x < 850)
            color = (120, 115, 105) if is_target and p > 0.3 else (165, 160, 150)
            draw.rectangle([x + 3, y + 3, x + block_w - 3, y + block_h - 3], fill=color, outline=PALETTE["outline"], width=3)
            if is_target and p > 0.4:
                draw.line([(x + 20, y + 30), (x + 20, y + block_h + 30)], fill=(60, 140, 220), width=4)

    # Iron Window with God-Ray Sunbeam
    win_x, win_y = 120, 260
    draw.rectangle([win_x, win_y, win_x + 260, win_y + 320], fill=(135, 195, 245), outline=PALETTE["outline"], width=8)
    for bx in range(win_x + 50, win_x + 260, 50):
        draw.line([(bx, win_y), (bx, win_y + 320)], fill=(40, 40, 45), width=8)
    draw.polygon([(win_x + 40, win_y + 40), (win_x + 240, win_y + 40), (VIDEO_WIDTH, floor_y - 200), (400, floor_y)], fill=(255, 245, 200, 30))

    draw.line([(0, floor_y), (VIDEO_WIDTH, floor_y)], fill=PALETTE["outline"], width=6)
    draw.rectangle([0, floor_y, VIDEO_WIDTH, VIDEO_HEIGHT], fill=(110, 105, 100))

    if p < 0.35:
        draw_costumed_character(draw, x=420, y=floor_y, costume="prisoner", action="walk", facing=1, scale=1.3, t=t, prop="cup")
        draw_costumed_character(draw, x=VIDEO_WIDTH - 180, y=floor_y, costume="soldier", action="idle", facing=-1, scale=1.1, t=t)
    elif p < 0.75:
        draw_costumed_character(draw, x=580, y=floor_y, costume="prisoner", action="water_wall", facing=1, scale=1.3, t=t, prop="cup")
        draw.text((720, floor_y - 420), "DRIP... DRIP...", fill=(70, 160, 245), font_size=34)
    else:
        hole_x, hole_y = 740, floor_y - 240
        draw.ellipse([hole_x - 90, hole_y - 80, hole_x + 90, hole_y + 80], fill=(135, 205, 255), outline=PALETTE["outline"], width=6)
        for r in range(6):
            rx = hole_x - 80 + r * 30
            draw.rectangle([rx, floor_y - 25, rx + 25, floor_y], fill=(135, 130, 120), outline=PALETTE["outline"], width=2)
        draw_costumed_character(draw, x=hole_x - 30, y=floor_y - 50, costume="prisoner", action="run", facing=1, scale=1.2, t=t)
        draw_costumed_character(draw, x=180, y=floor_y, costume="soldier", action="shock", facing=1, scale=1.2, t=t)


def render_scene_wwii_jungle(draw: ImageDraw.ImageDraw, t: float, p: float):
    """STORY: The Soldier Who Fought WWII for 10,000 Days (Hiroo Onoda in jungle)"""
    floor_y = 1420
    for tx in [80, 320, 680, 940]:
        draw.rectangle([tx - 25, 200, tx + 25, floor_y], fill=(95, 75, 45), outline=PALETTE["outline"], width=4)
        for ly in range(300, floor_y - 200, 150):
            sway = math.sin(t * 4.0 + ly) * 15
            draw.arc([tx - 120 + sway, ly - 40, tx + 120 + sway, ly + 60], 190, 350, fill=(45, 115, 40), width=16)

    draw.line([(0, floor_y), (VIDEO_WIDTH, floor_y)], fill=PALETTE["outline"], width=6)
    draw.rectangle([0, floor_y, VIDEO_WIDTH, VIDEO_HEIGHT], fill=(65, 85, 40))

    if p < 0.60:
        draw_costumed_character(draw, x=450, y=floor_y, costume="soldier", action="walk", facing=1, scale=1.3, t=t, prop="rifle")
        cx = 240
        draw.polygon([(cx - 30, floor_y), (cx + 30, floor_y), (cx, floor_y - 45)], fill=PALETTE["crimson"])
        draw.polygon([(cx - 15, floor_y), (cx + 15, floor_y), (cx, floor_y - 30)], fill=PALETTE["gold"])
    else:
        draw_costumed_character(draw, x=380, y=floor_y, costume="soldier", action="shock", facing=1, scale=1.3, t=t)
        draw_costumed_character(draw, x=720, y=floor_y, costume="citizen", action="walk", facing=-1, scale=1.2, t=t, prop="bread")
        draw.text((VIDEO_WIDTH // 2, floor_y - 420), "10,000 DAYS IN THE JUNGLE", fill=PALETTE["gold"], anchor="mm", font_size=42)


def render_scene_victorian_brewery(draw: ImageDraw.ImageDraw, t: float, p: float):
    """STORY: The London Beer Flood of 1814 (Giant vat bursts -> amber wave washes street)"""
    floor_y = 1380
    for idx, (bx, bw, bh) in enumerate([(40, 300, 750), (360, 380, 850), (760, 280, 700)]):
        draw.rectangle([bx, floor_y - bh, bx + bw, floor_y], fill=PALETTE["brick"], outline=PALETTE["outline"], width=5)
        for wy in range(floor_y - bh + 60, floor_y - 100, 110):
            for wx in range(bx + 40, bx + bw - 40, 80):
                draw.rectangle([wx, wy, wx + 45, wy + 70], fill=(255, 240, 190), outline=PALETTE["outline"], width=3)
        # Smoke
        for smk in range(3):
            sy = floor_y - bh - 40 - smk * 35 - int((t * 40) % 50)
            sx = bx + 60 + int(math.sin(t * 3.0 + smk) * 20)
            draw.ellipse([sx - 15, sy - 15, sx + 15, sy + 15], fill=(220, 220, 220))

    # Gas Lamp
    draw.line([(180, floor_y), (180, floor_y - 280)], fill=PALETTE["outline"], width=8)
    draw.polygon([(160, floor_y - 280), (200, floor_y - 280), (190, floor_y - 330), (170, floor_y - 330)], fill=(255, 235, 120), outline=PALETTE["outline"], width=4)

    # Giant Vat
    draw.rounded_rectangle([-120, floor_y - 500, 420, floor_y], radius=30, fill=PALETTE["wood"], outline=PALETTE["outline"], width=7)
    for vy in [floor_y - 420, floor_y - 280, floor_y - 140]:
        draw.line([(-120, vy), (420, vy)], fill=(60, 60, 65), width=10)

    # Flood Wave
    if p > 0.25:
        draw.line([(180, floor_y - 420), (220, floor_y - 250), (190, floor_y - 100)], fill=(255, 240, 120), width=8)
        wave_front = int((p - 0.25) * 1.6 * VIDEO_WIDTH)
        wave_pts = [(0, floor_y + 400), (0, floor_y - 280)]
        for wx in range(0, min(VIDEO_WIDTH, wave_front), 30):
            wy = floor_y - 260 + int(math.sin(wx * 0.02 + t * 8.0) * 45)
            wave_pts.append((wx, wy))
        if wave_front > 0:
            wave_pts.append((min(VIDEO_WIDTH, wave_front), floor_y + 400))
            draw.polygon(wave_pts, fill=PALETTE["beer_amber"], outline=(140, 80, 10), width=6)

    draw.line([(0, floor_y), (VIDEO_WIDTH, floor_y)], fill=PALETTE["outline"], width=6)

    if p < 0.30:
        draw_costumed_character(draw, x=420, y=floor_y, costume="worker", action="walk", facing=1, scale=1.3, t=t)
        draw_costumed_character(draw, x=700, y=floor_y, costume="citizen", action="walk", facing=-1, scale=1.1, t=t)
    elif p < 0.65:
        run_x = 450 + int((t * 280) % 550)
        draw_costumed_character(draw, x=run_x, y=floor_y, costume="citizen", action="run", facing=1, scale=1.2, t=t)
    else:
        draw_costumed_character(draw, x=180, y=floor_y - 120, costume="citizen", action="shock", facing=1, scale=1.0, t=t)
        draw_costumed_character(draw, x=VIDEO_WIDTH // 2, y=floor_y - 20, costume="worker", action="walk", facing=1, scale=1.1, t=t)


def render_scene_courtroom(draw: ImageDraw.ImageDraw, t: float, p: float):
    """STORY: The Corpse Synod of 897 AD (Pope drags corpse to trial & pounds gavel)"""
    floor_y = 1380
    for px in [100, 340, VIDEO_WIDTH - 340, VIDEO_WIDTH - 100]:
        draw.rectangle([px - 35, 180, px + 35, floor_y], fill=(225, 220, 210), outline=PALETTE["outline"], width=4)
        draw.arc([px - 140, 150, px + 140, 350], 180, 360, fill=PALETTE["outline"], width=4)

    draw.ellipse([VIDEO_WIDTH // 2 - 160, 260, VIDEO_WIDTH // 2 + 160, 580], fill=(240, 245, 255), outline=PALETTE["gold"], width=6)
    draw.line([(0, floor_y), (VIDEO_WIDTH, floor_y)], fill=PALETTE["outline"], width=6)

    if p < 0.30:
        draw_costumed_character(draw, x=380, y=floor_y, costume="pope", action="walk", facing=1, scale=1.3, t=t)
    elif p < 0.65:
        drag_x = VIDEO_WIDTH - int(((t - 10) * 90) % (VIDEO_WIDTH + 200))
        draw_costumed_character(draw, x=drag_x - 180, y=floor_y + 40, costume="pope", action="dead", facing=1, scale=1.1, t=t)
        draw_costumed_character(draw, x=drag_x, y=floor_y, costume="soldier", action="run", facing=1, scale=1.2, t=t)
    else:
        draw.rectangle([180, floor_y - 260, 320, floor_y], fill=(90, 30, 30), outline=PALETTE["gold"], width=5)
        draw_costumed_character(draw, x=250, y=floor_y - 30, costume="pope", action="dead", facing=1, scale=1.1, t=t)
        desk_x = VIDEO_WIDTH - 420
        draw.rectangle([desk_x, floor_y - 140, desk_x + 320, floor_y], fill=PALETTE["wood"], outline=PALETTE["outline"], width=6)
        draw_costumed_character(draw, x=desk_x + 160, y=floor_y - 140, costume="pope", action="slam", facing=-1, scale=1.3, t=t, prop="gavel")


# ====================================================================
# 4. MASTER CINEMATIC FRAME GENERATOR WITH DYNAMIC CAMERA
# ====================================================================
def render_cinematic_frame(t: float, total_duration: float, topic_title: str) -> Image.Image:
    """
    Renders a live 2D animated frame with full costumed characters,
    interactive living scenery, and cinematic camera moves (zooms & pans)!
    """
    # 1. Create World Canvas
    world = Image.new("RGB", (VIDEO_WIDTH, VIDEO_HEIGHT), PALETTE["bg_wall"])
    draw = ImageDraw.Draw(world)

    p = t / total_duration
    title_lower = topic_title.lower()

    # Route story to appropriate interactive scene
    if any(k in title_lower for k in ["water", "wall", "prison", "prisoner", "escape", "soap"]):
        render_scene_prison_wall(draw, t, p)
        category_label = "🔓 THE IMPOSSIBLE ESCAPE"
    elif any(k in title_lower for k in ["soldier", "wwii", "jungle", "10,000", "war", "hiroo"]):
        render_scene_wwii_jungle(draw, t, p)
        category_label = "🎖️ THE SOLDIER WHO NEVER SURRENDERED"
    elif any(k in title_lower for k in ["beer", "flood", "london", "disaster", "molasses"]):
        render_scene_victorian_brewery(draw, t, p)
        category_label = "🌊 THE 15-FOOT BEER TSUNAMI"
    else:  # Courtroom / Synod / Default
        render_scene_courtroom(draw, t, p)
        category_label = "⚖️ THE MACABRE TRIAL"

    # Category Banner at top
    draw.rectangle([60, 160, VIDEO_WIDTH - 60, 260], fill=PALETTE["bg_dark"], outline=PALETTE["gold"], width=4)
    draw.text((VIDEO_WIDTH // 2, 210), category_label, fill=PALETTE["gold"], anchor="mm", font_size=36)

    # 2. Dynamic Camera Moves: Easing Zoom & Pan
    # In Scene 1: Camera slowly pushes in from 1.0 to 1.18x on the character's face/hands!
    cam_zoom = 1.0 + (p * 0.18)
    cam_x = VIDEO_WIDTH // 2
    cam_y = VIDEO_HEIGHT // 2

    # Screen shake during major events (flood burst, gavel slam)
    cam_shake = 0.0
    if "court" in category_label.lower() and p > 0.65 and (t * 8.0) % 3.14 > 2.2:
        cam_shake = 10.0
    elif "flood" in category_label.lower() and 0.25 < p < 0.35:
        cam_shake = 12.0

    frame = apply_camera(world, target_x=cam_x, target_y=cam_y, zoom=cam_zoom, shake=cam_shake)

    # 3. Kinetic Progress Bar on final camera frame
    draw_final = ImageDraw.Draw(frame)
    prog_w = int(VIDEO_WIDTH * p)
    draw_final.rectangle([0, VIDEO_HEIGHT - 16, prog_w, VIDEO_HEIGHT], fill=PALETTE["gold"])

    return frame
