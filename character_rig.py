from PIL import Image, ImageDraw
from pathlib import Path
from config import ASSETS_DIR

CHAR_DIR = ASSETS_DIR / "character"
CHAR_DIR.mkdir(parents=True, exist_ok=True)

def draw_oversimplified_character(pose: str = "talking") -> str:
    """
    Renders a stylized 2D OverSimplified-style historian mascot with transparent background.
    Poses: 'talking', 'shocked', 'scheming', 'point'
    """
    width, height = 400, 500
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Palette
    SKIN = (255, 224, 189, 255)
    OUTLINE = (20, 20, 20, 255)
    COAT = (35, 45, 65, 255)      # Navy blue scholarly coat
    SHIRT = (240, 240, 240, 255)
    CROWN_GOLD = (230, 180, 30, 255)

    # 1. Body & Coat
    # Coat body
    draw.polygon([(120, 300), (280, 300), (330, 500), (70, 500)], fill=COAT, outline=OUTLINE, width=6)
    # White collar
    draw.polygon([(160, 300), (240, 300), (200, 360)], fill=SHIRT, outline=OUTLINE, width=5)
    # Tie/cravat
    draw.polygon([(185, 360), (215, 360), (220, 440), (200, 470), (180, 440)], fill=(180, 40, 40, 255), outline=OUTLINE, width=4)

    # 2. Arms & Gestures
    if pose == "shocked":
        # Hands on cheeks / head
        draw.line([(120, 320), (80, 240), (120, 180)], fill=COAT, width=28)
        draw.line([(120, 320), (80, 240), (120, 180)], fill=OUTLINE, width=6)
        draw.line([(280, 320), (320, 240), (280, 180)], fill=COAT, width=28)
        draw.line([(280, 320), (320, 240), (280, 180)], fill=OUTLINE, width=6)
        # Small hands
        draw.ellipse([105, 165, 135, 195], fill=SKIN, outline=OUTLINE, width=5)
        draw.ellipse([265, 165, 295, 195], fill=SKIN, outline=OUTLINE, width=5)
    elif pose == "point":
        # Right hand pointing upwards
        draw.line([(280, 320), (350, 270), (360, 180)], fill=COAT, width=28)
        draw.ellipse([345, 160, 375, 190], fill=SKIN, outline=OUTLINE, width=5)
        # Left hand down
        draw.line([(120, 320), (90, 400)], fill=COAT, width=26)
        draw.ellipse([75, 390, 105, 420], fill=SKIN, outline=OUTLINE, width=5)
    else:  # talking
        # Left hand gesturing forward
        draw.line([(120, 320), (80, 360), (60, 320)], fill=COAT, width=26)
        draw.ellipse([45, 305, 75, 335], fill=SKIN, outline=OUTLINE, width=5)
        # Right hand resting
        draw.line([(280, 320), (310, 380)], fill=COAT, width=26)
        draw.ellipse([295, 370, 325, 400], fill=SKIN, outline=OUTLINE, width=5)

    # 3. Head (OverSimplified round minimalist head)
    head_bbox = [110, 100, 290, 280]
    draw.ellipse(head_bbox, fill=SKIN, outline=OUTLINE, width=6)

    # 4. Hair / Scholar Wig
    draw.arc([105, 95, 295, 260], 190, 350, fill=OUTLINE, width=14)

    # 5. Eyes & Expression
    if pose == "shocked":
        # Giant shocked eyes
        draw.ellipse([140, 140, 185, 195], fill=(255, 255, 255), outline=OUTLINE, width=5)
        draw.ellipse([215, 140, 260, 195], fill=(255, 255, 255), outline=OUTLINE, width=5)
        # Tiny pupils
        draw.ellipse([160, 162, 172, 174], fill=OUTLINE)
        draw.ellipse([230, 162, 242, 174], fill=OUTLINE)
        # Wide O-shaped mouth
        draw.ellipse([180, 210, 220, 255], fill=(160, 30, 30), outline=OUTLINE, width=5)
    elif pose == "point":
        # Winking / confident eyes
        draw.ellipse([145, 160, 175, 190], fill=(255, 255, 255), outline=OUTLINE, width=5)
        draw.ellipse([155, 170, 165, 180], fill=OUTLINE)
        # Wink on other eye
        draw.line([(220, 175), (250, 175)], fill=OUTLINE, width=6)
        # Confident smirk
        draw.arc([175, 195, 225, 230], 10, 170, fill=OUTLINE, width=6)
    else:  # talking
        # Normal expressive eyes
        draw.ellipse([145, 155, 178, 190], fill=(255, 255, 255), outline=OUTLINE, width=5)
        draw.ellipse([222, 155, 255, 190], fill=(255, 255, 255), outline=OUTLINE, width=5)
        draw.ellipse([156, 166, 168, 178], fill=OUTLINE)
        draw.ellipse([233, 166, 245, 178], fill=OUTLINE)
        # Eyebrows
        draw.line([(140, 145), (175, 140)], fill=OUTLINE, width=5)
        draw.line([(225, 140), (260, 145)], fill=OUTLINE, width=5)
        # Animated open mouth
        draw.chord([180, 205, 220, 235], 0, 180, fill=(150, 20, 20), outline=OUTLINE, width=5)

    # 6. Monocle on right eye (for classy historian feel)
    draw.ellipse([215, 150, 260, 195], outline=CROWN_GOLD, width=5)
    draw.line([(260, 172), (280, 240)], fill=CROWN_GOLD, width=3)

    out_path = CHAR_DIR / f"mascot_{pose}.png"
    img.save(out_path, "PNG")
    print(f"[+] Rendered 2D Mascot pose: {out_path.name}")
    return str(out_path)

def generate_all_poses():
    for p in ["talking", "shocked", "point"]:
        draw_oversimplified_character(p)

if __name__ == "__main__":
    generate_all_poses()
