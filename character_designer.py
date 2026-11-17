import os
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

RIGS_DIR = Path("assets/character_rigs")
RIGS_DIR.mkdir(parents=True, exist_ok=True)

# Palette definitions
PALETTE = {
    "skin_light": (255, 225, 200, 255),
    "skin_shadow": (230, 190, 160, 255),
    "skin_rosy": (245, 175, 160, 255),
    "outline": (25, 20, 25, 255),
    "jester_yellow": (255, 204, 0, 255),
    "jester_yellow_dark": (215, 165, 0, 255),
    "jester_purple": (120, 35, 140, 255),
    "jester_purple_dark": (85, 20, 100, 255),
    "bell_gold": (255, 220, 60, 255),
    "king_crimson": (175, 25, 35, 255),
    "king_crimson_dark": (125, 15, 22, 255),
    "king_gold": (240, 195, 45, 255),
    "ermine_white": (245, 245, 242, 255),
    "ermine_spot": (30, 25, 30, 255),
    "steel_light": (210, 218, 228, 255),
    "steel_shadow": (140, 150, 165, 255),
    "wood_brown": (110, 65, 35, 255),
}

def create_sprite(w: int, h: int) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    return img, ImageDraw.Draw(img)

# ==============================================================================
# 1. TRIBOULET (THE JESTER) - MODULAR ILLUSTRATED PARTS
# ==============================================================================
def generate_triboulet_parts():
    char_dir = RIGS_DIR / "triboulet"
    char_dir.mkdir(parents=True, exist_ok=True)
    
    # Head & Expressions
    for expr in ["neutral", "smirk", "shock", "laugh"]:
        img, d = create_sprite(256, 256)
        # Face shape
        d.ellipse([64, 60, 192, 196], fill=PALETTE["skin_light"], outline=PALETTE["outline"], width=4)
        # Cheeks
        d.ellipse([76, 128, 106, 148], fill=PALETTE["skin_rosy"])
        d.ellipse([150, 128, 180, 148], fill=PALETTE["skin_rosy"])
        # Eyes
        if expr == "shock":
            d.ellipse([88, 92, 120, 128], fill=(255, 255, 255), outline=PALETTE["outline"], width=3)
            d.ellipse([136, 92, 168, 128], fill=(255, 255, 255), outline=PALETTE["outline"], width=3)
            d.ellipse([100, 106, 108, 114], fill=PALETTE["outline"])
            d.ellipse([148, 106, 156, 114], fill=PALETTE["outline"])
            # High arched brows
            d.arc([86, 75, 122, 95], 200, 340, fill=PALETTE["outline"], width=4)
            d.arc([134, 75, 170, 95], 200, 340, fill=PALETTE["outline"], width=4)
            # Open gasp mouth
            d.ellipse([116, 148, 140, 178], fill=(60, 15, 20), outline=PALETTE["outline"], width=3)
        elif expr == "smirk":
            # Sly eyes
            d.arc([90, 96, 122, 120], 190, 350, fill=PALETTE["outline"], width=4)
            d.arc([134, 96, 166, 120], 190, 350, fill=PALETTE["outline"], width=4)
            d.ellipse([104, 102, 114, 112], fill=PALETTE["outline"])
            d.ellipse([142, 102, 152, 112], fill=PALETTE["outline"])
            # Raised brow
            d.arc([88, 80, 120, 96], 200, 340, fill=PALETTE["outline"], width=4)
            d.arc([136, 86, 168, 102], 200, 340, fill=PALETTE["outline"], width=4)
            # Smirk curve
            d.arc([110, 140, 154, 166], 340, 140, fill=PALETTE["outline"], width=4)
        elif expr == "laugh":
            # Closed happy squinting eyes
            d.arc([90, 100, 122, 116], 190, 350, fill=PALETTE["outline"], width=4)
            d.arc([134, 100, 166, 116], 190, 350, fill=PALETTE["outline"], width=4)
            # Wide open laughing mouth with white teeth
            d.pieslice([106, 136, 150, 176], 0, 180, fill=(70, 15, 20), outline=PALETTE["outline"], width=3)
            d.rectangle([112, 137, 144, 145], fill=(255, 255, 255))
        else: # neutral
            d.ellipse([92, 100, 116, 120], fill=(255, 255, 255), outline=PALETTE["outline"], width=3)
            d.ellipse([140, 100, 164, 120], fill=(255, 255, 255), outline=PALETTE["outline"], width=3)
            d.ellipse([100, 106, 110, 116], fill=PALETTE["outline"])
            d.ellipse([148, 106, 158, 116], fill=PALETTE["outline"])
            d.line([(90, 90), (118, 88)], fill=PALETTE["outline"], width=3)
            d.line([(138, 88), (166, 90)], fill=PALETTE["outline"], width=3)
            d.arc([114, 144, 142, 160], 20, 160, fill=PALETTE["outline"], width=3)
            
        # Nose
        d.line([(128, 114), (124, 132), (134, 132)], fill=PALETTE["outline"], width=3)
        img.save(char_dir / f"head_{expr}.png")

    # Jester Cap (Three-horned chaperon with golden bells)
    img_cap, d_cap = create_sprite(300, 240)
    # Left horn (yellow)
    d_cap.polygon([(110, 110), (30, 60), (45, 120), (110, 130)], fill=PALETTE["jester_yellow"], outline=PALETTE["outline"], width=4)
    d_cap.ellipse([18, 48, 42, 72], fill=PALETTE["bell_gold"], outline=PALETTE["outline"], width=3)
    # Right horn (purple)
    d_cap.polygon([(190, 110), (270, 60), (255, 120), (190, 130)], fill=PALETTE["jester_purple"], outline=PALETTE["outline"], width=4)
    d_cap.ellipse([258, 48, 282, 72], fill=PALETTE["bell_gold"], outline=PALETTE["outline"], width=3)
    # Center horn (split yellow/purple)
    d_cap.polygon([(120, 110), (150, 20), (180, 110)], fill=PALETTE["jester_yellow"], outline=PALETTE["outline"], width=4)
    d_cap.polygon([(150, 20), (180, 110), (150, 110)], fill=PALETTE["jester_purple"], outline=PALETTE["outline"], width=4)
    d_cap.ellipse([136, 10, 164, 38], fill=PALETTE["bell_gold"], outline=PALETTE["outline"], width=3)
    # Forehead headband band with scalloped dagging
    d_cap.rounded_rectangle([95, 105, 205, 140], radius=10, fill=PALETTE["jester_yellow"], outline=PALETTE["outline"], width=4)
    img_cap.save(char_dir / "jester_cap.png")

    # Torso (Parti-colored yellow/purple with dagged hem and bells)
    img_t, d_t = create_sprite(256, 320)
    # Left half yellow, right half purple
    d_t.polygon([(64, 30), (128, 30), (128, 260), (50, 260)], fill=PALETTE["jester_yellow"], outline=PALETTE["outline"], width=4)
    d_t.polygon([(128, 30), (192, 30), (206, 260), (128, 260)], fill=PALETTE["jester_purple"], outline=PALETTE["outline"], width=4)
    # Scalloped dagged collar
    d_t.polygon([(60, 30), (80, 75), (105, 30), (128, 80), (150, 30), (175, 75), (195, 30)], fill=PALETTE["jester_purple"], outline=PALETTE["outline"], width=3)
    # Belt & buckle
    d_t.rectangle([54, 210, 202, 235], fill=(50, 35, 25), outline=PALETTE["outline"], width=3)
    d_t.rectangle([114, 205, 142, 240], fill=PALETTE["bell_gold"], outline=PALETTE["outline"], width=3)
    img_t.save(char_dir / "torso.png")

    # Upper Arm (Left Yellow, Right Purple)
    for side, col in [("left", PALETTE["jester_yellow"]), ("right", PALETTE["jester_purple"])]:
        img_ua, d_ua = create_sprite(128, 180)
        d_ua.rounded_rectangle([44, 20, 84, 160], radius=18, fill=col, outline=PALETTE["outline"], width=4)
        img_ua.save(char_dir / f"upper_arm_{side}.png")

    # Lower Arm / Forearm
    for side, col in [("left", PALETTE["jester_purple"]), ("right", PALETTE["jester_yellow"])]:
        img_la, d_la = create_sprite(128, 180)
        d_la.rounded_rectangle([46, 20, 82, 150], radius=16, fill=col, outline=PALETTE["outline"], width=4)
        img_la.save(char_dir / f"lower_arm_{side}.png")

    # Hands (Open, Fist, Point)
    for pose in ["open", "fist", "point"]:
        img_h, d_h = create_sprite(128, 128)
        if pose == "point":
            # Pointing index finger
            d_h.rounded_rectangle([48, 15, 68, 85], radius=8, fill=PALETTE["skin_light"], outline=PALETTE["outline"], width=3)
            d_h.ellipse([42, 45, 86, 95], fill=PALETTE["skin_light"], outline=PALETTE["outline"], width=3)
        elif pose == "fist":
            d_h.ellipse([44, 40, 84, 85], fill=PALETTE["skin_light"], outline=PALETTE["outline"], width=4)
            d_h.line([(48, 60), (80, 60)], fill=PALETTE["outline"], width=3)
        else: # open
            d_h.ellipse([42, 35, 86, 90], fill=PALETTE["skin_light"], outline=PALETTE["outline"], width=3)
            d_h.ellipse([30, 50, 52, 75], fill=PALETTE["skin_light"], outline=PALETTE["outline"], width=3) # thumb
        img_h.save(char_dir / f"hand_{pose}.png")

    # Upper Leg & Lower Leg (Striped tights)
    for side, col in [("left", PALETTE["jester_purple"]), ("right", PALETTE["jester_yellow"])]:
        img_ul, d_ul = create_sprite(128, 200)
        d_ul.rounded_rectangle([42, 20, 86, 180], radius=18, fill=col, outline=PALETTE["outline"], width=4)
        img_ul.save(char_dir / f"upper_leg_{side}.png")

        img_ll, d_ll = create_sprite(128, 200)
        d_ll.rounded_rectangle([46, 20, 82, 180], radius=16, fill=col, outline=PALETTE["outline"], width=4)
        img_ll.save(char_dir / f"lower_leg_{side}.png")

    # Curved Pointed Jester Shoes with golden bells
    for side in ["left", "right"]:
        img_f, d_f = create_sprite(160, 100)
        # Pointed curled shoe
        d_f.polygon([(30, 20), (85, 20), (95, 65), (145, 50), (135, 75), (30, 75)], fill=PALETTE["jester_purple"], outline=PALETTE["outline"], width=3)
        # Bell on tip
        d_f.ellipse([138, 42, 156, 60], fill=PALETTE["bell_gold"], outline=PALETTE["outline"], width=2)
        if side == "left":
            img_f = img_f.transpose(Image.FLIP_LEFT_RIGHT)
        img_f.save(char_dir / f"foot_{side}.png")

    print("[+] Generated complete modular 2D rig parts for TRIBOULET.")

# ==============================================================================
# 2. KING FRANCIS I - MODULAR ILLUSTRATED PARTS
# ==============================================================================
def generate_king_parts():
    char_dir = RIGS_DIR / "king_francis"
    char_dir.mkdir(parents=True, exist_ok=True)

    # Head with royal beard & expressions
    for expr in ["regal", "furious", "amused_laugh"]:
        img, d = create_sprite(300, 300)
        # Head base
        d.ellipse([75, 65, 225, 215], fill=PALETTE["skin_light"], outline=PALETTE["outline"], width=4)
        # Renaissance dark pointed beard and mustache
        d.polygon([(90, 160), (150, 255), (210, 160), (180, 200), (120, 200)], fill=(45, 30, 25), outline=PALETTE["outline"], width=3)
        # Mustache
        d.polygon([(110, 168), (150, 155), (190, 168), (150, 178)], fill=(40, 25, 20), outline=PALETTE["outline"], width=3)
        # Aquiline nose
        d.line([(150, 115), (142, 148), (155, 148)], fill=PALETTE["outline"], width=4)

        if expr == "furious":
            # Deep angled angry brows
            d.line([(95, 105), (135, 120)], fill=PALETTE["outline"], width=5)
            d.line([(165, 120), (205, 105)], fill=PALETTE["outline"], width=5)
            # Glaring eyes
            d.ellipse([105, 118, 130, 138], fill=(255, 255, 255), outline=PALETTE["outline"], width=3)
            d.ellipse([170, 118, 195, 138], fill=(255, 255, 255), outline=PALETTE["outline"], width=3)
            d.ellipse([115, 124, 123, 132], fill=PALETTE["outline"])
            d.ellipse([177, 124, 185, 132], fill=PALETTE["outline"])
            # Scowling mouth
            d.arc([130, 178, 170, 198], 190, 350, fill=PALETTE["outline"], width=4)
        elif expr == "amused_laugh":
            # Squinting laughing eyes
            d.arc([105, 118, 135, 134], 190, 350, fill=PALETTE["outline"], width=4)
            d.arc([165, 118, 195, 134], 190, 350, fill=PALETTE["outline"], width=4)
            d.arc([100, 102, 138, 118], 200, 340, fill=PALETTE["outline"], width=4)
            d.arc([162, 102, 200, 118], 200, 340, fill=PALETTE["outline"], width=4)
            # Booming laughing mouth
            d.pieslice([130, 168, 170, 202], 0, 180, fill=(70, 15, 20), outline=PALETTE["outline"], width=3)
            d.rectangle([135, 169, 165, 177], fill=(255, 255, 255))
        else: # regal
            d.ellipse([108, 118, 132, 136], fill=(255, 255, 255), outline=PALETTE["outline"], width=3)
            d.ellipse([168, 118, 192, 136], fill=(255, 255, 255), outline=PALETTE["outline"], width=3)
            d.ellipse([116, 122, 124, 130], fill=PALETTE["outline"])
            d.ellipse([176, 122, 184, 130], fill=PALETTE["outline"])
            d.line([(102, 110), (136, 110)], fill=PALETTE["outline"], width=4)
            d.line([(164, 110), (198, 110)], fill=PALETTE["outline"], width=4)
            d.line([(135, 178), (165, 178)], fill=PALETTE["outline"], width=3)

        img.save(char_dir / f"head_{expr}.png")

    # Royal Golden Crown with Fleur-de-lis
    img_crown, d_c = create_sprite(300, 180)
    # Crown base band
    d_c.rounded_rectangle([70, 95, 230, 135], radius=6, fill=PALETTE["king_gold"], outline=PALETTE["outline"], width=4)
    # Jewels on band
    for j_x in [95, 125, 150, 175, 205]:
        d_c.ellipse([j_x - 7, 108, j_x + 7, 122], fill=PALETTE["king_crimson"], outline=PALETTE["outline"], width=2)
    # Three Fleur-de-lis spikes
    d_c.polygon([(85, 95), (105, 35), (125, 95)], fill=PALETTE["king_gold"], outline=PALETTE["outline"], width=3)
    d_c.polygon([(130, 95), (150, 15), (170, 95)], fill=PALETTE["king_gold"], outline=PALETTE["outline"], width=3)
    d_c.polygon([(175, 95), (195, 35), (215, 95)], fill=PALETTE["king_gold"], outline=PALETTE["outline"], width=3)
    img_crown.save(char_dir / "royal_crown.png")

    # Majestic Torso (Crimson doublet with heavy Ermine fur collar & Order of St. Michael chain)
    img_t, d_t = create_sprite(340, 380)
    # Crimson doublet
    d_t.polygon([(70, 50), (270, 50), (290, 320), (50, 320)], fill=PALETTE["king_crimson"], outline=PALETTE["outline"], width=5)
    # Gold embroidery center
    d_t.rectangle([155, 50, 185, 320], fill=PALETTE["king_gold"], outline=PALETTE["outline"], width=3)
    for b_y in [90, 140, 190, 240, 290]:
        d_t.ellipse([162, b_y, 178, b_y + 16], fill=(50, 20, 10), outline=PALETTE["outline"], width=2)
    # Wide Ermine fur collar/shawl
    d_t.polygon([(40, 45), (170, 160), (300, 45), (260, 20), (170, 40), (80, 20)], fill=PALETTE["ermine_white"], outline=PALETTE["outline"], width=4)
    # Ermine black tails/spots
    for ex, ey in [(80, 55), (120, 90), (170, 125), (220, 90), (260, 55)]:
        d_t.polygon([(ex, ey), (ex - 4, ey + 18), (ex + 4, ey + 18)], fill=PALETTE["ermine_spot"])
    # Golden Order of St. Michael medallion
    d_t.arc([110, 110, 230, 220], 0, 180, fill=PALETTE["king_gold"], width=6)
    d_t.ellipse([160, 215, 180, 235], fill=PALETTE["king_gold"], outline=PALETTE["outline"], width=2)
    img_t.save(char_dir / "torso.png")

    # Arms (Heavy puffed crimson sleeves with gold slashes)
    for side in ["left", "right"]:
        img_ua, d_ua = create_sprite(160, 200)
        d_ua.ellipse([35, 20, 125, 170], fill=PALETTE["king_crimson"], outline=PALETTE["outline"], width=4)
        # Gold slashes
        d_ua.line([(55, 60), (105, 75)], fill=PALETTE["king_gold"], width=6)
        d_ua.line([(50, 100), (110, 115)], fill=PALETTE["king_gold"], width=6)
        img_ua.save(char_dir / f"upper_arm_{side}.png")

        img_la, d_la = create_sprite(140, 180)
        d_la.rounded_rectangle([45, 20, 95, 150], radius=16, fill=PALETTE["king_crimson_dark"], outline=PALETTE["outline"], width=4)
        # White lace cuff
        d_la.rounded_rectangle([40, 130, 100, 160], radius=8, fill=(255, 255, 255), outline=PALETTE["outline"], width=3)
        img_la.save(char_dir / f"lower_arm_{side}.png")

        # Royal hands with rings
        img_h, d_h = create_sprite(128, 128)
        d_h.ellipse([42, 35, 86, 92], fill=PALETTE["skin_light"], outline=PALETTE["outline"], width=4)
        d_h.ellipse([70, 48, 80, 58], fill=PALETTE["king_gold"]) # Gold ring
        img_h.save(char_dir / f"hand_{side}.png")

    # Royal Legs (Gold-braided velvet breeches and riding boots)
    for side in ["left", "right"]:
        img_ul, d_ul = create_sprite(140, 200)
        d_ul.rounded_rectangle([40, 20, 100, 180], radius=18, fill=PALETTE["king_crimson"], outline=PALETTE["outline"], width=4)
        img_ul.save(char_dir / f"upper_leg_{side}.png")

        img_ll, d_ll = create_sprite(140, 220)
        # Black leather riding boot
        d_ll.rounded_rectangle([45, 20, 95, 190], radius=12, fill=(30, 25, 28), outline=PALETTE["outline"], width=4)
        # Gold boot buckle
        d_ll.rectangle([55, 120, 85, 140], fill=PALETTE["king_gold"], outline=PALETTE["outline"], width=2)
        img_ll.save(char_dir / f"lower_leg_{side}.png")

        img_f, d_f = create_sprite(160, 90)
        d_f.polygon([(35, 20), (105, 20), (145, 65), (35, 65)], fill=(25, 20, 22), outline=PALETTE["outline"], width=4)
        if side == "left":
            img_f = img_f.transpose(Image.FLIP_LEFT_RIGHT)
        img_f.save(char_dir / f"foot_{side}.png")

    print("[+] Generated complete modular 2D rig parts for KING FRANCIS I.")

# ==============================================================================
# 3. CHARACTER DESIGN SHEET ARTIFACT (Proof of Visual Consistency)
# ==============================================================================
def generate_character_design_sheet():
    sheet_w, sheet_h = 1600, 1000
    sheet = Image.new("RGBA", (sheet_w, sheet_h), (20, 22, 28, 255))
    draw = ImageDraw.Draw(sheet)

    # Title header
    draw.rounded_rectangle([40, 30, sheet_w - 40, 100], radius=10, fill=(30, 34, 44, 255), outline=PALETTE["king_gold"], width=2)
    # Character 1 Panel (Triboulet)
    draw.rounded_rectangle([60, 130, 780, 950], radius=14, fill=(28, 30, 38, 255), outline=(255, 255, 255, 40), width=2)
    draw.text((420, 160), "TRIBOULET — THE ROYAL JESTER", fill=PALETTE["jester_yellow"], anchor="mm")
    
    # Character 2 Panel (King Francis I)
    draw.rounded_rectangle([820, 130, 1540, 950], radius=14, fill=(28, 30, 38, 255), outline=(255, 255, 255, 40), width=2)
    draw.text((1180, 160), "KING FRANCIS I — MONARCH OF FRANCE", fill=PALETTE["king_crimson"], anchor="mm")

    # Composite Triboulet Assembly preview
    t_dir = RIGS_DIR / "triboulet"
    t_torso = Image.open(t_dir / "torso.png")
    t_head = Image.open(t_dir / "head_smirk.png")
    t_cap = Image.open(t_dir / "jester_cap.png")
    
    sheet.alpha_composite(t_torso, (300, 430))
    sheet.alpha_composite(t_head, (300, 280))
    sheet.alpha_composite(t_cap, (278, 200))

    # Triboulet Expressions row
    for idx, exp in enumerate(["neutral", "smirk", "shock", "laugh"]):
        h_exp = Image.open(t_dir / f"head_{exp}.png").resize((120, 120))
        sheet.alpha_composite(h_exp, (90 + idx * 170, 780))
        draw.text((150 + idx * 170, 920), exp.upper(), fill=(200, 200, 200), anchor="mm")

    # Composite King Assembly preview
    k_dir = RIGS_DIR / "king_francis"
    k_torso = Image.open(k_dir / "torso.png")
    k_head = Image.open(k_dir / "head_regal.png")
    k_crown = Image.open(k_dir / "royal_crown.png")

    sheet.alpha_composite(k_torso, (1010, 420))
    sheet.alpha_composite(k_head, (1030, 260))
    sheet.alpha_composite(k_crown, (1030, 180))

    # King Expressions row
    for idx, exp in enumerate(["regal", "furious", "amused_laugh"]):
        k_exp = Image.open(k_dir / f"head_{exp}.png").resize((140, 140))
        sheet.alpha_composite(k_exp, (880 + idx * 220, 770))
        draw.text((950 + idx * 220, 920), exp.replace("_", " ").upper(), fill=(200, 200, 200), anchor="mm")

    sheet_path = RIGS_DIR / "character_design_sheet.png"
    sheet.save(sheet_path)
    print(f"[+] Character design sheet saved to: {sheet_path}")
    return sheet_path

if __name__ == "__main__":
    generate_triboulet_parts()
    generate_king_parts()
    generate_character_design_sheet()
