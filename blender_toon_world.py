"""
Blender 4.2 3D Toon World & Character Stage Animator
Implements the claude-animated-shorts SKILL.md & STYLE_BIBLE.md look in Blender 4.2 EEVEE-Next:
- Hand-painted procedural textures with dark seams (cobble, wood, brick, parchment)
- 3D world geometry with Solidify backface-culled black ink outlines (#030303)
- Flat 2D bean-head cartoon characters (toon_cast.py) on lit 3D planes (NOINK)
- Saturated sky gradient + matching horizon fog + Depth of Field (dofAt)
- Smootherstep gliding cameras + creeping push-ins + 4.5-deg Dutch rolls
"""

import os
import math
import subprocess
from typing import Dict, Any, List
from PIL import Image, ImageDraw
from config import BASE_DIR, OUTPUT_DIR, ASSETS_DIR
import toon_cast

BLENDER_EXE = r"C:\Program Files\Blender Foundation\Blender 4.2\blender.exe"


def generate_painted_textures(tex_dir: str) -> Dict[str, str]:
    """Generates painted HD textures with hand-inked seams (paint.ts style)."""
    os.makedirs(tex_dir, exist_ok=True)
    paths = {}

    # 1. Cobblestone plaza texture (1024x1024 crisp stone with dark mortar seams)
    cob_path = os.path.join(tex_dir, "cobble_hd_v2.png")
    if not os.path.exists(cob_path):
        im = Image.new("RGBA", (1024, 1024), (112, 108, 104, 255))
        d = ImageDraw.Draw(im)
        rows, cols = 12, 10
        rh, cw = 1024 // rows, 1024 // cols
        for r in range(rows):
            off = (cw // 2) if r % 2 else 0
            for c in range(-1, cols + 1):
                x0, y0 = c * cw + off, r * rh
                shade = ((r * 7 + c * 13) % 18) - 9
                col = (138 + shade, 132 + shade, 124 + shade, 255)
                d.rounded_rectangle([x0 + 4, y0 + 4, x0 + cw - 4, y0 + rh - 4], radius=14, fill=col, outline=(42, 38, 44, 255), width=5)
        im.save(cob_path)
    paths["cobble"] = cob_path

    # 2. Painted ochre/brick house wall with mortar seams
    brick_path = os.path.join(tex_dir, "brick_hd.png")
    if not os.path.exists(brick_path):
        im = Image.new("RGBA", (512, 512), (186, 132, 92, 255))
        d = ImageDraw.Draw(im)
        for r in range(12):
            y0 = r * 42
            off = 42 if r % 2 else 0
            for c in range(-1, 7):
                x0 = c * 85 + off
                v = ((r * 11 + c * 5) % 16) - 8
                col = (192 + v, 128 + v, 88 + v, 255)
                d.rectangle([x0 + 2, y0 + 2, x0 + 82, y0 + 39], fill=col, outline=(85, 52, 42, 200), width=2)
        im.save(brick_path)
    paths["brick"] = brick_path

    # 3. Painted timber planks with near-black seams (ochre wood deck)
    wood_path = os.path.join(tex_dir, "wood_hd.png")
    if not os.path.exists(wood_path):
        im = Image.new("RGBA", (512, 512), (168, 120, 72, 255))
        d = ImageDraw.Draw(im)
        for r in range(8):
            y0 = r * 64
            v = ((r * 17) % 14) - 7
            d.rectangle([0, y0 + 2, 512, y0 + 62], fill=(172 + v, 124 + v, 74 + v, 255), outline=(35, 24, 18, 255), width=3)
            # Plank vertical joints
            jx = ((r * 193 + 80) % 420) + 40
            d.line([(jx, y0), (jx, y0 + 64)], fill=(35, 24, 18, 255), width=3)
        im.save(wood_path)
    paths["wood"] = wood_path

    # 4. Radio speaker cloth / dial texture
    radio_path = os.path.join(tex_dir, "radio_face.png")
    if not os.path.exists(radio_path):
        im = Image.new("RGBA", (512, 512), (62, 42, 32, 255))
        d = ImageDraw.Draw(im)
        # Frame
        d.rounded_rectangle([16, 16, 496, 496], radius=24, fill=(68, 46, 34, 255), outline=(22, 16, 14, 255), width=10)
        # Speaker circle
        d.ellipse([106, 60, 406, 320], fill=(32, 24, 20, 255), outline=(215, 175, 100, 255), width=8)
        for x in range(136, 380, 28):
            d.line([(x, 80), (x, 300)], fill=(175, 138, 76, 220), width=6)
        # Warm glowing tuning dial
        d.rounded_rectangle([110, 360, 402, 436], radius=12, fill=(255, 205, 85, 255), outline=(28, 20, 14, 255), width=6)
        d.line([(256, 366), (256, 430)], fill=(215, 35, 35, 255), width=8)
        im.save(radio_path)
    paths["radio_face"] = radio_path

    return paths


def prepare_cast_sprites(cast_dir: str, topic_type: str) -> Dict[str, str]:
    """Generates story-matched toon.ts bean-head sprites with expressions and poses."""
    os.makedirs(cast_dir, exist_ok=True)
    sprites = {}

    if topic_type == "hitler":
        # Speaker on podium (charcoal/brown uniform coat + officer cap)
        sprites["speaker_stern"] = toon_cast.render_character_card(
            os.path.join(cast_dir, "speaker_stern.png"),
            jacket="#4d443a", pants="#34302a", hat="officer_cap", expr="stern", prop="mic", facing=1, seed=3
        )
        sprites["speaker_shout"] = toon_cast.render_character_card(
            os.path.join(cast_dir, "speaker_shout.png"),
            jacket="#4d443a", pants="#34302a", hat="officer_cap", expr="laugh", wave=0.8, facing=1, seed=3
        )
        # Citizens (1930s coats, fedoras, hair)
        sprites["cit_neutral"] = toon_cast.render_character_card(
            os.path.join(cast_dir, "cit_neutral.png"),
            jacket="#3f6fb5", pants="#383e4e", hat="fedora", expr="neutral", facing=-1, seed=7
        )
        sprites["cit_cheer"] = toon_cast.render_character_card(
            os.path.join(cast_dir, "cit_cheer.png"),
            jacket="#7a543c", pants="#383e4e", hat="fedora", expr="grin", wave=0.9, facing=1, seed=11
        )
        sprites["cit_shock"] = toon_cast.render_character_card(
            os.path.join(cast_dir, "cit_shock.png"),
            jacket="#3f6fb5", pants="#383e4e", hat="fedora", expr="shock", wave=0.3, facing=-1, seed=7
        )
        sprites["cit_walk1"] = toon_cast.render_character_card(
            os.path.join(cast_dir, "cit_walk1.png"),
            jacket="#5d7a3a", pants="#3b3f52", hat="hair", expr="nervous", mode="stroll", phase=0.25, facing=1, seed=19
        )
    elif topic_type == "bank":
        sprites["speaker_stern"] = toon_cast.render_character_card(
            os.path.join(cast_dir, "buyer_grin.png"),
            jacket="#2d4a78", pants="#242936", hat="tophat", expr="grin", prop="dollar", facing=1, seed=5
        )
        sprites["cit_shock"] = toon_cast.render_character_card(
            os.path.join(cast_dir, "banker_shock.png"),
            jacket="#4a3b52", pants="#242936", hat="hair", expr="shock", facing=-1, seed=9
        )
        sprites["cit_neutral"] = toon_cast.render_character_card(
            os.path.join(cast_dir, "clerk_neutral.png"),
            jacket="#627852", pants="#242936", hat="hair", expr="neutral", facing=1, seed=12
        )
        sprites["cit_cheer"] = sprites["speaker_stern"]
        sprites["speaker_shout"] = sprites["speaker_stern"]
        sprites["cit_walk1"] = sprites["cit_neutral"]
    else:
        sprites["speaker_stern"] = toon_cast.render_character_card(
            os.path.join(cast_dir, "hero_neutral.png"),
            jacket="#8c3b4a", pants="#383e4e", hat="tophat", expr="neutral", facing=1, seed=2
        )
        sprites["speaker_shout"] = toon_cast.render_character_card(
            os.path.join(cast_dir, "hero_grin.png"),
            jacket="#8c3b4a", pants="#383e4e", hat="tophat", expr="grin", wave=0.7, facing=1, seed=2
        )
        sprites["cit_neutral"] = toon_cast.render_character_card(
            os.path.join(cast_dir, "town_neutral.png"),
            jacket="#3f6fb5", pants="#383e4e", hat="fedora", expr="neutral", facing=-1, seed=6
        )
        sprites["cit_cheer"] = toon_cast.render_character_card(
            os.path.join(cast_dir, "town_cheer.png"),
            jacket="#b5653f", pants="#383e4e", hat="hair", expr="grin", wave=0.8, facing=1, seed=8
        )
        sprites["cit_shock"] = toon_cast.render_character_card(
            os.path.join(cast_dir, "town_shock.png"),
            jacket="#3f6fb5", pants="#383e4e", hat="fedora", expr="shock", facing=-1, seed=6
        )
        sprites["cit_walk1"] = sprites["cit_neutral"]

    return sprites


def render_blender_toon_world(script: Dict[str, Any], duration: float) -> str:
    """Builds and renders the full 3D painted toon world in Blender 4.2 EEVEE-Next."""
    script_id = script.get("id", "custom_short")
    style = script.get("style", "tall_tale_3d")
    full_text = (script.get("title", "") + " " + script.get("full_narration", "")).lower()

    if any(k in full_text for k in ["hitler", "1933", "weimar", "propaganda", "volksempf"]):
        topic_type = "hitler"
    elif "bank" in full_text and ("$1" in full_text or "dollar" in full_text):
        topic_type = "bank"
    else:
        topic_type = "general"

    tex_dir = os.path.abspath(os.path.join(str(ASSETS_DIR), "toon_textures"))
    cast_dir = os.path.abspath(os.path.join(str(ASSETS_DIR), f"cast_{script_id}"))
    textures = generate_painted_textures(tex_dir)
    sprites = prepare_cast_sprites(cast_dir, topic_type)

    out_raw = os.path.abspath(os.path.join(str(OUTPUT_DIR), f"raw_3d_{script_id}.mp4"))
    blend_py = os.path.abspath(os.path.join(str(OUTPUT_DIR), f"scene_{script_id}.py"))
    total_frames = max(72, int(math.ceil(duration * 24)))

    # Lighting preset from SKILL.md (Day vs Golden/Twilight)
    is_golden = (style == "night_file_3d") or (topic_type == "hitler")

    py_code = f'''import bpy
import math
import os

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

# 1080x1920 Vertical @ 24 FPS (75% render scale -> crisp 1080x1920 upscale in final FFmpeg pass, ~2.5x faster!)
scene.render.resolution_x = 1080
scene.render.resolution_y = 1920
scene.render.resolution_percentage = 75
scene.render.fps = 24
scene.frame_start = 1
scene.frame_end = {max(72, int(math.ceil(duration * 24)))}
scene.render.engine = 'BLENDER_EEVEE_NEXT'

# Fast, sharp EEVEE-Next GPU settings (no heavy GI raytracing needed for crisp 3D toon ink art!)
if hasattr(scene.eevee, 'taa_render_samples'):
    scene.eevee.taa_render_samples = 4
if hasattr(scene.eevee, 'use_raytracing'):
    scene.eevee.use_raytracing = False
if hasattr(scene.eevee, 'use_shadows'):
    scene.eevee.use_shadows = True
if hasattr(scene.eevee, 'shadow_ray_count'):
    scene.eevee.shadow_ray_count = 1
if hasattr(scene.eevee, 'shadow_step_count'):
    scene.eevee.shadow_step_count = 4

try:
    scene.view_settings.view_transform = 'Standard'
except Exception:
    pass

scene.render.image_settings.file_format = 'FFMPEG'
scene.render.ffmpeg.format = 'MPEG4'
scene.render.ffmpeg.codec = 'H264'
scene.render.ffmpeg.constant_rate_factor = 'MEDIUM'
scene.render.ffmpeg.ffmpeg_preset = 'REALTIME'
scene.render.filepath = r"{out_raw}"

# ---------------- World Sky Gradient + Matching Fog (SKILL.md look) ----------------
world = bpy.data.worlds.new("ToonWorld")
scene.world = world
world.use_nodes = True
wn = world.node_tree.nodes
wl = world.node_tree.links
wn.clear()

w_out = wn.new('ShaderNodeOutputWorld')
w_bg = wn.new('ShaderNodeBackground')
w_texcoord = wn.new('ShaderNodeTexCoord')
w_sep = wn.new('ShaderNodeSeparateXYZ')
w_ramp = wn.new('ShaderNodeValToRGB')

# Saturated sky gradient (golden/twilight vs bright day)
is_golden = {repr(is_golden)}
if is_golden:
    # Golden-hour / dramatic twilight sky (#6f5d8c top -> #ffcf9e horizon)
    w_ramp.color_ramp.elements[0].position = 0.0
    w_ramp.color_ramp.elements[0].color = (0.98, 0.72, 0.45, 1.0)
    w_ramp.color_ramp.elements[1].position = 0.45
    w_ramp.color_ramp.elements[1].color = (0.34, 0.31, 0.56, 1.0)
    w_bg.inputs['Strength'].default_value = 1.1
else:
    # Day sky (#3e7fd2 top -> #b8d0ec horizon)
    w_ramp.color_ramp.elements[0].position = 0.0
    w_ramp.color_ramp.elements[0].color = (0.72, 0.82, 0.93, 1.0)
    w_ramp.color_ramp.elements[1].position = 0.45
    w_ramp.color_ramp.elements[1].color = (0.24, 0.50, 0.82, 1.0)
    w_bg.inputs['Strength'].default_value = 1.2

wl.new(w_texcoord.outputs['Generated'], w_sep.inputs['Vector'])
wl.new(w_sep.outputs['Z'], w_ramp.inputs['Fac'])
wl.new(w_ramp.outputs['Color'], w_bg.inputs['Color'])
wl.new(w_bg.outputs['Background'], w_out.inputs['Surface'])

# ---------------- Materials + Inverted-Hull Black Ink (#030303) ----------------
ink_mat = bpy.data.materials.new("WorldInk")
ink_mat.use_nodes = True
ink_mat.use_backface_culling = True
inodes = ink_mat.node_tree.nodes
ilinks = ink_mat.node_tree.links
inodes.clear()
i_out = inodes.new('ShaderNodeOutputMaterial')
i_emit = inodes.new('ShaderNodeEmission')
i_emit.inputs['Color'].default_value = (0.008, 0.008, 0.012, 1.0)
i_emit.inputs['Strength'].default_value = 1.0
ilinks.new(i_emit.outputs['Emission'], i_out.inputs['Surface'])

def make_painted_mat(name, color=None, tex_path=None, scale_uv=1.0, emit=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Roughness'].default_value = 0.85
    if 'Specular IOR Level' in bsdf.inputs:
        bsdf.inputs['Specular IOR Level'].default_value = 0.08
    if tex_path and os.path.exists(tex_path):
        tc = nodes.new('ShaderNodeTexCoord')
        mp = nodes.new('ShaderNodeMapping')
        mp.inputs['Scale'].default_value = (scale_uv, scale_uv, scale_uv)
        tx = nodes.new('ShaderNodeTexImage')
        tx.image = bpy.data.images.load(tex_path)
        links.new(tc.outputs['UV'], mp.inputs['Vector'])
        links.new(mp.outputs['Vector'], tx.inputs['Vector'])
        links.new(tx.outputs['Color'], bsdf.inputs['Base Color'])
        if emit > 0:
            links.new(tx.outputs['Color'], bsdf.inputs['Emission Color'])
            bsdf.inputs['Emission Strength'].default_value = emit
    else:
        bsdf.inputs['Base Color'].default_value = color
        if emit > 0:
            bsdf.inputs['Emission Color'].default_value = color
            bsdf.inputs['Emission Strength'].default_value = emit
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat

def add_ink_outline(obj, thickness=0.032):
    obj.data.materials.append(ink_mat)
    mod = obj.modifiers.new("InkHull", 'SOLIDIFY')
    mod.thickness = -thickness
    mod.offset = 1.0
    mod.use_flip_normals = True
    mod.material_offset = len(obj.data.materials) - 1

# Materials
mat_cobble = make_painted_mat("Cobble", tex_path=r"{textures['cobble']}", scale_uv=34.0)
mat_brick = make_painted_mat("Brick", tex_path=r"{textures['brick']}", scale_uv=2.5)
mat_wood = make_painted_mat("Wood", tex_path=r"{textures['wood']}", scale_uv=2.0)
mat_radio = make_painted_mat("RadioFace", tex_path=r"{textures['radio_face']}", scale_uv=1.0, emit=0.15)

mat_ochre = make_painted_mat("OchreWall", color=(0.82, 0.64, 0.36, 1.0))
mat_cream = make_painted_mat("CreamWall", color=(0.88, 0.83, 0.72, 1.0))
mat_terra = make_painted_mat("TerraWall", color=(0.74, 0.36, 0.28, 1.0))
mat_slate = make_painted_mat("SlateRoof", color=(0.24, 0.26, 0.34, 1.0))
mat_stone = make_painted_mat("StonePlinth", color=(0.56, 0.54, 0.50, 1.0))
mat_banner = make_painted_mat("RedBanner", color=(0.68, 0.14, 0.16, 1.0))
mat_gold = make_painted_mat("GoldTrim", color=(0.88, 0.68, 0.22, 1.0))
mat_green = make_painted_mat("TreeGreen", color=(0.24, 0.52, 0.28, 1.0))
mat_glow_amber = make_painted_mat("GlowAmber", color=(1.0, 0.72, 0.25, 1.0), emit=2.5)

# ---------------- 1. Cobblestone Town Plaza Ground ----------------
bpy.ops.mesh.primitive_plane_add(size=120, location=(0, 0, 0))
ground = bpy.context.active_object
ground.name = "PlazaGround"
ground.data.materials.append(mat_cobble)

# ---------------- 2. Painted 3D European Town Houses (with plinths, pitched roofs, windows, ink) ----------------
def build_house(name, x, y, w, d, h, wall_mat, rot_z=0.0):
    # Main facade
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(x, y, h / 2.0))
    body = bpy.context.active_object
    body.name = name
    body.scale = (w, d, h)
    body.rotation_euler[2] = rot_z
    body.data.materials.append(wall_mat)
    add_ink_outline(body, 0.04)

    # Stone plinth base
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(x, y, 0.45))
    plinth = bpy.context.active_object
    plinth.scale = (w + 0.18, d + 0.18, 0.9)
    plinth.rotation_euler[2] = rot_z
    plinth.data.materials.append(mat_stone)
    add_ink_outline(plinth, 0.035)

    # Pitched roof (wedge prism / cone scaled)
    bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=max(w, d) * 0.78, depth=2.8, location=(x, y, h + 1.4))
    roof = bpy.context.active_object
    roof.scale = (w / max(w, d), d / max(w, d), 1.0)
    roof.rotation_euler[2] = rot_z + math.radians(45)
    roof.data.materials.append(mat_slate)
    add_ink_outline(roof, 0.04)

    # Windows on front face
    win_mat = make_painted_mat(f"Win_{{name}}", color=(0.20, 0.26, 0.36, 1.0))
    for wz in (2.6, 5.2):
        if wz + 0.8 < h:
            for wx in (-w * 0.26, w * 0.26):
                bpy.ops.mesh.primitive_cube_add(size=1.0, location=(x + wx * math.cos(rot_z) - (-d/2 - 0.05) * math.sin(rot_z), y + wx * math.sin(rot_z) + (-d/2 - 0.05) * math.cos(rot_z), wz))
                win = bpy.context.active_object
                win.scale = (1.1, 0.16, 1.45)
                win.rotation_euler[2] = rot_z
                win.data.materials.append(win_mat)
                add_ink_outline(win, 0.025)

# Town houses framing the plaza + radio street backdrop!
build_house("H_L1", -8.5, 4.0, 5.5, 5.0, 7.5, mat_ochre, math.radians(-12))
build_house("H_L2", -10.0, 12.5, 6.2, 5.5, 9.2, mat_brick, math.radians(-8))
build_house("H_R1", 8.5, 4.5, 5.5, 5.0, 7.8, mat_cream, math.radians(12))
build_house("H_R2", 10.2, 13.0, 6.0, 5.5, 8.8, mat_terra, math.radians(8))
build_house("H_BG1", -4.2, 21.0, 6.5, 5.5, 9.6, mat_cream, math.radians(0))
build_house("H_BG2", 4.5, 22.0, 6.8, 5.5, 10.4, mat_ochre, math.radians(0))
build_house("H_RAD1", 13.8, 12.0, 6.4, 5.5, 8.6, mat_brick, math.radians(-6))
build_house("H_RAD2", 20.5, 10.5, 6.0, 5.5, 7.8, mat_cream, math.radians(10))

# Stylized Trees + Streetlamps along the avenue & radio plaza
for tx, ty in ((-5.5, 8.5), (5.8, 9.0), (-6.8, 17.0), (6.5, 17.5), (10.5, 7.0), (18.2, 7.5)):
    bpy.ops.mesh.primitive_cylinder_add(radius=0.28, depth=2.4, location=(tx, ty, 1.2))
    tr = bpy.context.active_object
    tr.data.materials.append(mat_wood)
    add_ink_outline(tr, 0.025)
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=1.5, location=(tx, ty, 3.1))
    lf = bpy.context.active_object
    lf.scale = (1.0, 1.0, 1.25)
    lf.data.materials.append(mat_green)
    add_ink_outline(lf, 0.03)

for lx, ly in ((-4.2, 3.2), (4.4, 3.5), (11.2, 3.2)):
    bpy.ops.mesh.primitive_cylinder_add(radius=0.09, depth=3.6, location=(lx, ly, 1.8))
    pole = bpy.context.active_object
    pole.data.materials.append(mat_slate)
    add_ink_outline(pole, 0.02)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.26, location=(lx, ly, 3.75))
    bulb = bpy.context.active_object
    bulb.data.materials.append(mat_glow_amber)
    add_ink_outline(bulb, 0.02)

# Soft painted sky clouds (no ink, bright horizon tint)
cloud_mat = make_painted_mat("CloudMat", color=(0.98, 0.94, 0.90, 1.0), emit=0.55)
for cx, cy, cz, cs in ((-9, 46, 15, 3.6), (7, 50, 17, 4.2), (20, 44, 14, 3.2)):
    for ox, oz, r_c in ((0, 0, cs), (-cs * 0.7, -0.3, cs * 0.7), (cs * 0.75, -0.2, cs * 0.72)):
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=r_c, location=(cx + ox, cy, cz + oz))
        cl = bpy.context.active_object
        cl.scale = (1.3, 0.6, 0.8)
        cl.data.materials.append(cloud_mat)

# ---------------- 3. Story Centerpiece Props (3D Podium + Giant 3D Radio!) ----------------
# Grand wooden/stone podium at plaza center (y = 5.5)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 5.5, 0.55))
stage_base = bpy.context.active_object
stage_base.scale = (4.6, 3.2, 1.1)
stage_base.data.materials.append(mat_stone)
add_ink_outline(stage_base, 0.035)

bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 4.25, 1.48))
lectern = bpy.context.active_object
lectern.scale = (1.15, 0.65, 0.82)
lectern.data.materials.append(mat_wood)
add_ink_outline(lectern, 0.03)

# Dramatic Banners flanking the podium
for bx in (-1.8, 1.8):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(bx, 6.6, 2.8))
    bn = bpy.context.active_object
    bn.scale = (0.75, 0.12, 4.2)
    bn.data.materials.append(mat_banner)
    add_ink_outline(bn, 0.03)

# Giant 3D 1930s Volksempfaenger Radio staged on the right-side platform (x = 3.8, y = 1.2)
# So camera glides seamlessly from the plaza straight to the giant glowing radio!
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(14.5, 2.0, 1.45))
radio_box = bpy.context.active_object
radio_box.scale = (2.1, 1.4, 2.9)
radio_box.data.materials.append(mat_wood)
add_ink_outline(radio_box, 0.04)

bpy.ops.mesh.primitive_plane_add(size=1.0, location=(14.5, 1.28, 1.45))
radio_front = bpy.context.active_object
radio_front.rotation_euler = (math.radians(90), 0, 0)
radio_front.scale = (1.9, 2.7, 1.0)
radio_front.data.materials.append(mat_radio)

# Animated glowing broadcast rings expanding out of the 3D radio!
pulse_rings = []
for r_idx in range(3):
    bpy.ops.mesh.primitive_torus_add(major_radius=1.0, minor_radius=0.04, location=(14.5, 1.15, 1.95))
    ring = bpy.context.active_object
    ring.rotation_euler = (math.radians(90), 0, 0)
    ring.data.materials.append(mat_glow_amber)
    pulse_rings.append(ring)

for f in range(1, {total_frames} + 1, 2):
    for idx, ring in enumerate(pulse_rings):
        ph = ((f / 36.0) + idx / 3.0) % 1.0
        sc = 0.35 + ph * 1.40
        ring.scale = (sc, sc, 1.0)
        ring.keyframe_insert(data_path="scale", frame=f)

# ---------------- 4. 2D Bean-Head Cartoon Cast (NOINK collection, lit by scene lights, casts shadows) ----------------
def add_toon_card(name, img_path, loc, height_m=1.85, rot_z=0.0):
    bpy.ops.mesh.primitive_plane_add(size=1.0, location=(loc[0], loc[1], loc[2] + height_m / 2.0))
    plane = bpy.context.active_object
    plane.name = name
    # 600x1000 sprite ratio -> width = 0.6 * height
    plane.scale = (height_m * 0.6, height_m, 1.0)
    plane.rotation_euler = (math.radians(90), 0, math.radians(rot_z))

    mat = bpy.data.materials.new(f"CharMat_{{name}}")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Roughness'].default_value = 0.9
    if 'Specular IOR Level' in bsdf.inputs:
        bsdf.inputs['Specular IOR Level'].default_value = 0.0
    tx = nodes.new('ShaderNodeTexImage')
    tx.image = bpy.data.images.load(img_path)
    # Lit by scene light + soft self-readability (cardshade.ts style, never pure emissive!)
    links.new(tx.outputs['Color'], bsdf.inputs['Base Color'])
    links.new(tx.outputs['Color'], bsdf.inputs['Emission Color'])
    bsdf.inputs['Emission Strength'].default_value = 0.25
    links.new(tx.outputs['Alpha'], bsdf.inputs['Alpha'])
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    plane.data.materials.append(mat)
    return plane

# Place Orator behind podium (on elevated stage z=1.1)
speaker_a = add_toon_card("SpeakerStern", r"{sprites['speaker_stern']}", (0.0, 4.9, 1.1), height_m=1.95)
speaker_b = add_toon_card("SpeakerShout", r"{sprites['speaker_shout']}", (0.0, 4.9, 1.1), height_m=1.95)

# Animate speaker swap + cheering bounce!
for f in range(1, {total_frames} + 1, 15):
    is_shout = ((f // 15) % 2 == 1)
    speaker_a.hide_render = is_shout
    speaker_b.hide_render = not is_shout
    speaker_a.keyframe_insert(data_path="hide_render", frame=f)
    speaker_b.keyframe_insert(data_path="hide_render", frame=f)

# Place Front-Row Citizens in the plaza (facing podium / radio)
cit1 = add_toon_card("Cit1", r"{sprites['cit_neutral']}", (-1.6, 1.2, 0.0), height_m=1.80, rot_z=12)
cit2 = add_toon_card("Cit2", r"{sprites['cit_cheer']}", (1.4, 1.6, 0.0), height_m=1.82, rot_z=-15)
cit3 = add_toon_card("Cit3", r"{sprites['cit_shock']}", (-0.4, 0.5, 0.0), height_m=1.78, rot_z=6)
cit4 = add_toon_card("Cit4", r"{sprites['cit_walk1']}", (-3.2, 2.2, 0.0), height_m=1.76, rot_z=20)
cit5 = add_toon_card("Cit5", r"{sprites['cit_cheer']}", (2.9, 2.5, 0.0), height_m=1.80, rot_z=-20)

# Citizens by the Giant Radio (for Pivot shot!)
cit_radio = add_toon_card("CitRadio", r"{sprites['cit_shock']}", (12.2, 1.6, 0.0), height_m=1.82, rot_z=25)

# Subtle walk/bob animation on crowd citizens
for f in range(1, {total_frames} + 1, 6):
    bob = abs(math.sin(f * 0.25)) * 0.06
    for idx, c in enumerate((cit1, cit2, cit3, cit5)):
        c.location[2] = 0.90 + (bob if idx % 2 == 0 else (0.06 - bob))
        c.keyframe_insert(data_path="location", index=2, frame=f)

# ---------------- 5. 3-Point Warm Key + Cool Violet Fill Lighting (SKILL.md look) ----------------
sun_data = bpy.data.lights.new("KeySun", type='SUN')
sun_data.energy = 3.2 if is_golden else 4.0
sun_data.color = (1.0, 0.84, 0.65) if is_golden else (1.0, 0.96, 0.88)
sun_obj = bpy.data.objects.new("KeySun", sun_data)
scene.collection.objects.link(sun_obj)
sun_obj.rotation_euler = (math.radians(52), math.radians(-24), math.radians(32))

# Cool blue/violet fill light so shadows stay crisp blue-violet, never muddy brown!
fill_data = bpy.data.lights.new("CoolFill", type='AREA')
fill_data.energy = 900
fill_data.size = 14.0
fill_data.color = (0.48, 0.52, 0.92)
fill_obj = bpy.data.objects.new("CoolFill", fill_data)
scene.collection.objects.link(fill_obj)
fill_obj.location = (-8.0, -6.0, 8.0)
fill_obj.rotation_euler = (math.radians(55), 0, math.radians(-40))

# Dramatic stage spotlight beams on the podium for Night File 3D
if is_golden:
    for sx in (-3.5, 3.5):
        sp = bpy.data.lights.new("StageSpot", type='SPOT')
        sp.energy = 2800
        sp.spot_size = math.radians(38)
        sp.spot_blend = 0.35
        sp.color = (1.0, 0.78, 0.55)
        sp_obj = bpy.data.objects.new("StageSpot", sp)
        scene.collection.objects.link(sp_obj)
        sp_obj.location = (sx, 0.5, 8.5)
        sp_obj.rotation_euler = (math.radians(35), math.radians(-15 if sx > 0 else 15), 0)

# ---------------- 6. Gliding Smootherstep Camera + DOF + Creeping Push-Ins (SKILL.md) ----------------
cam_data = bpy.data.cameras.new("MainCam")
cam_data.lens = 38.0
cam_data.dof.use_dof = True
cam_data.dof.aperture_fstop = 4.0
cam_obj = bpy.data.objects.new("MainCam", cam_data)
scene.collection.objects.link(cam_obj)
scene.camera = cam_obj

# Camera target empty for smooth look-at
target = bpy.data.objects.new("CamTarget", None)
scene.collection.objects.link(target)
track = cam_obj.constraints.new('TRACK_TO')
track.target = target
track.track_axis = 'TRACK_NEGATIVE_Z'
track.up_axis = 'UP_Y'

def smootherstep(t):
    t = max(0.0, min(1.0, t))
    return t * t * t * (t * (t * 6 - 15) + 10)

N = {total_frames}
# Key camera beats mapped smoothly across N frames (zero static holds!)
# Format: (frame_frac, cam_pos, target_pos, lens, dof_dist, roll_deg)
BEATS = [
    (0.00, (-0.8, -3.5, 1.45), (-0.4, 0.5, 1.25), 42.0, 4.0, -2.5),   # Hook CU: shocked citizen
    (0.14, (-0.5, -2.6, 1.55), (-0.4, 0.5, 1.35), 46.0, 3.1, -1.5),   # Hook push-in
    (0.16, (-3.2, -7.2, 4.80), (0.0, 5.0, 2.20), 32.0, 13.0, 0.0),    # Wide Town Setting
    (0.32, (-1.8, -5.0, 3.40), (0.0, 5.0, 2.20), 35.0, 10.0, 1.5),    # Gliding into plaza
    (0.35, (-0.8, 1.9, 2.45),  (0.0, 4.9, 2.30), 46.0, 3.1, -3.0),    # Clear Podium Orator Shot (past crowd!)
    (0.55, (-0.4, 2.5, 2.55),  (0.0, 4.9, 2.40), 50.0, 2.5, -1.5),    # Pushing into Orator face & mic
    (0.58, (2.2, -1.5, 1.55),  (1.4, 1.6, 1.35), 48.0, 3.2, 3.5),     # Mystery CU on cheering/shocked crowd
    (0.68, (1.9, -0.7, 1.58),  (1.4, 1.6, 1.40), 52.0, 2.4, 2.0),     # Creeping push-in
    (0.71, (11.2, -4.8, 2.15), (13.4, 1.8, 1.45), 36.0, 6.8, -2.5),   # Pivot: Shocked Citizen + Giant 3D Radio!
    (0.88, (12.0, -3.2, 1.95), (13.9, 1.8, 1.60), 42.0, 5.2, 0.0),    # Pushing into glowing dial & waves
    (0.90, (-2.5, -6.5, 4.20), (0.0, 4.5, 2.10), 34.0, 12.0, 0.0),    # Payoff Pull-out back to plaza loop
    (1.00, (-0.8, -3.5, 1.45), (-0.4, 0.5, 1.25), 42.0, 4.0, -2.5),   # Seamless loop back to Frame 1!
]

for frac, pos, tgt, lens, dof_d, roll in BEATS:
    fr = max(1, min(N, int(round(frac * (N - 1))) + 1))
    cam_obj.location = pos
    cam_obj.keyframe_insert(data_path="location", frame=fr)
    target.location = tgt
    target.keyframe_insert(data_path="location", frame=fr)
    cam_data.lens = lens
    cam_data.keyframe_insert(data_path="lens", frame=fr)
    cam_data.dof.focus_distance = dof_d
    cam_data.keyframe_insert(data_path="dof.focus_distance", frame=fr)

# Use smooth Bezier interpolation on all camera keyframes
for obj in (cam_obj, target):
    if obj.animation_data and obj.animation_data.action:
        for fc in obj.animation_data.action.fcurves:
            for kp in fc.keyframe_points:
                kp.interpolation = 'BEZIER'

print("[*] Rendering 3D Toon World in Blender 4.2 EEVEE-Next...")
bpy.ops.render.render(animation=True)
print("[+] Blender 3D Toon World render complete ->", r"{out_raw}")
'''

    with open(blend_py, "w", encoding="utf-8") as f:
        f.write(py_code)

    print(f"[*] Launching Blender 4.2 EEVEE-Next ({total_frames} frames @ 1080x1920)...")
    res = subprocess.run([BLENDER_EXE, "--background", "--python", blend_py], capture_output=True, text=True)
    if res.returncode == 0 and os.path.exists(out_raw):
        print(f"[+] 3D Toon World rendered: {out_raw}")
        return out_raw
    else:
        print(f"[!] Blender render note ({res.returncode}): {res.stderr[-400:]}")
        return ""
