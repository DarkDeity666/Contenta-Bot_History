"""
Toon Cast Generator (Python Port of claude-animated-shorts toon.ts)
Generates exact bean-head 2D cartoon character sprites (600x1000 RGBA, 2x supersampled):
- Superellipse bean heads (H/W=0.94, crown=1.75, jaw=2.3, chin taper=-0.12, side bulge)
- Thick-thin dark plum ink outline (#241726) weighted away from key light
- Soft painted shadow crescents (SH_SKIN / SH_CLOTH)
- Deadpan lidded eyes (0.26W apart, zero blush, zero eye catchlights)
- 3.5 head-height adult proportions with single-stroke stick limbs & ink-dot hands
"""

import os
import math
from typing import Dict, List, Tuple, Optional, Any
from PIL import Image, ImageDraw

INK = "#241726"
SKIN = "#ffe2c2"
WHITE = "#ffffff"
MOUTH = "#5a1e28"
TONGUE = "#e86e78"

SH_SKIN = (0.96, 0.86, 0.84)
SH_CLOTH = (0.64, 0.66, 0.74)
SH_FELT = (0.62, 0.62, 0.70)

SKINS = ["#ffe2c2", "#f5c9a0", "#ecd0b6", "#c99067"]

SCALE = 2  # 2x supersampling (draw at 1200x2000 -> Lanczos downsample to 600x1000)


def hex_to_rgba(h: str, alpha: int = 255) -> Tuple[int, int, int, int]:
    h = h.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), alpha)


def mul_col(c: str, m: Tuple[float, float, float]) -> str:
    h = c.lstrip("#")
    r = min(255, int(int(h[0:2], 16) * m[0]))
    g = min(255, int(int(h[2:4], 16) * m[1]))
    b = min(255, int(int(h[4:6], 16) * m[2]))
    return f"#{r:02x}{g:02x}{b:02x}"


def mix_col(a: str, b: str, t: float) -> str:
    ha, hb = a.lstrip("#"), b.lstrip("#")
    r = int(int(ha[0:2], 16) * (1 - t) + int(hb[0:2], 16) * t)
    g = int(int(ha[2:4], 16) * (1 - t) + int(hb[2:4], 16) * t)
    bl = int(int(ha[4:6], 16) * (1 - t) + int(hb[4:6], 16) * t)
    return f"#{r:02x}{g:02x}{bl:02x}"


def rnd(seed: int, k: int) -> float:
    x = math.sin(seed * 127.1 + k * 311.7) * 43758.5453
    return x - math.floor(x)


def curve_pts(a: Tuple[float, float], k: Tuple[float, float], b: Tuple[float, float], n: int = 12) -> List[Tuple[float, float]]:
    c = (2 * k[0] - (a[0] + b[0]) / 2, 2 * k[1] - (a[1] + b[1]) / 2)
    out = []
    for i in range(n + 1):
        t = i / n
        s = 1 - t
        out.append((s * s * a[0] + 2 * s * t * c[0] + t * t * b[0], s * s * a[1] + 2 * s * t * c[1] + t * t * b[1]))
    return out


def blob_pts(cx: float, cy: float, a: float, b: float, n_top: float, n_bot: float, egg: float, asym: float, rot: float, noise: float, seed: int, n: int = 72) -> List[Tuple[float, float]]:
    ph = [rnd(seed, 11) * math.tau, rnd(seed, 12) * math.tau, rnd(seed, 13) * math.tau]
    pts = []
    cr, sr = math.cos(rot), math.sin(rot)
    for i in range(n):
        t = (i / n) * math.tau
        c, s = math.cos(t), math.sin(t)
        e = 2.0 / (n_top if s < 0 else n_bot)
        X = math.copysign(abs(c) ** e, c)
        Y = math.copysign(abs(s) ** e, s)
        X *= (1.0 + egg * Y) * (1.0 + asym * math.copysign(1.0, X))
        r = 1.0 + noise * (math.cos(2 * t + ph[0]) + 0.7 * math.cos(3 * t + ph[1]) + 0.5 * math.cos(4 * t + ph[2]))
        x = a * X * r
        y = b * Y * r
        pts.append((cx + x * cr - y * sr, cy + x * sr + y * cr))
    return pts


def head_blob(seed: int, a: float = 118.0, facing: int = 0) -> Dict[str, float]:
    f = facing if facing != 0 else (-1 if rnd(seed, 6) < 0.5 else 1)
    return {
        "a": a,
        "b": a * (0.94 + 0.08 * (rnd(seed, 1) - 0.5)),
        "n_top": 1.75 + 0.3 * (rnd(seed, 2) - 0.5),
        "n_bot": 2.3 + 0.3 * (rnd(seed, 3) - 0.5),
        "egg": -0.12 + 0.06 * (rnd(seed, 4) - 0.5),
        "asym": (0.06 + 0.04 * rnd(seed, 5)) * f,
        "rot": math.radians(8 * (rnd(seed, 7) - 0.5)),
        "noise": 0.008,
        "seed": seed,
    }


def thick_angle(light: float) -> float:
    return math.atan2(-math.sin(light) + 0.8, -math.cos(light))


class Pen:
    def __init__(self, img: Image.Image):
        self.img = img
        self.draw = ImageDraw.Draw(img, "RGBA")
        self.rot: Optional[Tuple[float, float, float, float, float]] = None

    def P(self, x: float, y: float) -> Tuple[float, float]:
        if self.rot:
            a, cx, cy, dx, dy = self.rot
            c, s = math.cos(a), math.sin(a)
            x, y = cx + (x - cx) * c - (y - cy) * s + dx, cy + (x - cx) * s + (y - cy) * c + dy
        return (x * SCALE, y * SCALE)

    def poly(self, pts: List[Tuple[float, float]], fill: Optional[str], ol: float = 0.0, col_ol: str = INK):
        s_pts = [self.P(x, y) for x, y in pts]
        if fill:
            self.draw.polygon(s_pts, fill=hex_to_rgba(fill))
        if ol > 0:
            self.stroke_closed(pts, ol, col_ol)

    def stroke_closed(self, pts: List[Tuple[float, float]], w: float, col: str = INK):
        s_pts = [self.P(x, y) for x, y in pts]
        s_pts.append(s_pts[0])
        self.draw.line(s_pts, fill=hex_to_rgba(col), width=max(1, int(w * SCALE)), joint="curve")

    def stroke(self, pts: List[Tuple[float, float]], w: float, col: str = INK):
        if len(pts) < 2:
            return
        s_pts = [self.P(x, y) for x, y in pts]
        lw = max(1, int(w * SCALE))
        self.draw.line(s_pts, fill=hex_to_rgba(col), width=lw, joint="curve")
        # Round endcaps
        r = lw / 2.0
        for px, py in (s_pts[0], s_pts[-1]):
            self.draw.ellipse([px - r, py - r, px + r, py + r], fill=hex_to_rgba(col))

    def dot(self, x: float, y: float, r: float, col: str = INK):
        px, py = self.P(x, y)
        sr = r * SCALE
        self.draw.ellipse([px - sr, py - sr, px + sr, py + sr], fill=hex_to_rgba(col))

    def ell(self, cx: float, cy: float, rx: float, ry: float, fill: Optional[str], ol: float = 0.0, a0: float = 0.0, a1: float = 360.0):
        pts = []
        n = 40
        for i in range(n + 1):
            a = math.radians(a0 + (a1 - a0) * i / n)
            pts.append((cx + rx * math.cos(a), cy + ry * math.sin(a)))
        if a1 - a0 >= 359:
            self.poly(pts[:-1], fill, ol)
        else:
            if fill:
                self.poly(pts, fill, 0)
            if ol > 0:
                self.stroke(pts, ol, INK)

    def arc(self, cx: float, cy: float, rx: float, ry: float, a0: float, a1: float, w: float, col: str = INK):
        pts = []
        n = 28
        for i in range(n + 1):
            a = math.radians(a0 + (a1 - a0) * i / n)
            pts.append((cx + rx * math.cos(a), cy + ry * math.sin(a)))
        self.stroke(pts, w, col)

    def shaded_fill(self, pts: List[Tuple[float, float]], base: str, shadow: str, light: float, r: float):
        """Fills base + soft directional shadow crescent on the far side from key light."""
        self.poly(pts, base, 0)
        # Compute centroid
        n = len(pts)
        cx = sum(p[0] for p in pts) / n
        cy = sum(p[1] for p in pts) / n
        # Shadow layer clipped to shape
        mask = Image.new("L", self.img.size, 0)
        mdraw = ImageDraw.Draw(mask)
        mdraw.polygon([self.P(x, y) for x, y in pts], fill=255)

        sh_layer = Image.new("RGBA", self.img.size, (0, 0, 0, 0))
        sdraw = ImageDraw.Draw(sh_layer, "RGBA")
        # Draw soft crescent on shadow side
        dx = -math.cos(light) * r * 0.48
        dy = -math.sin(light) * r * 0.48
        sh_pts = [self.P(x + dx, y + dy) for x, y in pts]
        # Invert inside mask by filling whole shadow then punching base offset
        sdraw.polygon([self.P(x, y) for x, y in pts], fill=hex_to_rgba(shadow, 235))
        # Punch lit interior
        lit_mask = Image.new("L", self.img.size, 255)
        ldraw = ImageDraw.Draw(lit_mask)
        ldraw.polygon([self.P(x - dx * 0.6, y - dy * 0.6) for x, y in pts], fill=0)
        # Combine mask & lit_mask
        from PIL import ImageChops
        final_mask = ImageChops.multiply(mask, lit_mask)
        sh_layer.putalpha(final_mask)
        self.img.alpha_composite(sh_layer)
        # Re-bind draw after composite
        self.draw = ImageDraw.Draw(self.img, "RGBA")

    def ink_ring(self, pts: List[Tuple[float, float]], w0: float, thick: float, k: float = 0.45, col: str = INK):
        """Thick-thin variable ink outline weighted toward shadow side (thickAngle)."""
        n = len(pts)
        cx = sum(p[0] for p in pts) / n
        cy = sum(p[1] for p in pts) / n
        out_pts, inn_pts = [], []
        for i, q in enumerate(pts):
            a = pts[(i + n - 1) % n]
            b = pts[(i + 1) % n]
            nx, ny = b[1] - a[1], a[0] - b[0]
            l = math.hypot(nx, ny) or 1.0
            nx /= l
            ny /= l
            h = 0.5 * w0 * (1.0 + k * math.cos(math.atan2(q[1] - cy, q[0] - cx) - thick))
            out_pts.append(self.P(q[0] + nx * h, q[1] + ny * h))
            inn_pts.append(self.P(q[0] - nx * h, q[1] - ny * h))

        # Build polygon ring
        ring_mask = Image.new("L", self.img.size, 0)
        rdraw = ImageDraw.Draw(ring_mask)
        rdraw.polygon(out_pts, fill=255)
        rdraw.polygon(inn_pts, fill=0)
        ink_layer = Image.new("RGBA", self.img.size, hex_to_rgba(col, 255))
        ink_layer.putalpha(ring_mask)
        self.img.alpha_composite(ink_layer)
        self.draw = ImageDraw.Draw(self.img, "RGBA")


def taper(p: Pen, a: Tuple[float, float], b: Tuple[float, float], wa: float, wb: float, col: str = INK):
    dx, dy = b[0] - a[0], b[1] - a[1]
    l = math.hypot(dx, dy) or 1.0
    nx, ny = -dy / l, dx / l
    poly = [
        (a[0] + nx * wa / 2, a[1] + ny * wa / 2),
        (b[0] + nx * wb / 2, b[1] + ny * wb / 2),
        (b[0] - nx * wb / 2, b[1] - ny * wb / 2),
        (a[0] - nx * wa / 2, a[1] - ny * wa / 2),
    ]
    p.poly(poly, col, 0)
    p.dot(a[0], a[1], wa / 2, col)
    p.dot(b[0], b[1], wb / 2, col)


# Expression dictionary matching STYLE_BIBLE & toon.ts
FACE_MAP = {
    "neutral": {"eye": "lid", "brow": (0, -1), "mouth": "dash"},
    "stern": {"eye": "lid", "brow": (3, -2), "mouth": "frown"},
    "grin": {"eye": "happy", "brow": (-3, -3), "mouth": "grin"},
    "laugh": {"eye": "squeeze", "brow": (-4, -4), "mouth": "laugh"},
    "nervous": {"eye": "small", "brow": (-3, 2), "mouth": "wave"},
    "shock": {"eye": "shock", "brow": (-7, -6), "mouth": "O"},
    "smile": {"eye": "dot", "brow": (0, -1), "mouth": "smirk"},
}


def draw_eye(p: Pen, kind: str, x: float, ey: float, u: float, side: int, look: float):
    lx = x + look * 3 * u
    lw = 3.8 * u
    if kind == "dot":
        p.ell(lx, ey, 3.8 * u, 5.5 * u, INK, 0)
    elif kind == "small":
        p.ell(lx, ey, 3.0 * u, 4.4 * u, INK, 0)
    elif kind == "lid":
        # Deadpan half-disc lidded eye (zero catchlights!)
        p.ell(lx, ey - u, 7 * u, 6 * u, INK, 0, 0, 180)
        p.stroke([(x - 9 * u, ey - u), (x + 9 * u, ey - u)], lw)
    elif kind == "happy":
        p.arc(x, ey + 3 * u, 8 * u, 6 * u, 200, 340, lw)
    elif kind == "dash":
        p.stroke([(x - 8.5 * u, ey), (x + 8.5 * u, ey)], lw)
    elif kind == "squeeze":
        p.stroke([(x + 6 * u * side, ey - 5 * u), (x - 6 * u * side, ey), (x + 6 * u * side, ey + 5 * u)], lw)
    elif kind == "shock":
        p.ell(x, ey, 11 * u, 11 * u, WHITE, 2.6 * u)
        p.dot(lx - side * 1.5 * u, ey + 1.5 * u, 3 * u)


def draw_mouth(p: Pen, kind: str, mx: float, my: float, u: float):
    mw = 4.0 * u
    if kind == "dash":
        p.stroke([(mx - 5.5 * u, my), (mx + 5.5 * u, my - 0.8 * u)], mw)
    elif kind == "frown":
        p.arc(mx, my + 3 * u, 6.5 * u, 3.5 * u, 200, 340, mw)
    elif kind == "smirk":
        p.arc(mx + u, my - 3 * u, 7 * u, 4 * u, 10, 150, mw)
    elif kind == "grin":
        p.ell(mx, my - u, 12 * u, 8 * u, MOUTH, 2.8 * u, 0, 180)
    elif kind == "laugh":
        p.ell(mx, my, 15 * u, 10 * u, MOUTH, 2.8 * u, 0, 180)
        p.ell(mx + 2 * u, my + 5 * u, 6 * u, 3 * u, TONGUE, 0)
    elif kind == "O":
        p.ell(mx, my + 2 * u, 9 * u, 11 * u, MOUTH, 3.2 * u)
    elif kind == "wave":
        pts = [(mx - 9 * u + i * 1.5 * u, my + 1.5 * u * math.sin(i * 1.3)) for i in range(13)]
        p.stroke(pts, 3 * u)


def render_character_card(
    out_path: str,
    jacket: str = "#3b4252",
    pants: str = "#2e3440",
    boots: str = INK,
    hat: Optional[str] = "fedora",
    skin: str = SKIN,
    expr: str = "neutral",
    mode: str = "stand",
    phase: float = 0.0,
    facing: int = 1,
    look: float = 0.0,
    blink: bool = False,
    wave: Optional[float] = None,
    prop: Optional[str] = None,
    seed: int = 1,
) -> str:
    """Renders a 600x1000 toon.ts-accurate 2D character sprite card to PNG."""
    canvas = Image.new("RGBA", (600 * SCALE, 1000 * SCALE), (0, 0, 0, 0))
    p = Pen(canvas)

    light = math.radians(-120)
    thick = thick_angle(light)

    H = head_blob(seed, 118.0, facing)
    W = 2 * H["a"]
    HH = 2 * H["b"]
    u = W / 100.0
    ow = 5.0 * u

    torso_h = 1.1 * HH
    legs_h = 1.4 * HH
    tall = (1.0 + 1.1 + 1.4) * HH
    sole = 975.0

    two = math.tau
    bob = 0.025 * tall * math.cos(2 * two * phase) if mode == "march" else (0.015 * tall * math.cos(2 * two * phase) if mode == "stroll" else 0.0)
    torso_bot = sole - legs_h + bob
    chin = torso_bot - torso_h
    hc = chin - H["b"]
    crown = hc - H["b"]
    hip_y = torso_bot - 0.12 * HH

    leg_col = mix_col(pants, INK, 0.55)
    arm_col = mix_col(jacket, INK, 0.50)
    leg_w = 5.8 * u
    foot_w = 7.5 * u

    # 1. Legs & Boots
    lift_amt = 60.0 * (1.25 if mode == "march" else 0.55 if mode == "stroll" else 0.0)
    for side, ph in ((-1, 0.0), (1, 0.5)):
        up = max(0.0, math.sin(two * (phase + ph))) * lift_amt
        hx, fx, fy = 300 + side * 15 * u, 300 + side * 22 * u, sole - 4 * u - up
        kx = (hx + fx) / 2 + side * (1.5 * u + up * 0.16)
        ky = (hip_y + fy) / 2 - up * 0.08
        p.stroke(curve_pts((hx, hip_y), (kx, ky), (fx, fy)), leg_w, leg_col)
        if boots != INK:
            p.stroke([(fx - side * 3 * u, fy), (fx + side * 13 * u, fy + 0.5 * u)], foot_w + 3, INK)
        p.stroke([(fx - side * 3 * u, fy), (fx + side * 13 * u, fy + 0.5 * u)], foot_w, boots)

    # 2. Upper Body Tilt / Sway
    sway = 1.6 * math.sin(two * phase) if mode == "march" else (1.0 * math.sin(two * phase) if mode == "stroll" else 0.0)
    p.rot = (math.radians(sway), 300.0, hip_y, 0.0, 0.0) if sway else None

    ta = (0.8 / 2.0) * W / 1.06
    tb = 0.5 * (torso_bot - (chin - 0.25 * HH))
    tcx, tcy = 300 + 3 * u * facing, torso_bot - tb
    tp = blob_pts(tcx, tcy, ta, tb, 2.2, 2.6, 0.12, 0.04 * facing, 0.0, 0.006, seed + 7)

    def shoulder(side: int) -> Tuple[float, float]:
        return (tcx + side * 0.85 * ta, chin + 0.12 * HH)

    def hang_arm(side: int, fwd: float) -> Tuple[Tuple[float, float], Tuple[float, float], Tuple[float, float]]:
        S = shoulder(side)
        ex = tcx + side * (1.12 * ta + 4 * u)
        hx = ex + side * 3 * u - side * 6 * u * max(0.0, fwd) + side * 4 * u * max(0.0, -fwd)
        return (S, (ex, S[1] + 0.48 * HH), (hx, chin + 1.04 * HH - abs(fwd) * 9 * u))

    sw = math.sin(two * phase) if mode in ("march", "stroll") else 0.0
    arm_l = hang_arm(-1, -sw)
    if wave is not None:
        S = shoulder(1)
        arm_r = (S, (tcx + 1.1 * ta + 10 * u + 3 * u * wave, S[1] - 0.22 * HH), (tcx + 1.18 * ta + 16 * u + 12 * u * wave, S[1] - 0.6 * HH))
    elif prop == "mic":
        S = shoulder(1)
        arm_r = (S, (tcx + 1.08 * ta + 8 * u, S[1] + 0.15 * HH), (tcx + 0.65 * ta, S[1] - 0.18 * HH))
    elif prop == "radio":
        S = shoulder(1)
        arm_r = (S, (tcx + 1.05 * ta + 4 * u, S[1] + 0.35 * HH), (tcx + 0.65 * ta, S[1] + 0.28 * HH))
    else:
        arm_r = hang_arm(1, sw)

    for arm in (arm_l,):
        p.stroke(curve_pts(*arm), 5.2 * u, arm_col)
        p.dot(arm[2][0], arm[2][1], 5.5 * u, INK)
    if prop not in ("mic", "radio", "dollar"):
        p.stroke(curve_pts(*arm_r), 5.2 * u, arm_col)
        p.dot(arm_r[2][0], arm_r[2][1], 5.5 * u, INK)

    # Torso shaded fill + ink ring + collar/buttons
    p.shaded_fill(tp, jacket, mul_col(jacket, SH_CLOTH), light, ta)
    for i in range(3):
        by = chin + 0.18 * HH + i * 0.22 * HH
        p.dot(tcx + 2 * u * facing, by, 2.8 * u, INK)
        p.dot(tcx + 2 * u * facing, by, 2.0 * u, "#d9dde0")
    p.ink_ring(tp, ow, thick)

    # Front arm + Props held in hand
    if prop in ("mic", "radio", "dollar"):
        p.stroke(curve_pts(*arm_r), 5.2 * u, arm_col)
        p.dot(arm_r[2][0], arm_r[2][1], 5.5 * u, INK)
        hx, hy = arm_r[2]
        if prop == "mic":
            p.stroke([(hx, hy + 10 * u), (hx + 4 * u, hy - 28 * u)], 3.8 * u, "#44444a")
            p.ell(hx + 5 * u, hy - 34 * u, 8 * u, 10 * u, "#9aa0aa", 2.2 * u)
        elif prop == "dollar":
            p.poly([(hx - 16 * u, hy - 20 * u), (hx + 20 * u, hy - 20 * u), (hx + 20 * u, hy + 2 * u), (hx - 16 * u, hy + 2 * u)], "#6cc26f", 2.4 * u)

    # 3. Head (Rotates with body sway)
    p.rot = (math.radians(sway), 300.0, hip_y, 0.0, 0.0) if sway else None
    hp = blob_pts(300, hc, H["a"], H["b"], H["n_top"], H["n_bot"], H["egg"], H["asym"], H["rot"], H["noise"], seed)
    p.shaded_fill(hp, skin, mul_col(skin, SH_SKIN), light, H["a"])
    p.ink_ring(hp, ow, thick)

    # Hat / Hair
    if hat == "fedora":
        yb = crown + 0.17 * HH
        ht = 0.42 * HH
        wb, wt = 0.34 * W, 0.28 * W
        body = [(300 - wb, yb), (300 - wt, yb - ht), (300 + wt, yb - ht), (300 + wb, yb)]
        p.shaded_fill(body, "#3b3842", mul_col("#3b3842", SH_FELT), light, wt)
        p.poly(body, None, ow * 0.85)
        p.ell(300, yb + 2 * u, 0.48 * W, 0.055 * HH, "#27242d", ow * 0.85)
    elif hat == "tophat":
        yb = crown + 0.22 * HH
        ht = 0.75 * HH
        wb, wt = 0.31 * W, 0.33 * W
        body = [(300 - wb, yb), (300 - wt, yb - ht), (300 + wt, yb - ht), (300 + wb, yb)]
        p.shaded_fill(body, "#2e2a36", mul_col("#2e2a36", SH_FELT), light, wt)
        p.poly(body, None, ow * 0.85)
        p.ell(300, yb + 1 * u, 0.45 * W, 0.05 * HH, "#1d1b22", ow * 0.85)
    elif hat == "hair":
        cut = crown + 0.40 * HH
        arc = [(x, y) for x, y in hp if y < cut]
        if len(arc) >= 3:
            p.shaded_fill(arc, "#4a3328", mul_col("#4a3328", SH_FELT), light, H["a"])
            p.poly(arc, None, ow * 0.85)
    elif hat == "officer_cap":
        yb = crown + 0.26 * HH
        ht = 0.36 * HH
        body = [(300 - 0.38 * W, yb), (300 - 0.44 * W, yb - ht), (300 + 0.44 * W, yb - ht), (300 + 0.38 * W, yb)]
        p.shaded_fill(body, "#4a4640", mul_col("#4a4640", SH_FELT), light, 0.44 * W)
        p.poly(body, None, ow * 0.85)
        p.ell(300 + 6 * u * facing, yb + 3 * u, 0.36 * W, 0.045 * HH, "#16171b", 2.2 * u, 0, 180)

    # 4. Face (Exact toon.ts proportions: eyes 26u apart, zero blush, zero catchlights!)
    F = FACE_MAP.get(expr, FACE_MAP["neutral"])
    fx = 300 + 7 * u * facing
    ex = (12.0 if F["eye"] == "shock" else 13.0) * u
    ey = hc
    ekind = "dash" if blink and F["eye"] not in ("happy", "squeeze") else F["eye"]

    for side in (-1, 1):
        x = fx + side * ex
        draw_eye(p, ekind, x, ey, u, side, look)
        dI, dO = F["brow"]
        by = ey - (17.0 if hat in ("fedora", "tophat", "officer_cap") else 20.0) * u
        if ekind == "shock":
            p.arc(x, by - 6 * u, 9 * u, 3 * u, 200, 340, 4 * u)
        else:
            taper(p, (x - side * 8.5 * u, by + dI * u), (x + side * 8.5 * u, by + dO * u), 5 * u, 2.5 * u)

    mx = 300 + 8 * u * facing
    my = hc + 20 * u
    draw_mouth(p, F["mouth"], mx, my, u)

    p.rot = None

    final = canvas.resize((600, 1000), Image.Resampling.LANCZOS)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    final.save(out_path)
    return out_path
