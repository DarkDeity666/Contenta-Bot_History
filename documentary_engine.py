import math
import os
import json
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageEnhance

from config import (
    VIDEO_WIDTH, VIDEO_HEIGHT, FPS, OUTPUT_DIR, ASSETS_DIR
)

HISTORICAL_ASSETS_DIR = ASSETS_DIR / "historical_assets"

# Typography settings
FONT_IMPACT = "C:/Windows/Fonts/impact.ttf"
FONT_ARIAL_BOLD = "C:/Windows/Fonts/arialbd.ttf"
FONT_TREBUCHET_BOLD = "C:/Windows/Fonts/trebucbd.ttf"

def get_font(path: str, size: int) -> ImageFont.FreeTypeFont:
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()

# Color palette for 2.5D documentary motion graphics
DOC_PALETTE = {
    "bg_dark": (14, 16, 20),
    "gold": (255, 215, 0),
    "gold_dim": (205, 165, 30),
    "crimson": (225, 45, 45),
    "cyan": (0, 225, 255),
    "white": (255, 255, 255),
    "off_white": (240, 240, 245),
    "dark_card": (18, 20, 25, 215),
    "border_gold": (212, 175, 55),
    "shadow": (0, 0, 0, 160)
}

# Image cache to prevent reloading from disk every frame
_IMAGE_CACHE: Dict[str, Image.Image] = {}

def load_cached_image(path: str) -> Image.Image:
    if path not in _IMAGE_CACHE:
        if not os.path.exists(path):
            raise FileNotFoundError(f"Historical asset not found: {path}")
        im = Image.open(path).convert("RGBA")
        _IMAGE_CACHE[path] = im
    return _IMAGE_CACHE[path]

# Scene definitions with exact historical asset routing & editorial staging
SCENE_TIMELINE = [
    {
        "id": "scene_1_hook_map",
        "start": 0.0,
        "end": 9.84,
        "asset": "western_front_map.jpg",
        "category": "⚔️ WWI UNTOLD HISTORY",
        "date_stamp": "📅 SEPTEMBER 28, 1918",
        "location": "📍 MARCOING, NORTHERN FRANCE",
        "headline": "THE CROSSHAIRS OF DESTINY",
        "zoom_start": 1.0,
        "zoom_end": 1.18,
        "pan_start": (0.0, 0.0),
        "pan_end": (40.0, -25.0),
        "overlay_type": "sniper_hud"
    },
    {
        "id": "scene_2_tandey_portrait",
        "start": 9.84,
        "end": 15.42,
        "asset": "tandey_portrait.jpg",
        "category": "🎖️ VICTORIA CROSS RECIPIENT",
        "date_stamp": "📅 5TH DUKE OF WELLINGTON'S REGT",
        "location": "🎖️ PRIVATE HENRY TANDEY, VC",
        "headline": "BRITAIN'S MOST DECORATED PRIVATE",
        "zoom_start": 1.02,
        "zoom_end": 1.15,
        "pan_start": (0.0, 20.0),
        "pan_end": (0.0, -15.0),
        "overlay_type": "hero_badge"
    },
    {
        "id": "scene_3_hitler_ww1",
        "start": 15.42,
        "end": 26.30,
        "asset": "hitler_ww1.jpg",
        "category": "🕊️ THE MORAL DILEMMA",
        "date_stamp": "📅 SEPTEMBER 1918 (NO-MAN'S LAND)",
        "location": "📍 BAVARIAN 16TH RESERVE INFANTRY",
        "headline": "A WOUNDED CORPORAL SPARED",
        "zoom_start": 1.0,
        "zoom_end": 1.16,
        "pan_start": (-30.0, 10.0),
        "pan_end": (20.0, -20.0),
        "overlay_type": "mercy_highlight"
    },
    {
        "id": "scene_4_matania_painting",
        "start": 26.30,
        "end": 34.54,
        "asset": "matania_painting.jpg",
        "category": "🎨 THE HISTORIC PAINTING",
        "date_stamp": "📅 FORTUNINO MATANIA (1914)",
        "location": "🖼️ MENIN CROSSROADS",
        "headline": "THE IMAGE HITLER NEVER FORGOT",
        "zoom_start": 1.0,
        "zoom_end": 1.15,
        "pan_start": (-50.0, 0.0),
        "pan_end": (50.0, 0.0),
        "overlay_type": "painting_callout"
    },
    {
        "id": "scene_5_chamberlain_berghof",
        "start": 34.54,
        "end": 51.74,
        "asset": "chamberlain_hitler_1938.jpg",
        "category": "⛰️ THE BERGHOF ENCOUNTER",
        "date_stamp": "📅 SEPTEMBER 15, 1938",
        "location": "⛰️ OBERSALZBERG, BAVARIAN ALPS",
        "headline": "CHAMBERLAIN SEES THE PAINTING",
        "zoom_start": 1.0,
        "zoom_end": 1.14,
        "pan_start": (-25.0, 15.0),
        "pan_end": (25.0, -15.0),
        "overlay_type": "quote_card"
    },
    {
        "id": "scene_6_myth_check",
        "start": 51.74,
        "end": 64.23,
        "asset": "chamberlain_newspaper.jpg",
        "category": "🔍 ACADEMIC FACT-CHECK",
        "date_stamp": "📜 WAR DIARIES & DISLOCATION",
        "location": "🔍 UNITS 50 MILES APART",
        "headline": "THE MYTH OF PROVIDENCE",
        "zoom_start": 1.08,
        "zoom_end": 1.0,
        "pan_start": (0.0, -30.0),
        "pan_end": (0.0, 0.0),
        "overlay_type": "fact_check_verdict"
    }
]

def render_documentary_frame(cur_t: float, total_duration: float) -> Image.Image:
    """
    Renders an authentic, broadcast-grade 2.5D documentary short frame (1080x1920):
    - Real public-domain historical portraits, paintings, and maps
    - Ambient blurred mirror background (zero black gaps or awkward stretching)
    - Foreground hero image with subtle gold archival border and drop shadow
    - Continuous smooth Ken Burns motion (subtle scale & pan)
    - Historical date stamp ribbons, location pins, and documentary callout cards
    - Cinematic corner vignette and subtle archival texture
    """
    # 1. Determine active scene
    scene = SCENE_TIMELINE[-1]
    for sc in SCENE_TIMELINE:
        if sc["start"] <= cur_t < sc["end"]:
            scene = sc
            break

    scene_dur = max(0.1, scene["end"] - scene["start"])
    p_scene = max(0.0, min(1.0, (cur_t - scene["start"]) / scene_dur))
    global_p = max(0.0, min(1.0, cur_t / total_duration))

    # 2. Compute smooth Ken Burns interpolation
    # Ease-in-out smooth progression
    ease_p = 0.5 - 0.5 * math.cos(p_scene * math.pi)
    zoom = scene["zoom_start"] + (scene["zoom_end"] - scene["zoom_start"]) * ease_p
    pan_x = scene["pan_start"][0] + (scene["pan_end"][0] - scene["pan_start"][0]) * ease_p
    pan_y = scene["pan_start"][1] + (scene["pan_end"][1] - scene["pan_start"][1]) * ease_p

    # Load hero historical asset
    asset_path = str(HISTORICAL_ASSETS_DIR / scene["asset"])
    hero_raw = load_cached_image(asset_path)

    # 3. Create 1080x1920 Base Canvas
    canvas = Image.new("RGBA", (VIDEO_WIDTH, VIDEO_HEIGHT), DOC_PALETTE["bg_dark"])

    # 4. Atmospheric Blurred Background Layer (Fills entire 9:16 frame seamlessly!)
    # Scale raw image to cover full 1080x1920
    im_w, im_h = hero_raw.size
    cover_scale = max(VIDEO_WIDTH / im_w, VIDEO_HEIGHT / im_h) * 1.05
    bg_w = int(im_w * cover_scale)
    bg_h = int(im_h * cover_scale)
    bg_resized = hero_raw.resize((bg_w, bg_h), Image.Resampling.BILINEAR)
    
    # Center crop to 1080x1920
    bg_left = (bg_w - VIDEO_WIDTH) // 2
    bg_top = (bg_h - VIDEO_HEIGHT) // 2
    bg_cropped = bg_resized.crop((bg_left, bg_top, bg_left + VIDEO_WIDTH, bg_top + VIDEO_HEIGHT))
    
    # Apply Gaussian Blur and dark moody tint
    bg_blurred = bg_cropped.filter(ImageFilter.GaussianBlur(radius=32))
    dark_tint = Image.new("RGBA", (VIDEO_WIDTH, VIDEO_HEIGHT), (12, 14, 18, 160))
    bg_blurred.alpha_composite(dark_tint)
    canvas.paste(bg_blurred, (0, 0))

    # 5. Foreground Hero Layer (Crisp, Framed, Floating Historical Asset)
    # Fit inside comfortable viewing safe-area (width ~920px, height ~1100px)
    max_hero_w = 920
    max_hero_h = 1060
    fit_scale = min(max_hero_w / im_w, max_hero_h / im_h) * zoom
    
    hero_w = int(im_w * fit_scale)
    hero_h = int(im_h * fit_scale)
    hero_scaled = hero_raw.resize((hero_w, hero_h), Image.Resampling.LANCZOS)

    # Position hero in middle-upper third (leaving lower third clear for kinetic captions)
    hero_cx = (VIDEO_WIDTH // 2) + int(pan_x)
    hero_cy = 840 + int(pan_y)
    hero_x = hero_cx - (hero_w // 2)
    hero_y = hero_cy - (hero_h // 2)

    # Soft 3D Drop Shadow behind hero
    shadow_pad = 40
    shadow_box = Image.new("RGBA", (hero_w + shadow_pad * 2, hero_h + shadow_pad * 2), (0, 0, 0, 0))
    s_draw = ImageDraw.Draw(shadow_box)
    s_draw.rectangle([shadow_pad, shadow_pad + 12, shadow_pad + hero_w, shadow_pad + hero_h + 12], fill=(0, 0, 0, 180))
    shadow_box = shadow_box.filter(ImageFilter.GaussianBlur(radius=24))
    canvas.alpha_composite(shadow_box, (hero_x - shadow_pad, hero_y - shadow_pad))

    # Paste hero image
    canvas.alpha_composite(hero_scaled, (hero_x, hero_y))

    # Clean Archival Gold & White Double Border around hero
    draw = ImageDraw.Draw(canvas)
    draw.rectangle([hero_x, hero_y, hero_x + hero_w, hero_y + hero_h], outline=DOC_PALETTE["border_gold"], width=3)
    draw.rectangle([hero_x + 5, hero_y + 5, hero_x + hero_w - 5, hero_y + hero_h - 5], outline=(255, 255, 255, 80), width=1)

    # 6. Documentary Graphic Overlays & Callout Badges
    font_cat = get_font(FONT_IMPACT, 34)
    font_badge = get_font(FONT_ARIAL_BOLD, 26)
    font_sub = get_font(FONT_TREBUCHET_BOLD, 22)

    # Top Category Banner (Upper-Safe Zone)
    top_y = 140
    draw.rounded_rectangle([70, top_y, VIDEO_WIDTH - 70, top_y + 80], radius=10, fill=DOC_PALETTE["dark_card"], outline=DOC_PALETTE["border_gold"], width=2)
    draw.text((VIDEO_WIDTH // 2, top_y + 40), scene["category"], fill=DOC_PALETTE["gold"], anchor="mm", font=font_cat)

    # Date Stamp & Location Ribbon (Right above hero photo)
    ribbon_y = max(240, hero_y - 65)
    draw.rounded_rectangle([80, ribbon_y, VIDEO_WIDTH - 80, ribbon_y + 50], radius=8, fill=(20, 22, 28, 230), outline=(255, 255, 255, 45), width=1)
    draw.text((105, ribbon_y + 25), scene["date_stamp"], fill=DOC_PALETTE["gold"], anchor="lm", font=font_sub)
    draw.text((VIDEO_WIDTH - 105, ribbon_y + 25), scene["location"], fill=DOC_PALETTE["off_white"], anchor="rm", font=font_sub)

    # Scene-Specific Interactive Overlays
    if scene["overlay_type"] == "sniper_hud":
        # Tactical crosshair reticle on Marcoing map
        ch_x = hero_cx
        ch_y = hero_cy
        ch_r = 95
        # Red pulsing circle
        pulse = math.sin(cur_t * 5.0) * 8
        draw.ellipse([ch_x - ch_r - pulse, ch_y - ch_r - pulse, ch_x + ch_r + pulse, ch_y + ch_r + pulse], outline=DOC_PALETTE["crimson"], width=3)
        draw.line([(ch_x - ch_r - 30, ch_y), (ch_x + ch_r + 30, ch_y)], fill=DOC_PALETTE["crimson"], width=2)
        draw.line([(ch_x, ch_y - ch_r - 30), (ch_x, ch_y + ch_r + 30)], fill=DOC_PALETTE["crimson"], width=2)
        draw.text((ch_x, ch_y - ch_r - 28), "🎯 TARGET LOCATED: MARCOING 1918", fill=DOC_PALETTE["crimson"], anchor="mm", font=font_sub)

    elif scene["overlay_type"] == "hero_badge":
        # Victoria Cross medal banner below hero
        b_y = hero_y + hero_h + 18
        draw.rounded_rectangle([100, b_y, VIDEO_WIDTH - 100, b_y + 55], radius=6, fill=DOC_PALETTE["dark_card"], outline=DOC_PALETTE["gold"], width=2)
        draw.text((VIDEO_WIDTH // 2, b_y + 27), "🎖️ HIGHEST MILITARY HONOUR: THE VICTORIA CROSS", fill=DOC_PALETTE["gold"], anchor="mm", font=font_sub)

    elif scene["overlay_type"] == "quote_card":
        # Highlighted quotation box
        q_y = hero_y + hero_h + 18
        draw.rounded_rectangle([70, q_y, VIDEO_WIDTH - 70, q_y + 75], radius=8, fill=(35, 25, 15, 235), outline=DOC_PALETTE["gold"], width=2)
        draw.text((VIDEO_WIDTH // 2, q_y + 24), '“THAT MAN CAME SO NEAR TO KILLING ME...”', fill=DOC_PALETTE["gold"], anchor="mm", font=font_badge)
        draw.text((VIDEO_WIDTH // 2, q_y + 54), '— ADOLF HITLER TO NEVILLE CHAMBERLAIN (1938)', fill=DOC_PALETTE["off_white"], anchor="mm", font=font_sub)

    elif scene["overlay_type"] == "fact_check_verdict":
        # Verdict stamp
        v_y = hero_y + hero_h + 18
        draw.rounded_rectangle([80, v_y, VIDEO_WIDTH - 80, v_y + 65], radius=8, fill=(45, 18, 18, 240), outline=DOC_PALETTE["crimson"], width=2)
        draw.text((VIDEO_WIDTH // 2, v_y + 32), '⚠️ FACT-CHECK: UNITS WERE 50 MILES APART', fill=DOC_PALETTE["crimson"], anchor="mm", font=font_badge)

    # 7. Cinematic Vignette (Subtle edge darkening for phone focus)
    vignette = Image.new("RGBA", (VIDEO_WIDTH, VIDEO_HEIGHT), (0, 0, 0, 0))
    v_draw = ImageDraw.Draw(vignette)
    v_draw.rectangle([0, 0, VIDEO_WIDTH, 120], fill=(0, 0, 0, 95))
    v_draw.rectangle([0, VIDEO_HEIGHT - 120, VIDEO_WIDTH, VIDEO_HEIGHT], fill=(0, 0, 0, 120))
    canvas.alpha_composite(vignette)

    # 8. Bottom Narrative Progress Bar
    prog_w = int(VIDEO_WIDTH * global_p)
    draw_final = ImageDraw.Draw(canvas)
    draw_final.rectangle([0, VIDEO_HEIGHT - 12, prog_w, VIDEO_HEIGHT], fill=DOC_PALETTE["gold"])

    return canvas.convert("RGB")

