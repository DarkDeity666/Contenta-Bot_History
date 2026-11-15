from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
from config import ASSETS_DIR

GFX_DIR = ASSETS_DIR / "graphics"
GFX_DIR.mkdir(parents=True, exist_ok=True)

def create_stamp(text: str, filename: str, color=(190, 35, 35, 255)):
    """Creates a vintage wax seal / rubber stamp graphic."""
    w, h = 500, 160
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Distressed border
    draw.rounded_rectangle([10, 10, w - 10, h - 10], radius=15, outline=color, width=8)
    draw.rounded_rectangle([20, 20, w - 20, h - 20], radius=10, outline=color, width=3)

    # Stamp text
    # Draw large bold text
    draw.text((w // 2, h // 2), text, fill=color, anchor="mm", font_size=42)

    out_path = GFX_DIR / filename
    img.save(out_path, "PNG")
    print(f"[+] Rendered Stamp graphic: {filename}")
    return str(out_path)

def create_crossed_swords():
    """Renders 2D crossed battle swords icon."""
    w, h = 300, 300
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    STEEL = (220, 220, 230, 255)
    GOLD = (212, 175, 55, 255)
    DARK = (30, 30, 30, 255)

    # Sword 1 (top-left to bottom-right)
    draw.line([(40, 40), (260, 260)], fill=STEEL, width=14)
    draw.line([(40, 40), (260, 260)], fill=DARK, width=2)
    # Crossguard
    draw.line([(200, 240), (240, 200)], fill=GOLD, width=12)
    # Pommel
    draw.ellipse([250, 250, 275, 275], fill=GOLD, outline=DARK, width=3)

    # Sword 2 (top-right to bottom-left)
    draw.line([(260, 40), (40, 260)], fill=STEEL, width=14)
    draw.line([(260, 40), (40, 260)], fill=DARK, width=2)
    # Crossguard
    draw.line([(100, 240), (60, 200)], fill=GOLD, width=12)
    # Pommel
    draw.ellipse([25, 250, 50, 275], fill=GOLD, outline=DARK, width=3)

    out_path = GFX_DIR / "swords_clash.png"
    img.save(out_path, "PNG")
    print(f"[+] Rendered Swords graphic: {out_path.name}")
    return str(out_path)

def generate_all_graphics():
    create_stamp("HISTORICAL FACT", "stamp_fact.png", color=(212, 175, 55, 255))
    create_stamp("100% UNTOLD", "stamp_untold.png", color=(210, 45, 45, 255))
    create_crossed_swords()

if __name__ == "__main__":
    generate_all_graphics()
