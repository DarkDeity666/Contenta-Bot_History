import math
import random
from typing import Dict, Any, List, Optional, Tuple
from PIL import Image, ImageDraw, ImageFilter

from config import VIDEO_WIDTH, VIDEO_HEIGHT, FPS

# ====================================================================
# PALETTE DEFINITION (High-contrast cinematic colors)
# ====================================================================
PALETTE = {
    "bg_dark": (18, 19, 24),
    "bg_slate": (32, 34, 42),
    "wall_stone": (55, 52, 48),
    "wall_stone_light": (75, 71, 65),
    "wall_mortar": (38, 36, 33),
    "floor_wood": (62, 44, 30),
    "floor_wood_dark": (45, 30, 20),
    "stick_black": (20, 20, 22),
    "stick_white": (250, 250, 252),
    "stick_head": (255, 255, 255),
    "gold": (255, 205, 45),
    "gold_glow": (255, 225, 90),
    "crimson": (230, 45, 45),
    "water_blue": (65, 160, 245),
    "water_light": (140, 210, 255),
    "lantern_warm": (255, 175, 55),
    "moonlight": (130, 190, 255),
    "shadow": (0, 0, 0, 75)
}

# ====================================================================
# 1. 2D CAMERA SYSTEM (PUNCH ZOOMS, TRACKING PAN, SCREEN SHAKE)
# ====================================================================
class Camera2D:
    def __init__(self, target_x: float, target_y: float, zoom: float = 1.0, shake: float = 0.0):
        self.target_x = target_x
        self.target_y = target_y
        self.zoom = zoom
        self.shake = shake
        
        # Compute shake offsets
        self.shake_x = (random.random() * 2 - 1) * shake if shake > 0 else 0
        self.shake_y = (random.random() * 2 - 1) * shake if shake > 0 else 0

    def world_to_screen(self, wx: float, wy: float) -> Tuple[int, int]:
        """Converts world coordinates to screen pixel coordinates directly."""
        cx = VIDEO_WIDTH / 2.0
        cy = VIDEO_HEIGHT / 2.0
        
        sx = cx + (wx - self.target_x) * self.zoom + self.shake_x
        sy = cy + (wy - self.target_y) * self.zoom + self.shake_y
        return int(sx), int(sy)

    def scale_len(self, length: float) -> int:
        """Scales line/shape dimensions according to camera zoom."""
        return max(1, int(length * self.zoom))

def get_camera_shot(t: float, total_duration: float, topic_title: str) -> Camera2D:
    """
    Computes dynamic cinematic camera moves based on script progression:
    - Hook (0-4s): Starts wide (1.1x), sudden PUNCH ZOOM (1.55x) on stickman at 1.8s!
    - Setup (4-15s): Medium tracking shot (1.25x) panning with stickman.
    - Escalation (15-28s): Tight action zoom (1.65x) on the wall/tool with camera shake.
    - Climax & Loop (28s-End): Wide reveal (1.05x) pulling back for infinite loop.
    """
    p = t / total_duration
    
    # Default center anchor
    cam_x = VIDEO_WIDTH / 2.0
    cam_y = 1150.0
    cam_zoom = 1.15
    cam_shake = 0.0

    if t < 1.8:
        # Initial hook establishing
        cam_zoom = 1.08 + (t / 1.8) * 0.07
        cam_x = 540.0
        cam_y = 1180.0
    elif t < 4.2:
        # PUNCH ZOOM on the hook punchline!
        cam_zoom = 1.52 + math.sin((t - 1.8) * 2.0) * 0.05
        cam_x = 480.0
        cam_y = 1080.0
        if t < 2.2:
            cam_shake = 8.0 * (1.0 - (t - 1.8) / 0.4)
    elif t < 15.0:
        # Medium tracking pan following character's journey
        pan_progress = (t - 4.2) / 10.8
        cam_x = 480.0 + pan_progress * 160.0
        cam_y = 1120.0
        cam_zoom = 1.25 + math.sin(pan_progress * 3.14) * 0.1
    elif t < 27.0:
        # Tight action zoom on the interaction (chipping mortar, water pouring)
        cam_x = 680.0
        cam_y = 1160.0
        cam_zoom = 1.62
        # Subtle rhythmic impact shake during chipping
        strike_phase = (t * 6.0) % 1.0
        if strike_phase < 0.2:
            cam_shake = 5.0
    else:
        # Climax escape and pull-back to wide shot for seamless loop
        pull_p = min(1.0, (t - 27.0) / 7.0)
        cam_x = 680.0 - pull_p * 140.0
        cam_y = 1160.0 + pull_p * 20.0
        cam_zoom = 1.62 - pull_p * 0.52 # Smoothly pulls back from 1.62x to 1.10x!
        if 27.0 <= t <= 27.8:
            cam_shake = 12.0 * (1.0 - (t - 27.0) / 0.8) # Big impact shake on breakout

    return Camera2D(target_x=cam_x, target_y=cam_y, zoom=cam_zoom, shake=cam_shake)

# ====================================================================
# 2. POLISHED 2D STICKMAN RIG (EXPRESSIVE, COSTUMED, LIVING MOTION)
# ====================================================================
def draw_cinematic_stickman(
    draw: ImageDraw.ImageDraw,
    cam: Camera2D,
    world_x: float,
    world_y: float,
    costume: str = "prisoner",   # 'prisoner', 'soldier', 'pope', 'worker', 'citizen'
    action: str = "idle",        # 'idle', 'walk', 'run', 'water_wall', 'chip', 'slam', 'shock'
    facing: int = 1,
    scale: float = 1.0,
    t: float = 0.0,
    prop: Optional[str] = None   # 'cup', 'spoon', 'gavel', 'rifle', 'torch'
):
    """
    Renders an ultra-polished, highly expressive 2D stickman:
    - Bold, thick comic ink lines that scale with camera zoom
    - Expressive cartoon eyes that dart around and react with shock/suspicion
    - Animated mouth with speech bounce
    - Themed historical costumes (prisoner stripes, roman toga, papal robes, soldier gear)
    - Animated dynamic props (chipping spoon, splashing water cup, gavel, bayonet)
    """
    # Scale dimensions with camera zoom
    limb_w = max(4, cam.scale_len(10 * scale))
    outline_w = max(2, cam.scale_len(3.5 * scale))
    head_r = cam.scale_len(36 * scale)
    torso_len = cam.scale_len(120 * scale)

    # Base bone coordinates in world space
    wx, wy = world_x, world_y

    # Motion kinematics
    hip_bounce = 0.0
    body_tilt = 0.0
    l_leg_ang, r_leg_ang = 0.0, 0.0
    l_arm_ang, r_arm_ang = 0.25, -0.25
    eye_look_x = facing * 0.35
    mouth_open = max(0.0, math.sin(t * 14.0) * 0.5)

    if action == "walk":
        cycle = math.sin(t * 7.5)
        l_leg_ang = cycle * 0.55
        r_leg_ang = -cycle * 0.55
        l_arm_ang = -cycle * 0.6
        r_arm_ang = cycle * 0.6
        hip_bounce = -abs(cycle) * 12 * scale
        body_tilt = 0.1 * facing

    elif action == "run":
        cycle = math.sin(t * 15.0)
        l_leg_ang = cycle * 0.95
        r_leg_ang = -cycle * 0.95
        l_arm_ang = -cycle * 1.1
        r_arm_ang = cycle * 1.1
        hip_bounce = -abs(cycle) * 20 * scale
        body_tilt = 0.32 * facing

    elif action == "water_wall":
        pour = math.sin(t * 4.5)
        r_arm_ang = -1.45 + pour * 0.25 * facing
        l_arm_ang = 0.4 * facing
        body_tilt = 0.12 * facing
        eye_look_x = facing * 0.7

    elif action == "chip":
        strike = (t * 6.0) % 1.0
        # Windup -> Snap strike -> Recoil
        if strike < 0.4:
            r_arm_ang = -1.9 * facing
            body_tilt = -0.15 * facing
        elif strike < 0.6:
            r_arm_ang = -0.85 * facing # Impact!
            body_tilt = 0.22 * facing
        else:
            r_arm_ang = -1.3 * facing
            body_tilt = 0.05 * facing
        l_arm_ang = 0.5 * facing

    elif action == "shock":
        l_arm_ang = -2.3
        r_arm_ang = 2.3
        body_tilt = -0.15 * facing
        mouth_open = 1.0
        hip_bounce = math.sin(t * 20.0) * 4.0

    elif action == "slam":
        slam_cyc = max(0.0, math.sin(t * 8.0))
        r_arm_ang = -2.2 + slam_cyc * 2.4 * facing
        l_arm_ang = 0.35 * facing
        body_tilt = slam_cyc * 0.2 * facing

    # Screen space core joints
    sx_hip, sy_hip = cam.world_to_screen(wx, wy + hip_bounce)
    
    # Neck and head
    neck_dx = int(math.sin(body_tilt) * torso_len)
    neck_dy = int(-math.cos(body_tilt) * torso_len)
    sx_neck = sx_hip + neck_dx
    sy_neck = sy_hip + neck_dy
    
    head_dx = int(math.sin(body_tilt) * (head_r + 4))
    head_dy = int(-math.cos(body_tilt) * (head_r + 4))
    sx_head = sx_neck + head_dx
    sy_head = sy_neck + head_dy

    # 1. Soft Dynamic Drop Shadow under feet
    sh_w = cam.scale_len(55 * scale)
    sh_h = cam.scale_len(14 * scale)
    sx_feet, sy_feet = cam.world_to_screen(wx, wy)
    draw.ellipse([sx_feet - sh_w, sy_feet - sh_h, sx_feet + sh_w, sy_feet + sh_h], fill=(0, 0, 0, 95))

    # 2. Draw Legs (with knee articulation)
    leg_len = cam.scale_len(48 * scale)
    for leg_ang, side in [(l_leg_ang, -1), (r_leg_ang, 1)]:
        knee_x = sx_hip + int(math.sin(leg_ang) * leg_len)
        knee_y = sy_hip + int(math.cos(leg_ang) * leg_len)
        foot_x = knee_x + int(math.sin(leg_ang * 0.85) * leg_len)
        foot_y = knee_y + int(math.cos(leg_ang * 0.85) * leg_len)

        # Draw pants/legs
        draw.line([(sx_hip, sy_hip), (knee_x, knee_y)], fill=PALETTE["stick_black"], width=limb_w)
        draw.line([(knee_x, knee_y), (foot_x, foot_y)], fill=PALETTE["stick_black"], width=limb_w)
        
        # Shoe
        shoe_w = cam.scale_len(18 * scale)
        shoe_h = cam.scale_len(9 * scale)
        s_x0 = foot_x - (shoe_w // 2) if facing < 0 else foot_x - 4
        s_x1 = foot_x + shoe_w if facing > 0 else foot_x + (shoe_w // 2)
        draw.ellipse([s_x0, foot_y - shoe_h // 2, s_x1, foot_y + shoe_h // 2], fill=PALETTE["stick_black"])

    # 3. Draw Torso & Costume
    torso_w = cam.scale_len(32 * scale)
    torso_rect = [sx_neck - torso_w // 2, sy_neck, sx_neck + torso_w // 2, sy_hip]
    
    if costume == "prisoner":
        # White & Black Striped Prison Inmate Shirt
        draw.rounded_rectangle(torso_rect, radius=max(2, cam.scale_len(6)), fill=(245, 245, 250), outline=PALETTE["stick_black"], width=outline_w)
        stripe_step = max(4, cam.scale_len(16 * scale))
        for sy in range(sy_neck + stripe_step // 2, sy_hip - 4, stripe_step * 2):
            draw.rectangle([sx_neck - torso_w // 2 + outline_w, sy, sx_neck + torso_w // 2 - outline_w, sy + stripe_step], fill=PALETTE["stick_black"])
    elif costume in ["soldier", "guard"]:
        # Khaki Military Uniform with Gold Buckle
        draw.rounded_rectangle(torso_rect, radius=max(2, cam.scale_len(6)), fill=(80, 95, 60), outline=PALETTE["stick_black"], width=outline_w)
        draw.rectangle([sx_neck - torso_w // 2, sy_hip - cam.scale_len(18), sx_neck + torso_w // 2, sy_hip - cam.scale_len(6)], fill=(50, 35, 20))
        draw.rectangle([sx_neck - cam.scale_len(6), sy_hip - cam.scale_len(20), sx_neck + cam.scale_len(6), sy_hip - cam.scale_len(4)], fill=PALETTE["gold"])
    elif costume == "pope":
        # Crimson & Gold Ceremonial Papal Robes
        draw.rounded_rectangle(torso_rect, radius=max(2, cam.scale_len(6)), fill=(245, 245, 255), outline=PALETTE["stick_black"], width=outline_w)
        draw.line([(sx_neck - cam.scale_len(8), sy_neck), (sx_neck - cam.scale_len(8), sy_hip)], fill=PALETTE["gold"], width=cam.scale_len(5))
        draw.line([(sx_neck + cam.scale_len(8), sy_neck), (sx_neck + cam.scale_len(8), sy_hip)], fill=PALETTE["gold"], width=cam.scale_len(5))
    else:
        # Standard Clean Black Comic Torso
        draw.line([(sx_neck, sy_neck), (sx_hip, sy_hip)], fill=PALETTE["stick_black"], width=limb_w + 4)

    # 4. Draw Arms & Hands
    shoulder = (sx_neck, sy_neck + cam.scale_len(10 * scale))
    arm_len = cam.scale_len(40 * scale)
    hand_r_pos = None

    for arm_ang, side in [(l_arm_ang, -1), (r_arm_ang, 1)]:
        el_x = shoulder[0] + int(math.sin(arm_ang) * arm_len * facing)
        el_y = shoulder[1] + int(math.cos(arm_ang) * arm_len)
        h_x = el_x + int(math.sin(arm_ang + 0.3 * side) * arm_len * facing)
        h_y = el_y + int(math.cos(arm_ang + 0.3 * side) * arm_len)

        draw.line([shoulder, (el_x, el_y)], fill=PALETTE["stick_black"], width=limb_w)
        draw.line([(el_x, el_y), (h_x, h_y)], fill=PALETTE["stick_black"], width=limb_w)
        
        # Stylized Hand/Fist
        hand_r = cam.scale_len(7 * scale)
        draw.ellipse([h_x - hand_r, h_y - hand_r, h_x + hand_r, h_y + hand_r], fill=PALETTE["stick_white"], outline=PALETTE["stick_black"], width=outline_w)
        if side == 1:
            hand_r_pos = (h_x, h_y)

    # 5. Draw Head, Face & Expressions
    draw.ellipse([sx_head - head_r, sy_head - head_r, sx_head + head_r, sy_head + head_r], fill=PALETTE["stick_head"], outline=PALETTE["stick_black"], width=outline_w + 1)
    
    # Big expressive cartoon eyes
    eye_offset_x = int(head_r * eye_look_x)
    eye_w = cam.scale_len(10 * scale)
    eye_h = cam.scale_len(14 * scale) if action != "shock" else cam.scale_len(20 * scale)
    eye_y = sy_head - cam.scale_len(4 * scale)

    # Left & Right eyes
    draw.ellipse([sx_head - eye_w * 2 + eye_offset_x, eye_y - eye_h, sx_head - eye_offset_x // 2 + eye_offset_x, eye_y + eye_h], fill=(255, 255, 255), outline=PALETTE["stick_black"], width=2)
    draw.ellipse([sx_head + eye_offset_x // 2 + eye_offset_x, eye_y - eye_h, sx_head + eye_w * 2 + eye_offset_x, eye_y + eye_h], fill=(255, 255, 255), outline=PALETTE["stick_black"], width=2)

    # Dark Pupils tracking the scene
    pupil_r = cam.scale_len(4 * scale)
    pupil_ox = int(facing * 3 * scale)
    draw.ellipse([sx_head - eye_w + eye_offset_x + pupil_ox - pupil_r, eye_y - pupil_r, sx_head - eye_w + eye_offset_x + pupil_ox + pupil_r, eye_y + pupil_r], fill=PALETTE["stick_black"])
    draw.ellipse([sx_head + eye_w + eye_offset_x + pupil_ox - pupil_r, eye_y - pupil_r, sx_head + eye_w + eye_offset_x + pupil_ox + pupil_r, eye_y + pupil_r], fill=PALETTE["stick_black"])

    # Animated Expressive Mouth
    mouth_y = sy_head + cam.scale_len(12 * scale)
    if action == "shock":
        # Wide agape O-mouth
        m_r = cam.scale_len(12 * scale)
        draw.ellipse([sx_head + eye_offset_x - m_r, mouth_y - m_r, sx_head + eye_offset_x + m_r, mouth_y + m_r], fill=PALETTE["crimson"], outline=PALETTE["stick_black"], width=2)
        # Sweat droplet
        sw_x = sx_head - head_r - cam.scale_len(10)
        sw_y = sy_head - cam.scale_len(10)
        draw.ellipse([sw_x - 5, sw_y, sw_x + 5, sw_y + 12], fill=PALETTE["water_light"])
        draw.polygon([(sw_x - 4, sw_y + 3), (sw_x, sw_y - 8), (sw_x + 4, sw_y + 3)], fill=PALETTE["water_light"])
    elif mouth_open > 0.2:
        # Talking open smile/grimace
        mh = cam.scale_len(10 * scale * mouth_open)
        mw = cam.scale_len(14 * scale)
        draw.chord([sx_head + eye_offset_x - mw, mouth_y - mh, sx_head + eye_offset_x + mw, mouth_y + mh], 0, 180, fill=PALETTE["crimson"], outline=PALETTE["stick_black"], width=2)
    else:
        # Confident smirk / focused straight mouth
        draw.line([(sx_head + eye_offset_x - cam.scale_len(8), mouth_y), (sx_head + eye_offset_x + cam.scale_len(8), mouth_y)], fill=PALETTE["stick_black"], width=outline_w)

    # 6. Character Costume Hats
    if costume == "prisoner":
        # Striped Prisoner Beanie
        draw.chord([sx_head - head_r - 2, sy_head - head_r - cam.scale_len(10), sx_head + head_r + 2, sy_head - cam.scale_len(4)], 180, 360, fill=(245, 245, 250), outline=PALETTE["stick_black"], width=outline_w)
        draw.line([(sx_head - head_r + 4, sy_head - head_r // 2 - cam.scale_len(4)), (sx_head + head_r - 4, sy_head - head_r // 2 - cam.scale_len(4))], fill=PALETTE["stick_black"], width=cam.scale_len(6))
    elif costume in ["soldier", "guard"]:
        # Steel Military Helmet
        draw.chord([sx_head - head_r - 6, sy_head - head_r - cam.scale_len(12), sx_head + head_r + 6, sy_head + cam.scale_len(4)], 180, 360, fill=(70, 85, 50), outline=PALETTE["stick_black"], width=outline_w)
        draw.line([(sx_head - head_r - 10, sy_head + cam.scale_len(2)), (sx_head + head_r + 10, sy_head + cam.scale_len(2))], fill=(50, 60, 35), width=cam.scale_len(5))
    elif costume == "pope":
        # Papal Mitre
        mitre_pts = [
            (sx_head - cam.scale_len(20), sy_head - head_r),
            (sx_head - cam.scale_len(16), sy_head - head_r - cam.scale_len(60)),
            (sx_head, sy_head - head_r - cam.scale_len(75)),
            (sx_head + cam.scale_len(16), sy_head - head_r - cam.scale_len(60)),
            (sx_head + cam.scale_len(20), sy_head - head_r)
        ]
        draw.polygon(mitre_pts, fill=(255, 255, 255), outline=PALETTE["stick_black"], width=outline_w)
        draw.line([(sx_head, sy_head - head_r - cam.scale_len(60)), (sx_head, sy_head - head_r - cam.scale_len(10))], fill=PALETTE["gold"], width=cam.scale_len(4))

    # 7. Interactive Props
    if hand_r_pos and prop:
        hx, hy = hand_r_pos
        if prop == "cup":
            # Tin Cup with splashing water droplets
            cw = cam.scale_len(22 * scale)
            ch = cam.scale_len(18 * scale)
            draw.polygon([(hx, hy - ch), (hx + cw * facing, hy - ch - 6), (hx + cw * facing + 4, hy + 4), (hx + 4 * facing, hy + 8)], fill=(195, 200, 210), outline=PALETTE["stick_black"], width=2)
            # Water splash arc
            splash_x = hx + int(cw * 1.5 * facing)
            splash_y = hy + ch
            draw.line([(hx + cw * facing, hy - ch // 2), (splash_x, splash_y)], fill=PALETTE["water_blue"], width=cam.scale_len(4))
            for d in range(3):
                dx = splash_x + int((d * 12 + math.sin(t * 10 + d) * 8) * facing)
                dy = splash_y + int(math.cos(t * 10 + d) * 10)
                dr = cam.scale_len(3)
                draw.ellipse([dx - dr, dy - dr, dx + dr, dy + dr], fill=PALETTE["water_light"])
        elif prop == "spoon":
            # Metal spoon / chisel
            sl = cam.scale_len(30 * scale)
            draw.line([(hx, hy), (hx + int(sl * facing), hy - int(sl * 0.4))], fill=(210, 215, 220), width=cam.scale_len(5))
            draw.ellipse([hx + int(sl * facing) - 4, hy - int(sl * 0.4) - 4, hx + int(sl * facing) + 6, hy - int(sl * 0.4) + 6], fill=(170, 175, 180))
        elif prop == "gavel":
            gl = cam.scale_len(42 * scale)
            draw.line([(hx, hy), (hx + int(gl * facing), hy - int(gl * 0.7))], fill=PALETTE["floor_wood"], width=cam.scale_len(7))
            gh_x = hx + int(gl * facing)
            gh_y = hy - int(gl * 0.7)
            draw.line([(gh_x - 12, gh_y - 18), (gh_x + 12, gh_y + 18)], fill=PALETTE["floor_wood_dark"], width=cam.scale_len(16))
        elif prop == "rifle":
            rl = cam.scale_len(75 * scale)
            draw.line([(hx - int(25 * facing), hy + 30), (hx + int(rl * facing), hy - 65)], fill=(85, 55, 30), width=cam.scale_len(7))
            draw.line([(hx + int((rl - 10) * facing), hy - 55), (hx + int((rl + 25) * facing), hy - 95)], fill=(50, 50, 55), width=cam.scale_len(4))

# ====================================================================
# 3. RICH ATMOSPHERIC ILLUSTRATED 2D BACKGROUNDS
# ====================================================================

def render_scene_prison_break(draw: ImageDraw.ImageDraw, cam: Camera2D, t: float, p: float):
    """
    STORY: The Prisoner Who Watered His Wall
    - Rich stone brick dungeon wall with varied color shading
    - Mortar seams eroding and bricks actively popping out
    - Iron barred window with glowing God-ray moonlight beam
    - Wooden prisoner bed with straw mattress
    - Guard patrolling with lantern in the distance
    - Dynamic danger callout: glowing arrow pointing to the loose brick!
    """
    floor_wy = 1380.0
    brick_w, brick_h = 160.0, 75.0

    # 1. Detailed Stone Masonry Wall
    for row, wy in enumerate(range(200, int(floor_wy), int(brick_h))):
        offset = (row % 2) * (brick_w / 2.0)
        for wx in range(int(-offset - 200), VIDEO_WIDTH + 400, int(brick_w)):
            is_escape_spot = (row == 8 and 680 < wx < 920)
            
            # Convert brick corners to camera screen coordinates
            s_x0, s_y0 = cam.world_to_screen(wx + 4, wy + 4)
            s_x1, s_y1 = cam.world_to_screen(wx + brick_w - 4, wy + brick_h - 4)

            # Weathered color variation
            b_seed = (int(wx) * 31 + int(wy) * 17) % 7
            base_col = (52 + b_seed * 4, 48 + b_seed * 3, 44 + b_seed * 3)

            if is_escape_spot:
                if p > 0.45:
                    # Mortar completely dissolved!
                    base_col = (25, 23, 20)
                else:
                    base_col = (65, 80, 105) # Damp dark mortar

            draw.rectangle([s_x0, s_y0, s_x1, s_y1], fill=base_col, outline=PALETTE["wall_mortar"], width=max(1, cam.scale_len(2)))

    # 2. The Great Escape Hole (Revealed in Daylight!)
    hole_wx, hole_wy = 800.0, floor_wy - 210.0
    s_hx, s_hy = cam.world_to_screen(hole_wx, hole_wy)
    hole_rw = cam.scale_len(85)
    hole_rh = cam.scale_len(75)

    if p > 0.55:
        # Daylight beaming in through the broken opening!
        draw.ellipse([s_hx - hole_rw, s_hy - hole_rh, s_hx + hole_rw, s_hy + hole_rh], fill=PALETTE["moonlight"], outline=PALETTE["stick_black"], width=max(2, cam.scale_len(4)))
        # Broken rubble debris on the floor
        for r in range(5):
            rx_w = hole_wx - 70 + r * 35
            s_rx, s_ry = cam.world_to_screen(rx_w, floor_wy - 15)
            rw = cam.scale_len(24)
            rh = cam.scale_len(16)
            draw.rectangle([s_rx, s_ry, s_rx + rw, s_ry + rh], fill=(45, 42, 38), outline=PALETTE["stick_black"], width=max(1, cam.scale_len(2)))
    else:
        # Secret loose bricks vibrating
        vib = math.sin(t * 12.0) * 3 if 0.25 < p <= 0.55 else 0
        draw.rectangle([s_hx - hole_rw, s_hy - hole_rh + int(vib), s_hx + hole_rw, s_hy + hole_rh + int(vib)], fill=(35, 33, 30), outline=PALETTE["gold"] if p > 0.3 else PALETTE["wall_mortar"], width=max(1, cam.scale_len(3)))

    # 3. Dungeon Window with Moonlight God-Ray Beam
    win_wx, win_wy = 180.0, 420.0
    s_wx0, s_wy0 = cam.world_to_screen(win_wx, win_wy)
    s_wx1, s_wy1 = cam.world_to_screen(win_wx + 220, win_wy + 280)
    draw.rectangle([s_wx0, s_wy0, s_wx1, s_wy1], fill=(120, 180, 240), outline=PALETTE["stick_black"], width=max(2, cam.scale_len(5)))
    
    # Iron Bars on Window
    for bx in [win_wx + 55, win_wx + 110, win_wx + 165]:
        s_bx0, s_by0 = cam.world_to_screen(bx, win_wy)
        s_bx1, s_by1 = cam.world_to_screen(bx, win_wy + 280)
        draw.line([(s_bx0, s_by0), (s_bx1, s_by1)], fill=PALETTE["stick_black"], width=max(2, cam.scale_len(6)))

    # Volumetric light ray cutting through darkness
    ray_pts = [
        cam.world_to_screen(win_wx + 30, win_wy + 30),
        cam.world_to_screen(win_wx + 190, win_wy + 30),
        cam.world_to_screen(1050, floor_wy),
        cam.world_to_screen(450, floor_wy)
    ]
    draw.polygon(ray_pts, fill=(180, 220, 255, 35))

    # 4. Dungeon Cobblestone / Flagstone Floor
    s_fl_l = cam.world_to_screen(-300, floor_wy)
    s_fl_r = cam.world_to_screen(VIDEO_WIDTH + 300, floor_wy)
    draw.line([s_fl_l, s_fl_r], fill=PALETTE["stick_black"], width=max(3, cam.scale_len(7)))
    s_fl_bot = cam.world_to_screen(0, floor_wy + 600)
    draw.rectangle([s_fl_l[0], s_fl_l[1], s_fl_r[0], s_fl_bot[1]], fill=PALETTE["bg_dark"])

    # 5. Wooden Prisoner Cot / Bed
    bed_wx = 320.0
    s_bed0 = cam.world_to_screen(bed_wx - 140, floor_wy - 180)
    s_bed1 = cam.world_to_screen(bed_wx + 140, floor_wy)
    draw.rounded_rectangle([s_bed0[0], s_bed0[1], s_bed1[0], s_bed1[1]], radius=cam.scale_len(6), fill=PALETTE["floor_wood"], outline=PALETTE["stick_black"], width=max(2, cam.scale_len(4)))
    # Straw Mattress on Cot
    s_straw0 = cam.world_to_screen(bed_wx - 130, floor_wy - 230)
    s_straw1 = cam.world_to_screen(bed_wx + 130, floor_wy - 170)
    draw.rounded_rectangle([s_straw0[0], s_straw0[1], s_straw1[0], s_straw1[1]], radius=cam.scale_len(8), fill=(215, 185, 90), outline=PALETTE["stick_black"], width=max(2, cam.scale_len(3)))

    # 6. Character Choreography across the 4 Script Beats
    if p < 0.28:
        # Beat 1: Inmate sneaking across cell with water cup
        draw_cinematic_stickman(draw, cam, world_x=520, world_y=floor_wy, costume="prisoner", action="walk", facing=1, scale=1.35, t=t, prop="cup")
        # Secondary Guard patrolling in the background corridor
        draw_cinematic_stickman(draw, cam, world_x=980, world_y=floor_wy, costume="guard", action="idle", facing=-1, scale=1.1, t=t, prop="rifle")
    elif p < 0.60:
        # Beat 2 & 3: Inmate actively softening wall and chipping loose bricks!
        draw_cinematic_stickman(draw, cam, world_x=680, world_y=floor_wy, costume="prisoner", action="chip", facing=1, scale=1.45, t=t, prop="spoon")
        
        # Glowing 3D-style Floating Danger Callout (Like ujustbuiltit / Comicron)
        callout_sx, callout_sy = cam.world_to_screen(hole_wx, hole_wy - 140)
        draw.text((callout_sx, callout_sy), "⚡ MORTAR DISSOLVING", fill=PALETTE["gold"], anchor="mm", font_size=max(16, cam.scale_len(28)))
        # Glowing arrow pointing down to hole
        ar_y = callout_sy + cam.scale_len(22)
        draw.polygon([(callout_sx - 10, ar_y), (callout_sx + 10, ar_y), (callout_sx, ar_y + 14)], fill=PALETTE["gold"])
    else:
        # Beat 4: Climax Escape into daylight!
        draw_cinematic_stickman(draw, cam, world_x=hole_wx - 20, world_y=floor_wy - 40, costume="prisoner", action="run", facing=1, scale=1.3, t=t)
        # Shocked guard drops rifle!
        draw_cinematic_stickman(draw, cam, world_x=220, world_y=floor_wy, costume="guard", action="shock", facing=1, scale=1.25, t=t)


def render_scene_courtroom_synod(draw: ImageDraw.ImageDraw, cam: Camera2D, t: float, p: float):
    """
    STORY: The Corpse Synod of 897 AD (Pope Stephen VI puts deceased Pope Formosus on trial)
    - Gothic cathedral stone arches with glowing candle candelabras
    - High judicial bench with wooden gavel
    - Corpse of Formosus propped up on papal throne
    - Pope Stephen VI screaming accusations and pounding gavel
    """
    floor_wy = 1380.0
    
    # 1. Gothic Cathedral Arches
    for px in [120, 420, VIDEO_WIDTH - 420, VIDEO_WIDTH - 120]:
        s0 = cam.world_to_screen(px - 45, 120)
        s1 = cam.world_to_screen(px + 45, floor_wy)
        draw.rectangle([s0[0], s0[1], s1[0], s1[1]], fill=(60, 56, 52), outline=PALETTE["stick_black"], width=max(2, cam.scale_len(4)))
        # Arch curve
        s_arc0 = cam.world_to_screen(px - 140, 100)
        s_arc1 = cam.world_to_screen(px + 140, 380)
        draw.arc([s_arc0[0], s_arc0[1], s_arc1[0], s_arc1[1]], 180, 360, fill=PALETTE["gold"], width=max(2, cam.scale_len(4)))

    # Floor
    s_fl_l = cam.world_to_screen(-300, floor_wy)
    s_fl_r = cam.world_to_screen(VIDEO_WIDTH + 300, floor_wy)
    draw.line([s_fl_l, s_fl_r], fill=PALETTE["stick_black"], width=max(3, cam.scale_len(7)))
    s_fl_bot = cam.world_to_screen(0, floor_wy + 600)
    draw.rectangle([s_fl_l[0], s_fl_l[1], s_fl_r[0], s_fl_bot[1]], fill=PALETTE["floor_wood_dark"])

    # High Judicial Bench
    bench_wx = VIDEO_WIDTH - 320
    s_b0 = cam.world_to_screen(bench_wx - 160, floor_wy - 180)
    s_b1 = cam.world_to_screen(bench_wx + 160, floor_wy)
    draw.rectangle([s_b0[0], s_b0[1], s_b1[0], s_b1[1]], fill=PALETTE["floor_wood"], outline=PALETTE["stick_black"], width=max(2, cam.scale_len(5)))

    # Accused Throne
    throne_wx = 360.0
    s_t0 = cam.world_to_screen(throne_wx - 100, floor_wy - 260)
    s_t1 = cam.world_to_screen(throne_wx + 100, floor_wy)
    draw.rectangle([s_t0[0], s_t0[1], s_t1[0], s_t1[1]], fill=(120, 35, 35), outline=PALETTE["gold"], width=max(2, cam.scale_len(5)))

    if p < 0.35:
        # Beat 1: Pope enters cathedral
        draw_cinematic_stickman(draw, cam, world_x=480, world_y=floor_wy, costume="pope", action="walk", facing=1, scale=1.35, t=t)
    elif p < 0.70:
        # Beat 2 & 3: Dead Pope propped on throne, Pope Stephen slams gavel!
        draw_cinematic_stickman(draw, cam, world_x=throne_wx, world_y=floor_wy - 40, costume="pope", action="idle", facing=1, scale=1.2, t=t)
        draw_cinematic_stickman(draw, cam, world_x=bench_wx, world_y=floor_wy - 180, costume="pope", action="slam", facing=-1, scale=1.4, t=t, prop="gavel")
        
        # Comic Action Word: "GUILTY!"
        txt_sx, txt_sy = cam.world_to_screen(VIDEO_WIDTH // 2, 850)
        draw.text((txt_sx, txt_sy), "⚖️ GUILTY!", fill=PALETTE["crimson"], anchor="mm", font_size=max(20, cam.scale_len(48)))
    else:
        # Beat 4: Soldiers drag the corpse into the Tiber River!
        draw_cinematic_stickman(draw, cam, world_x=520, world_y=floor_wy, costume="guard", action="run", facing=1, scale=1.3, t=t)
        draw_cinematic_stickman(draw, cam, world_x=340, world_y=floor_wy, costume="pope", action="shock", facing=1, scale=1.1, t=t)


def render_scene_beer_flood(draw: ImageDraw.ImageDraw, cam: Camera2D, t: float, p: float):
    """
    STORY: The London Beer Flood of 1814
    - Victorian London brick brewery facade with smokestacks
    - Giant wooden fermentation vat bound with iron hoops
    - Hoops bursting with sparks and 15-foot tsunami wave of amber porter
    - Panicking citizens fleeing up streetlamps
    """
    floor_wy = 1380.0
    
    # Victorian Brewery Brick Buildings
    for bx, bw, bh in [(40, 320, 850), (400, 360, 920), (800, 320, 780)]:
        s0 = cam.world_to_screen(bx, floor_wy - bh)
        s1 = cam.world_to_screen(bx + bw, floor_wy)
        draw.rectangle([s0[0], s0[1], s1[0], s1[1]], fill=(145, 55, 42), outline=PALETTE["stick_black"], width=max(2, cam.scale_len(4)))
        # Windows
        for wy in range(int(floor_wy - bh + 80), int(floor_wy - 100), 120):
            for wx in range(bx + 40, bx + bw - 40, 90):
                ws0 = cam.world_to_screen(wx, wy)
                ws1 = cam.world_to_screen(wx + 50, wy + 80)
                draw.rectangle([ws0[0], ws0[1], ws1[0], ws1[1]], fill=(255, 235, 170), outline=PALETTE["stick_black"], width=2)

    # Giant Fermentation Vat on Left
    vat_w = 420.0
    vat_h = 580.0
    vs0 = cam.world_to_screen(-80, floor_wy - vat_h)
    vs1 = cam.world_to_screen(vat_w, floor_wy)
    draw.rounded_rectangle([vs0[0], vs0[1], vs1[0], vs1[1]], radius=cam.scale_len(25), fill=PALETTE["floor_wood"], outline=PALETTE["stick_black"], width=max(3, cam.scale_len(7)))
    # Iron Hoops
    for hy in [floor_wy - 480, floor_wy - 320, floor_wy - 160]:
        hs0 = cam.world_to_screen(-80, hy)
        hs1 = cam.world_to_screen(vat_w, hy)
        draw.line([hs0, hs1], fill=(45, 45, 50), width=max(2, cam.scale_len(12)))

    # Cobblestone Street
    s_fl_l = cam.world_to_screen(-300, floor_wy)
    s_fl_r = cam.world_to_screen(VIDEO_WIDTH + 300, floor_wy)
    draw.line([s_fl_l, s_fl_r], fill=PALETTE["stick_black"], width=max(3, cam.scale_len(7)))

    # The 15-Foot Porter Tsunami!
    if p > 0.28:
        wave_front_w = -80.0 + (p - 0.28) * 1.8 * (VIDEO_WIDTH + 400)
        wave_pts = [
            cam.world_to_screen(-80, floor_wy + 400),
            cam.world_to_screen(-80, floor_wy - 340)
        ]
        for wx in range(-80, int(min(VIDEO_WIDTH + 200, wave_front_w)), 40):
            wy = floor_wy - 320 + math.sin(wx * 0.02 + t * 9.0) * 45
            wave_pts.append(cam.world_to_screen(wx, wy))
        if wave_front_w > -80:
            wave_pts.append(cam.world_to_screen(min(VIDEO_WIDTH + 200, wave_front_w), floor_wy + 400))
            draw.polygon(wave_pts, fill=(195, 120, 25), outline=(130, 75, 10), width=max(2, cam.scale_len(5)))

    # Characters
    if p < 0.32:
        draw_cinematic_stickman(draw, cam, world_x=450, world_y=floor_wy, costume="worker", action="walk", facing=1, scale=1.3, t=t)
    elif p < 0.70:
        draw_cinematic_stickman(draw, cam, world_x=720, world_y=floor_wy, costume="citizen", action="run", facing=1, scale=1.35, t=t)
    else:
        draw_cinematic_stickman(draw, cam, world_x=820, world_y=floor_wy - 150, costume="citizen", action="shock", facing=-1, scale=1.2, t=t)


# ====================================================================
# 4. MASTER 2D FRAME COMPOSITOR (ZERO 3D, 100% POLISHED STICKMAN)
# ====================================================================
def render_master_stickman_frame(t: float, total_duration: float, topic_title: str) -> Image.Image:
    """
    Renders an ultra-polished, content-rich 2D stickman frame:
    - Zero 3D models (100% clean, crisp 2D comic stickman animation)
    - Dynamic Camera2D with punch zooms, tracking pans, and screen shakes
    - Themed historical sets and costumed characters
    - Atmospheric lighting and top category branding banner
    """
    # 1. Base Canvas
    img = Image.new("RGB", (VIDEO_WIDTH, VIDEO_HEIGHT), PALETTE["bg_dark"])
    draw = ImageDraw.Draw(img)

    p = t / total_duration
    title_lower = topic_title.lower()

    # 2. Compute Dynamic Camera Shot
    cam = get_camera_shot(t, total_duration, topic_title)

    # 3. Render Appropriate Historical Scene
    if any(k in title_lower for k in ["water", "wall", "prison", "prisoner", "escape", "soap", "tunnel"]):
        render_scene_prison_break(draw, cam, t, p)
        category_label = "🔓 THE IMPOSSIBLE ESCAPE"
    elif any(k in title_lower for k in ["beer", "flood", "london", "disaster", "molasses", "dam", "liquid"]):
        render_scene_beer_flood(draw, cam, t, p)
        category_label = "🌊 THE 15-FOOT BEER TSUNAMI"
    else:
        render_scene_courtroom_synod(draw, cam, t, p)
        category_label = "⚖️ THE MACABRE TRIAL"

    # 4. Vignette / Dark Ambient Edge Glow
    # Soft corner shadow keeps user eye locked on the center stickman!
    vignette = Image.new("RGBA", (VIDEO_WIDTH, VIDEO_HEIGHT), (0, 0, 0, 0))
    v_draw = ImageDraw.Draw(vignette)
    v_draw.rectangle([0, 0, VIDEO_WIDTH, 140], fill=(0, 0, 0, 85))
    v_draw.rectangle([0, VIDEO_HEIGHT - 120, VIDEO_WIDTH, VIDEO_HEIGHT], fill=(0, 0, 0, 110))
    img.paste(Image.alpha_composite(Image.new("RGBA", (VIDEO_WIDTH, VIDEO_HEIGHT), (0,0,0,0)), vignette), (0,0), vignette)

    # 5. Top Category Banner
    draw_final = ImageDraw.Draw(img)
    draw_final.rectangle([80, 140, VIDEO_WIDTH - 80, 230], fill=PALETTE["bg_dark"], outline=PALETTE["gold"], width=3)
    draw_final.text((VIDEO_WIDTH // 2, 185), category_label, fill=PALETTE["gold"], anchor="mm", font_size=34)

    # 6. Bottom Story Progress Bar
    prog_w = int(VIDEO_WIDTH * p)
    draw_final.rectangle([0, VIDEO_HEIGHT - 12, prog_w, VIDEO_HEIGHT], fill=PALETTE["gold"])

    return img
