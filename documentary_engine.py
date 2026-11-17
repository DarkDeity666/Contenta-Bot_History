import os
import math
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageEnhance

from config import VIDEO_WIDTH, VIDEO_HEIGHT, ASSETS_DIR

HISTORICAL_ASSETS_DIR = ASSETS_DIR / "historical_assets"

# Premium Documentary Color Palette
DOC_PALETTE = {
    "bg_dark": (10, 11, 14, 255),
    "gold": (255, 215, 0, 255),
    "border_gold": (212, 175, 55, 255),
    "crimson": (230, 57, 70, 255),
    "dark_card": (18, 20, 26, 230),
    "off_white": (245, 245, 245, 255),
    "charcoal": (30, 32, 40, 255),
}

# Typography
FONT_IMPACT = "Impact"
FONT_ARIAL_BOLD = "Arial Bold"
FONT_TREBUCHET_BOLD = "Trebuchet MS Bold"

def get_font(name: str, size: int) -> ImageFont.FreeTypeFont:
    for font_file in [f"{name.lower().replace(' ', '')}.ttf", f"{name}.ttf", "arialbd.ttf", "arial.ttf"]:
        try:
            return ImageFont.truetype(font_file, size)
        except OSError:
            continue
    return ImageFont.load_default()

_IMAGE_CACHE: Dict[str, Image.Image] = {}

def load_cached_image(path: str) -> Image.Image:
    if path not in _IMAGE_CACHE:
        if not os.path.exists(path):
            raise FileNotFoundError(f"Historical asset not found: {path}")
        im = Image.open(path).convert("RGBA")
        _IMAGE_CACHE[path] = im
    return _IMAGE_CACHE[path]

# Script #5 Timeline (Henry Tandey / WWI Hitler)
SCENE_TIMELINE_5 = [
    {
        "id": "scene_1_hook_map",
        "start": 0.0,
        "end": 9.84,
        "asset": "western_front_map.jpg",
        "category": "[ ARCHIVAL DOSSIER: WWI ]",
        "date_stamp": "SEPTEMBER 28, 1918",
        "location": "MARCOING, FRANCE",
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
        "category": "[ VICTORIA CROSS DOSSIER ]",
        "date_stamp": "5TH DUKE OF WELLINGTON'S",
        "location": "PVT. HENRY TANDEY, VC",
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
        "category": "[ THE MORAL DILEMMA ]",
        "date_stamp": "NO-MAN'S LAND, 1918",
        "location": "16TH BAVARIAN INFANTRY",
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
        "category": "[ ARTIFACT OF MEMORY ]",
        "date_stamp": "FORTUNINO MATANIA (1914)",
        "location": "MENIN CROSSROADS",
        "headline": "THE PAINTING HITLER KEPT",
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
        "category": "[ THE BERGHOF ENCOUNTER ]",
        "date_stamp": "SEPTEMBER 15, 1938",
        "location": "OBERSALZBERG, BAVARIA",
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
        "category": "[ HISTORICAL FACT-CHECK ]",
        "date_stamp": "REGIMENTAL WAR LOGS",
        "location": "UNITS 50 MILES APART",
        "headline": "THE MYTH OF PROVIDENCE",
        "zoom_start": 1.08,
        "zoom_end": 1.0,
        "pan_start": (0.0, -30.0),
        "pan_end": (0.0, 0.0),
        "overlay_type": "fact_check_verdict"
    }
]

# Script #6 Timeline (The Bureaucracy of the Holocaust)
SCENE_TIMELINE_6 = [
    {
        "id": "scene_1_wannsee_villa",
        "start": 0.0,
        "end": 14.50,
        "asset": "wannsee_villa.jpg",
        "category": "[ ARCHIVAL DOSSIER: WANNSEE 1942 ]",
        "date_stamp": "JANUARY 20, 1942",
        "location": "GROSSER WANNSEE, BERLIN",
        "headline": "THE 90-MINUTE MEETING",
        "zoom_start": 1.0,
        "zoom_end": 1.15,
        "pan_start": (0.0, 15.0),
        "pan_end": (0.0, -15.0),
        "overlay_type": "villa_badge"
    },
    {
        "id": "scene_2_wannsee_protocol",
        "start": 14.50,
        "end": 25.90,
        "asset": "wannsee_protocol.jpg",
        "category": "[ DECLASSIFIED EVIDENCE ]",
        "date_stamp": "PROTOKOLL DER KONFERENZ",
        "location": "15-PAGE EICHMANN MINUTES",
        "headline": "THE BUREAUCRACY OF GENOCIDE",
        "zoom_start": 1.02,
        "zoom_end": 1.16,
        "pan_start": (0.0, 25.0),
        "pan_end": (0.0, -20.0),
        "overlay_type": "protocol_badge"
    },
    {
        "id": "scene_3_deportation_railway",
        "start": 25.90,
        "end": 36.80,
        "asset": "deportation_railway.jpg",
        "category": "[ REICHSBAHN LOGISTICS ]",
        "date_stamp": "DEUTSCHE REICHSBAHN",
        "location": "BIRKENAU RAILWAY SPUR",
        "headline": "THIRD-CLASS FARES PER KILOMETER",
        "zoom_start": 1.0,
        "zoom_end": 1.18,
        "pan_start": (0.0, 20.0),
        "pan_end": (0.0, -10.0),
        "overlay_type": "railway_hud"
    },
    {
        "id": "scene_4_auschwitz_blueprint",
        "start": 36.80,
        "end": 52.00,
        "asset": "auschwitz_blueprint.jpg",
        "category": "[ INDUSTRIAL BLUEPRINTS ]",
        "date_stamp": "ZENTRALBAULEITUNG SS",
        "location": "AUSCHWITZ-BIRKENAU",
        "headline": "CORPORATE CONTRACTS & BLUEPRINTS",
        "zoom_start": 1.04,
        "zoom_end": 1.16,
        "pan_start": (-35.0, 0.0),
        "pan_end": (35.0, 0.0),
        "overlay_type": "blueprint_badge"
    },
    {
        "id": "scene_5_nuremberg_courtroom",
        "start": 52.00,
        "end": 64.50,
        "asset": "nuremberg_courtroom.jpg",
        "category": "[ THE NUREMBERG TRIBUNAL ]",
        "date_stamp": "NOVEMBER 1945",
        "location": "PALACE OF JUSTICE, NUREMBERG",
        "headline": "THE SURVIVING PAPER TRAIL",
        "zoom_start": 1.0,
        "zoom_end": 1.15,
        "pan_start": (-20.0, 10.0),
        "pan_end": (20.0, -10.0),
        "overlay_type": "nuremberg_badge"
    },
    {
        "id": "scene_6_holocaust_memorial",
        "start": 64.50,
        "end": 76.50,
        "asset": "holocaust_memorial.jpg",
        "category": "[ HISTORICAL RECORD ]",
        "date_stamp": "BERLIN HISTORICAL MEMORIAL",
        "location": "SOLEMN COMMEMORATION",
        "headline": "THE BUREAUCRACY OF EVIL",
        "zoom_start": 1.10,
        "zoom_end": 1.0,
        "pan_start": (0.0, -20.0),
        "pan_end": (0.0, 10.0),
        "overlay_type": "memorial_badge"
    }
]

TIMELINES = {
    5: SCENE_TIMELINE_5,
    6: SCENE_TIMELINE_6
}

def render_documentary_frame(cur_t: float, total_duration: float, script_id: int = 6) -> Image.Image:
    """
    Renders an authentic, broadcast-grade 2.5D documentary short frame (1080x1920):
    - Real public-domain historical portraits, paintings, blueprints, and maps
    - Ambient blurred mirror background (zero black gaps or awkward stretching)
    - Foreground hero image with subtle gold archival border and drop shadow
    - Continuous smooth Ken Burns motion (subtle scale & pan)
    - Safe-area compliance: hero placed high enough so badges never collide with lower-third subtitles
    - Archival HUD callout cards and date/location tags
    - Cinematic corner vignette and bottom narrative progress bar
    """
    timeline = TIMELINES.get(script_id, SCENE_TIMELINE_6)
    
    # 1. Determine active scene
    scene = timeline[-1]
    for sc in timeline:
        if sc["start"] <= cur_t < sc["end"]:
            scene = sc
            break

    scene_dur = max(0.1, scene["end"] - scene["start"])
    p_scene = max(0.0, min(1.0, (cur_t - scene["start"]) / scene_dur))
    global_p = max(0.0, min(1.0, cur_t / total_duration))

    # 2. Compute smooth Ken Burns interpolation
    ease_p = 0.5 - 0.5 * math.cos(p_scene * math.pi)
    zoom = scene["zoom_start"] + (scene["zoom_end"] - scene["zoom_start"]) * ease_p
    pan_x = scene["pan_start"][0] + (scene["pan_end"][0] - scene["pan_start"][0]) * ease_p
    pan_y = scene["pan_start"][1] + (scene["pan_end"][1] - scene["pan_start"][1]) * ease_p

    # Load hero historical asset
    asset_path = str(HISTORICAL_ASSETS_DIR / scene["asset"])
    hero_raw = load_cached_image(asset_path)

    # 3. Create 1080x1920 Base Canvas
    canvas = Image.new("RGBA", (VIDEO_WIDTH, VIDEO_HEIGHT), DOC_PALETTE["bg_dark"])

    # 4. Atmospheric Blurred Background Layer (Fills entire 9:16 frame seamlessly)
    im_w, im_h = hero_raw.size
    cover_scale = max(VIDEO_WIDTH / im_w, VIDEO_HEIGHT / im_h) * 1.05
    bg_w = int(im_w * cover_scale)
    bg_h = int(im_h * cover_scale)
    bg_resized = hero_raw.resize((bg_w, bg_h), Image.Resampling.BILINEAR)
    
    bg_left = (bg_w - VIDEO_WIDTH) // 2
    bg_top = (bg_h - VIDEO_HEIGHT) // 2
    bg_cropped = bg_resized.crop((bg_left, bg_top, bg_left + VIDEO_WIDTH, bg_top + VIDEO_HEIGHT))
    
    bg_blurred = bg_cropped.filter(ImageFilter.GaussianBlur(radius=32))
    dark_tint = Image.new("RGBA", (VIDEO_WIDTH, VIDEO_HEIGHT), (12, 14, 18, 160))
    bg_blurred.alpha_composite(dark_tint)
    canvas.paste(bg_blurred, (0, 0))

    # 5. Foreground Hero Layer (Safe-area fit: max height 940 to leave lower third completely open)
    max_hero_w = 920
    max_hero_h = 940
    fit_scale = min(max_hero_w / im_w, max_hero_h / im_h) * zoom
    
    hero_w = int(im_w * fit_scale)
    hero_h = int(im_h * fit_scale)
    hero_scaled = hero_raw.resize((hero_w, hero_h), Image.Resampling.LANCZOS)

    # Position hero centered at Y=800 (spans ~330 to 1270)
    hero_cx = (VIDEO_WIDTH // 2) + int(pan_x)
    hero_cy = 800 + int(pan_y)
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

    # Archival Gold & White Double Border around hero
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

    # Scene-Specific Interactive Overlays (b_y sits right below hero, leaves 150px gap before captions at Y=1530)
    b_y = hero_y + hero_h + 16

    # Script #5 overlays
    if scene["overlay_type"] == "sniper_hud":
        ch_x = hero_cx
        ch_y = hero_cy
        ch_r = 95
        pulse = math.sin(cur_t * 5.0) * 8
        draw.ellipse([ch_x - ch_r - pulse, ch_y - ch_r - pulse, ch_x + ch_r + pulse, ch_y + ch_r + pulse], outline=DOC_PALETTE["crimson"], width=3)
        draw.line([(ch_x - ch_r - 30, ch_y), (ch_x + ch_r + 30, ch_y)], fill=DOC_PALETTE["crimson"], width=2)
        draw.line([(ch_x, ch_y - ch_r - 30), (ch_x, ch_y + ch_r + 30)], fill=DOC_PALETTE["crimson"], width=2)
        draw.text((ch_x, ch_y - ch_r - 28), "TARGET LOCATED: MARCOING 1918", fill=DOC_PALETTE["crimson"], anchor="mm", font=font_sub)

    elif scene["overlay_type"] == "hero_badge":
        draw.rounded_rectangle([100, b_y, VIDEO_WIDTH - 100, b_y + 55], radius=6, fill=DOC_PALETTE["dark_card"], outline=DOC_PALETTE["gold"], width=2)
        draw.text((VIDEO_WIDTH // 2, b_y + 27), "HIGHEST MILITARY HONOUR: THE VICTORIA CROSS", fill=DOC_PALETTE["gold"], anchor="mm", font=font_sub)

    elif scene["overlay_type"] == "quote_card":
        draw.rounded_rectangle([70, b_y, VIDEO_WIDTH - 70, b_y + 65], radius=8, fill=(35, 25, 15, 235), outline=DOC_PALETTE["gold"], width=2)
        draw.text((VIDEO_WIDTH // 2, b_y + 22), '“THAT MAN CAME SO NEAR TO KILLING ME...”', fill=DOC_PALETTE["gold"], anchor="mm", font=font_badge)
        draw.text((VIDEO_WIDTH // 2, b_y + 48), '— ADOLF HITLER TO NEVILLE CHAMBERLAIN (1938)', fill=DOC_PALETTE["off_white"], anchor="mm", font=font_sub)

    elif scene["overlay_type"] == "fact_check_verdict":
        draw.rounded_rectangle([80, b_y, VIDEO_WIDTH - 80, b_y + 55], radius=8, fill=(45, 18, 18, 240), outline=DOC_PALETTE["crimson"], width=2)
        draw.text((VIDEO_WIDTH // 2, b_y + 27), 'HISTORICAL FACT-CHECK: UNITS WERE 50 MILES APART', fill=DOC_PALETTE["crimson"], anchor="mm", font=font_badge)

    # Script #6 overlays
    elif scene["overlay_type"] == "villa_badge":
        draw.rounded_rectangle([90, b_y, VIDEO_WIDTH - 90, b_y + 55], radius=6, fill=DOC_PALETTE["dark_card"], outline=DOC_PALETTE["gold"], width=2)
        draw.text((VIDEO_WIDTH // 2, b_y + 27), "SITE OF THE WANNSEE CONFERENCE (1942)", fill=DOC_PALETTE["gold"], anchor="mm", font=font_sub)

    elif scene["overlay_type"] == "protocol_badge":
        draw.rounded_rectangle([80, b_y, VIDEO_WIDTH - 80, b_y + 55], radius=6, fill=DOC_PALETTE["dark_card"], outline=DOC_PALETTE["gold"], width=2)
        draw.text((VIDEO_WIDTH // 2, b_y + 27), "EXHIBIT: OFFICIAL 15-PAGE EICHMANN PROTOCOL", fill=DOC_PALETTE["gold"], anchor="mm", font=font_sub)

    elif scene["overlay_type"] == "railway_hud":
        draw.rounded_rectangle([70, b_y, VIDEO_WIDTH - 70, b_y + 55], radius=6, fill=(35, 18, 18, 240), outline=DOC_PALETTE["crimson"], width=2)
        draw.text((VIDEO_WIDTH // 2, b_y + 27), "REICHSBAHN: CHARGED PER KM IN PASSENGER FARES", fill=DOC_PALETTE["crimson"], anchor="mm", font=font_sub)

    elif scene["overlay_type"] == "blueprint_badge":
        draw.rounded_rectangle([80, b_y, VIDEO_WIDTH - 80, b_y + 55], radius=6, fill=DOC_PALETTE["dark_card"], outline=DOC_PALETTE["gold"], width=2)
        draw.text((VIDEO_WIDTH // 2, b_y + 27), "ARCHITECTURAL BLUEPRINTS: DISCOVERED IN BERLIN", fill=DOC_PALETTE["gold"], anchor="mm", font=font_sub)

    elif scene["overlay_type"] == "nuremberg_badge":
        draw.rounded_rectangle([70, b_y, VIDEO_WIDTH - 70, b_y + 55], radius=6, fill=(35, 18, 18, 240), outline=DOC_PALETTE["crimson"], width=2)
        draw.text((VIDEO_WIDTH // 2, b_y + 27), "NUREMBERG EVIDENCE: THE PAPER TRAIL SURVIVED", fill=DOC_PALETTE["crimson"], anchor="mm", font=font_sub)

    elif scene["overlay_type"] == "memorial_badge":
        draw.rounded_rectangle([80, b_y, VIDEO_WIDTH - 80, b_y + 55], radius=6, fill=DOC_PALETTE["dark_card"], outline=DOC_PALETTE["gold"], width=2)
        draw.text((VIDEO_WIDTH // 2, b_y + 27), "HISTORICAL RECORD: COMMEMORATION & MEMORY", fill=DOC_PALETTE["gold"], anchor="mm", font=font_sub)

    # 7. Cinematic Vignette
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

if __name__ == "__main__":
    test_img = render_documentary_frame(2.0, 76.0, script_id=6)
    test_img.save("output/test_script_6_frame.png")
    print("Test frame rendered successfully.")
