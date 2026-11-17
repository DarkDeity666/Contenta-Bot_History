"""
=============================================================================
MASTER ANIMATED SHORT GENERATOR: TRIBOULET & KING FRANCIS I
=============================================================================
Full cinematic multi-act 2.5D animation in Blender 4.2 EEVEE-Next:
- 115.75 seconds (3,472 frames @ 30 FPS, 1080x1920 vertical)
- Articulated 2D cartoon puppets with expressive facial expressions
- Dynamic camera cuts, zooms, parallax staging, and lighting
- Automated Foley SFX synchronization, background music, and kinetic subtitles
=============================================================================
"""

import os
import math
import subprocess
import imageio_ffmpeg

TOTAL_FRAMES = 3472  # 115.73 seconds @ 30 FPS
OUTPUT_RAW_VIDEO = os.path.abspath("output/triboulet_raw.mp4")
FINAL_EXPORT_VIDEO = os.path.abspath("output/history_short_triboulet_master.mp4")

BLENDER_SCRIPT = """
import bpy
import math
import os

TOTAL_FRAMES = 3472

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

# 1080x1920 Vertical Video @ 30 FPS
scene.render.resolution_x = 1080
scene.render.resolution_y = 1920
scene.render.fps = 30
scene.frame_start = 1
scene.frame_end = TOTAL_FRAMES
scene.render.engine = 'BLENDER_EEVEE_NEXT'

# Video export settings
scene.render.image_settings.file_format = 'FFMPEG'
scene.render.ffmpeg.format = 'MPEG4'
scene.render.ffmpeg.codec = 'H264'
scene.render.ffmpeg.constant_rate_factor = 'LOW'
scene.render.ffmpeg.ffmpeg_preset = 'REALTIME'
scene.render.filepath = r"{output_video}"

# World ambient lighting (bright & vibrant cartoon ambiance)
world = bpy.data.worlds.new("W")
scene.world = world
world.use_nodes = True
bg = world.node_tree.nodes.get("Background")
bg.inputs['Color'].default_value = (0.09, 0.08, 0.12, 1.0)
bg.inputs['Strength'].default_value = 1.2

# 3-Point Lighting
key_light = bpy.data.lights.new("Key", type='SPOT')
key_light.energy = 3200
key_light.color = (1.0, 0.95, 0.88)
key_light.spot_size = math.radians(80)
key_obj = bpy.data.objects.new("Light_Key", key_light)
bpy.context.collection.objects.link(key_obj)
key_obj.location = (-2.0, -5.5, 4.0)
key_obj.rotation_euler = (math.radians(45), math.radians(-15), 0)

fill_light = bpy.data.lights.new("Fill", type='POINT')
fill_light.energy = 900
fill_light.color = (0.65, 0.75, 1.0)
fill_obj = bpy.data.objects.new("Light_Fill", fill_light)
bpy.context.collection.objects.link(fill_obj)
fill_obj.location = (3.5, -4.0, 2.0)

# Rim Sunlight from stained glass
rim_light = bpy.data.lights.new("Rim", type='SUN')
rim_light.energy = 2.0
rim_light.color = (1.0, 0.95, 0.9)
rim_obj = bpy.data.objects.new("Light_Rim", rim_light)
bpy.context.collection.objects.link(rim_obj)
rim_obj.rotation_euler = (math.radians(-35), 0, math.radians(180))

# Virtual Camera
cam_data = bpy.data.cameras.new("Cam")
cam_data.lens = 42
cam_obj = bpy.data.objects.new("Camera", cam_data)
bpy.context.collection.objects.link(cam_obj)
scene.camera = cam_obj

def create_sprite_mesh(name, img_path, width, height, pivot=(0.5, 0.5)):
    mat = bpy.data.materials.new(name=f"Mat_{name}")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    out_node = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    tex_node = nodes.new('ShaderNodeTexImage')
    if os.path.exists(img_path):
        tex_node.image = bpy.data.images.load(os.path.abspath(img_path))
    links.new(tex_node.outputs['Color'], bsdf.inputs['Base Color'])
    links.new(tex_node.outputs['Alpha'], bsdf.inputs['Alpha'])
    links.new(bsdf.outputs['BSDF'], out_node.inputs['Surface'])
    
    if hasattr(mat, 'blend_method'):
        mat.blend_method = 'BLEND'
    if hasattr(mat, 'shadow_method'):
        mat.shadow_method = 'CLIP'
        
    mesh = bpy.data.meshes.new(name)
    px, py = pivot
    x_min = -px * width
    x_max = (1.0 - px) * width
    z_min = -py * height
    z_max = (1.0 - py) * height
    
    verts = [(x_min, 0, z_min), (x_max, 0, z_min), (x_max, 0, z_max), (x_min, 0, z_max)]
    faces = [(0, 1, 2, 3)]
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    
    uv_layer = mesh.uv_layers.new(name="UVMap")
    uvs = [(0, 0), (1, 0), (1, 1), (0, 1)]
    for i, loop in enumerate(mesh.loops):
        uv_layer.data[loop.index].uv = uvs[i % 4]
        
    obj = bpy.data.objects.new(name, mesh)
    obj.data.materials.append(mat)
    bpy.context.collection.objects.link(obj)
    return obj

# Environment Assembly
env_dir = os.path.join("assets", "environments", "renaissance_court")
deep_bg = create_sprite_mesh("Env_DeepBG", os.path.join(env_dir, "deep_background.png"), 14.0, 9.0, (0.5, 0.5))
deep_bg.location = (0, 11.0, 1.2)

wall = create_sprite_mesh("Env_Wall", os.path.join(env_dir, "midground_wall.png"), 11.0, 7.5, (0.5, 0.5))
wall.location = (0, 5.0, 0.6)

throne = create_sprite_mesh("Env_Throne", os.path.join(env_dir, "throne_dais.png"), 3.6, 3.6, (0.5, 0.5))
throne.location = (1.1, 0.6, -0.4)

floor = create_sprite_mesh("Env_Floor", os.path.join(env_dir, "marble_floor.png"), 14.0, 12.0, (0.5, 0.5))
floor.rotation_euler = (math.radians(-90), 0, 0)
floor.location = (0, 1.5, -2.1)

fg = create_sprite_mesh("Env_FG", os.path.join(env_dir, "foreground_framing.png"), 6.2, 10.5, (0.5, 0.5))
fg.location = (0, -4.5, 0.0)

# Build Triboulet Character
char_tri_dir = os.path.join("assets", "character_rigs_v2", "triboulet")
s_t = 1.45
tri_root = bpy.data.objects.new("Triboulet_Root", None)
tri_root.location = (-2.8, 0, -1.25)
bpy.context.collection.objects.link(tri_root)

torso_t_h = 0.75 * s_t
tri_torso = create_sprite_mesh("Tri_Torso", os.path.join(char_tri_dir, "torso.png"), 0.6*s_t, torso_t_h, (0.5, 0.0))
tri_torso.parent = tri_root
tri_torso.location = (0, 0, 0.65*s_t)

head_t_h = 0.6 * s_t
tri_head = create_sprite_mesh("Tri_Head", os.path.join(char_tri_dir, "head_smirk.png"), 0.6*s_t, head_t_h, (0.5, 0.1))
tri_head.parent = tri_torso
tri_head.location = (0, -0.01, torso_t_h - 0.12*s_t)

tri_cap = create_sprite_mesh("Tri_Cap", os.path.join(char_tri_dir, "jester_cap.png"), 0.9*s_t, 0.65*s_t, (0.5, 0.35))
tri_cap.parent = tri_head
tri_cap.location = (0, -0.02, head_t_h * 0.52)

tri_arm_up_l = create_sprite_mesh("Tri_ArmUp_L", os.path.join(char_tri_dir, "upper_arm_left.png"), 0.22*s_t, 0.42*s_t, (0.5, 0.9))
tri_arm_up_l.parent = tri_torso
tri_arm_up_l.location = (0.22*s_t, 0.01, torso_t_h * 0.8)

tri_arm_low_l = create_sprite_mesh("Tri_ArmLow_L", os.path.join(char_tri_dir, "lower_arm_left.png"), 0.18*s_t, 0.38*s_t, (0.5, 0.9))
tri_arm_low_l.parent = tri_arm_up_l
tri_arm_low_l.location = (0.0, 0.01, -0.34*s_t)

tri_hand_l = create_sprite_mesh("Tri_Hand_L", os.path.join(char_tri_dir, "hand_open.png"), 0.25*s_t, 0.25*s_t, (0.5, 0.85))
tri_hand_l.parent = tri_arm_low_l
tri_hand_l.location = (0.0, 0.01, -0.32*s_t)

tri_arm_up_r = create_sprite_mesh("Tri_ArmUp_R", os.path.join(char_tri_dir, "upper_arm_right.png"), 0.22*s_t, 0.42*s_t, (0.5, 0.9))
tri_arm_up_r.parent = tri_torso
tri_arm_up_r.location = (-0.22*s_t, -0.01, torso_t_h * 0.8)

tri_arm_low_r = create_sprite_mesh("Tri_ArmLow_R", os.path.join(char_tri_dir, "lower_arm_right.png"), 0.18*s_t, 0.38*s_t, (0.5, 0.9))
tri_arm_low_r.parent = tri_arm_up_r
tri_arm_low_r.location = (0.0, -0.01, -0.34*s_t)

tri_hand_r = create_sprite_mesh("Tri_Hand_R", os.path.join(char_tri_dir, "hand_point.png"), 0.28*s_t, 0.24*s_t, (0.5, 0.85))
tri_hand_r.parent = tri_arm_low_r
tri_hand_r.location = (0.0, -0.01, -0.32*s_t)

# Legs
tri_leg_up_l = create_sprite_mesh("Tri_LegUp_L", os.path.join(char_tri_dir, "upper_leg_left.png"), 0.22*s_t, 0.45*s_t, (0.5, 0.95))
tri_leg_up_l.parent = tri_root
tri_leg_up_l.location = (0.12*s_t, 0.01, 0.65*s_t)

tri_leg_low_l = create_sprite_mesh("Tri_LegLow_L", os.path.join(char_tri_dir, "lower_leg_left.png"), 0.19*s_t, 0.45*s_t, (0.5, 0.95))
tri_leg_low_l.parent = tri_leg_up_l
tri_leg_low_l.location = (0.0, 0.01, -0.38*s_t)

tri_foot_l = create_sprite_mesh("Tri_Foot_L", os.path.join(char_tri_dir, "foot_left.png"), 0.36*s_t, 0.24*s_t, (0.3, 0.85))
tri_foot_l.parent = tri_leg_low_l
tri_foot_l.location = (0.03*s_t, 0.01, -0.4*s_t)

tri_leg_up_r = create_sprite_mesh("Tri_LegUp_R", os.path.join(char_tri_dir, "upper_leg_right.png"), 0.22*s_t, 0.45*s_t, (0.5, 0.95))
tri_leg_up_r.parent = tri_root
tri_leg_up_r.location = (-0.12*s_t, -0.01, 0.65*s_t)

tri_leg_low_r = create_sprite_mesh("Tri_LegLow_R", os.path.join(char_tri_dir, "lower_leg_right.png"), 0.19*s_t, 0.45*s_t, (0.5, 0.95))
tri_leg_low_r.parent = tri_leg_up_r
tri_leg_low_r.location = (0.0, -0.01, -0.38*s_t)

tri_foot_r = create_sprite_mesh("Tri_Foot_R", os.path.join(char_tri_dir, "foot_right.png"), 0.36*s_t, 0.24*s_t, (0.7, 0.85))
tri_foot_r.parent = tri_leg_low_r
tri_foot_r.location = (-0.03*s_t, -0.01, -0.4*s_t)

# Build King Francis I Character
char_king_dir = os.path.join("assets", "character_rigs_v2", "king_francis")
s_k = 1.6
king_root = bpy.data.objects.new("King_Root", None)
king_root.location = (1.1, 0.2, -0.9)
bpy.context.collection.objects.link(king_root)

torso_k_h = 0.85 * s_k
king_torso = create_sprite_mesh("King_Torso", os.path.join(char_king_dir, "torso.png"), 0.85*s_k, torso_k_h, (0.5, 0.0))
king_torso.parent = king_root
king_torso.location = (0, 0, 0.25*s_k)

head_k_h = 0.65 * s_k
king_head = create_sprite_mesh("King_Head", os.path.join(char_king_dir, "head_furious.png"), 0.6*s_k, head_k_h, (0.5, 0.15))
king_head.parent = king_torso
king_head.location = (0, -0.01, torso_k_h - 0.15*s_k)

king_crown = create_sprite_mesh("King_Crown", os.path.join(char_king_dir, "royal_crown.png"), 0.68*s_k, 0.4*s_k, (0.5, 0.35))
king_crown.parent = king_head
king_crown.location = (0, -0.02, head_k_h * 0.6)

king_arm_up_l = create_sprite_mesh("King_ArmUp_L", os.path.join(char_king_dir, "upper_arm_left.png"), 0.36*s_k, 0.46*s_k, (0.5, 0.9))
king_arm_up_l.parent = king_torso
king_arm_up_l.location = (-0.34*s_k, -0.01, torso_k_h * 0.75)

king_arm_low_l = create_sprite_mesh("King_ArmLow_L", os.path.join(char_king_dir, "lower_arm_left.png"), 0.25*s_k, 0.42*s_k, (0.5, 0.9))
king_arm_low_l.parent = king_arm_up_l
king_arm_low_l.location = (0.0, -0.01, -0.38*s_k)

king_hand_l = create_sprite_mesh("King_Hand_L", os.path.join(char_king_dir, "hand_left.png"), 0.28*s_k, 0.24*s_k, (0.5, 0.85))
king_hand_l.parent = king_arm_low_l
king_hand_l.location = (0.0, -0.01, -0.35*s_k)

king_arm_up_r = create_sprite_mesh("King_ArmUp_R", os.path.join(char_king_dir, "upper_arm_right.png"), 0.36*s_k, 0.46*s_k, (0.5, 0.9))
king_arm_up_r.parent = king_torso
king_arm_up_r.location = (0.34*s_k, 0.01, torso_k_h * 0.75)

king_arm_low_r = create_sprite_mesh("King_ArmLow_R", os.path.join(char_king_dir, "lower_arm_right.png"), 0.25*s_k, 0.42*s_k, (0.5, 0.9))
king_arm_low_r.parent = king_arm_up_r
king_arm_low_r.location = (0.0, 0.01, -0.38*s_k)

king_hand_r = create_sprite_mesh("King_Hand_R", os.path.join(char_king_dir, "hand_right.png"), 0.26*s_k, 0.26*s_k, (0.5, 0.85))
king_hand_r.parent = king_arm_low_r
king_hand_r.location = (0.0, 0.01, -0.35*s_k)

# =============================================================================
# CINEMATIC MULTI-ACT KEYFRAME ANIMATION & CAMERA DIRECTING
# =============================================================================

# SHOT 1 (Frames 1 - 540): Establishing Wide Pan & Jester Strut
cam_obj.location = (-1.4, -8.2, 0.2)
cam_obj.rotation_euler = (math.radians(90), 0, math.radians(-10))
cam_obj.keyframe_insert("location", frame=1)
cam_obj.keyframe_insert("rotation_euler", frame=1)

cam_obj.location = (-0.4, -7.2, 0.0)
cam_obj.rotation_euler = (math.radians(90), 0, math.radians(-3))
cam_obj.keyframe_insert("location", frame=540)
cam_obj.keyframe_insert("rotation_euler", frame=540)

# Triboulet walks in from X = -2.8 to X = -0.8
tri_root.location = (-2.8, 0, -1.25)
tri_root.keyframe_insert("location", frame=1)
tri_root.location = (-0.8, 0, -1.25)
tri_root.keyframe_insert("location", frame=300)

# Walk cycle frames 1 - 300
for f in range(1, 301, 20):
    # Left step
    tri_leg_up_l.rotation_euler = (math.radians(22), 0, 0)
    tri_leg_up_r.rotation_euler = (math.radians(-22), 0, 0)
    tri_arm_up_l.rotation_euler = (math.radians(-25), 0, 0)
    tri_arm_up_r.rotation_euler = (math.radians(25), 0, 0)
    tri_torso.location = (0, 0, 0.65*s_t + 0.04)
    tri_leg_up_l.keyframe_insert("rotation_euler", frame=f)
    tri_leg_up_r.keyframe_insert("rotation_euler", frame=f)
    tri_arm_up_l.keyframe_insert("rotation_euler", frame=f)
    tri_arm_up_r.keyframe_insert("rotation_euler", frame=f)
    tri_torso.keyframe_insert("location", frame=f)
    
    # Right step
    tri_leg_up_l.rotation_euler = (math.radians(-22), 0, 0)
    tri_leg_up_r.rotation_euler = (math.radians(22), 0, 0)
    tri_arm_up_l.rotation_euler = (math.radians(25), 0, 0)
    tri_arm_up_r.rotation_euler = (math.radians(-25), 0, 0)
    tri_torso.location = (0, 0, 0.65*s_t - 0.02)
    tri_leg_up_l.keyframe_insert("rotation_euler", frame=min(f+10, 300))
    tri_leg_up_r.keyframe_insert("rotation_euler", frame=min(f+10, 300))
    tri_arm_up_l.keyframe_insert("rotation_euler", frame=min(f+10, 300))
    tri_arm_up_r.keyframe_insert("rotation_euler", frame=min(f+10, 300))
    tri_torso.keyframe_insert("location", frame=min(f+10, 300))

# Rest stance at frame 320
tri_leg_up_l.rotation_euler = (0, 0, 0)
tri_leg_up_r.rotation_euler = (0, 0, 0)
tri_leg_up_l.keyframe_insert("rotation_euler", frame=320)
tri_leg_up_r.keyframe_insert("rotation_euler", frame=320)

# SHOT 2 (Frames 541 - 1020): Medium Two-Shot on King's Warning
cam_obj.location = (0.2, -6.8, 0.1)
cam_obj.rotation_euler = (math.radians(90), 0, math.radians(2))
cam_obj.keyframe_insert("location", frame=541)
cam_obj.keyframe_insert("rotation_euler", frame=541)

# King raises pointing arm with stern royal authority
king_arm_up_l.rotation_euler = (0, 0, math.radians(-45))
king_arm_low_l.rotation_euler = (0, 0, math.radians(-35))
king_arm_up_l.keyframe_insert("rotation_euler", frame=600)
king_arm_low_l.keyframe_insert("rotation_euler", frame=600)

# King wags pointing finger
for f in [680, 740, 800, 860]:
    king_arm_up_l.rotation_euler = (0, 0, math.radians(-50))
    king_arm_up_l.keyframe_insert("rotation_euler", frame=f)
    king_arm_up_l.rotation_euler = (0, 0, math.radians(-38))
    king_arm_up_l.keyframe_insert("rotation_euler", frame=f+30)

# Triboulet stands center, smirking, hand on hip
tri_arm_up_r.rotation_euler = (0, 0, math.radians(35))
tri_arm_low_r.rotation_euler = (0, 0, math.radians(65))
tri_head.rotation_euler = (0, 0, math.radians(-10))
tri_arm_up_r.keyframe_insert("rotation_euler", frame=650)
tri_arm_low_r.keyframe_insert("rotation_euler", frame=650)
tri_head.keyframe_insert("rotation_euler", frame=650)

# SHOT 3 (Frames 1021 - 1500): The Audacious Slap Action!
# Camera cuts to dramatic close profile
cam_obj.location = (0.3, -5.8, 0.0)
cam_obj.rotation_euler = (math.radians(90), 0, math.radians(4))
cam_obj.keyframe_insert("location", frame=1021)
cam_obj.keyframe_insert("rotation_euler", frame=1021)

# Triboulet creeps up close to King (from X = -0.8 to X = 0.2)
tri_root.location = (-0.8, 0, -1.25)
tri_root.keyframe_insert("location", frame=1030)
tri_root.location = (0.2, 0, -1.25)
tri_root.keyframe_insert("location", frame=1120)

# Triboulet winds up his right arm high
tri_arm_up_r.rotation_euler = (0, 0, math.radians(95))
tri_arm_low_r.rotation_euler = (0, 0, math.radians(60))
tri_arm_up_r.keyframe_insert("rotation_euler", frame=1130)
tri_arm_low_r.keyframe_insert("rotation_euler", frame=1130)

# SLAP IMPACT at Frame 1145! Arm whips down onto royal backside!
tri_arm_up_r.rotation_euler = (0, 0, math.radians(-45))
tri_arm_low_r.rotation_euler = (0, 0, math.radians(-30))
tri_arm_up_r.keyframe_insert("rotation_euler", frame=1145)
tri_arm_low_r.keyframe_insert("rotation_euler", frame=1145)

# Camera Shake on impact (Frames 1145 - 1160)
for shake_f in [1145, 1148, 1152, 1156, 1160]:
    shake_x = 0.3 + (0.08 if shake_f % 2 == 0 else -0.08)
    cam_obj.location = (shake_x, -5.8, 0.05 if shake_f % 2 == 0 else -0.05)
    cam_obj.keyframe_insert("location", frame=shake_f)
cam_obj.location = (0.3, -5.8, 0.0)
cam_obj.keyframe_insert("location", frame=1165)

# King Francis whips around, trembling with fury
king_torso.rotation_euler = (0, 0, math.radians(15))
king_head.rotation_euler = (0, 0, math.radians(18))
king_torso.keyframe_insert("rotation_euler", frame=1165)
king_head.keyframe_insert("rotation_euler", frame=1165)

# Triboulet recoils in shock/mock horror
tri_root.location = (-0.6, 0, -1.25)
tri_arm_up_l.rotation_euler = (0, 0, math.radians(-70))
tri_arm_up_r.rotation_euler = (0, 0, math.radians(70))
tri_root.keyframe_insert("location", frame=1180)
tri_arm_up_l.keyframe_insert("rotation_euler", frame=1180)
tri_arm_up_r.keyframe_insert("rotation_euler", frame=1180)

# SHOT 4 (Frames 1501 - 2160): The Ultimatum & The Theatrical Apology
cam_obj.location = (0.0, -6.5, 0.2)
cam_obj.rotation_euler = (math.radians(88), 0, 0)
cam_obj.keyframe_insert("location", frame=1501)
cam_obj.keyframe_insert("rotation_euler", frame=1501)

# Triboulet executes a deep, exaggerated court bow (Frames 1650 - 1850)
tri_torso.rotation_euler = (0, 0, math.radians(-38))
tri_head.rotation_euler = (0, 0, math.radians(25))
tri_arm_up_l.rotation_euler = (0, math.radians(-35), math.radians(-20))
tri_arm_up_r.rotation_euler = (0, math.radians(35), math.radians(20))
tri_torso.keyframe_insert("rotation_euler", frame=1720)
tri_head.keyframe_insert("rotation_euler", frame=1720)
tri_arm_up_l.keyframe_insert("rotation_euler", frame=1720)
tri_arm_up_r.keyframe_insert("rotation_euler", frame=1720)

# Rises back up from bow with a glowing innocent smile
tri_torso.rotation_euler = (0, 0, 0)
tri_head.rotation_euler = (0, 0, 0)
tri_arm_up_l.rotation_euler = (0, 0, 0)
tri_arm_up_r.rotation_euler = (0, 0, 0)
tri_torso.keyframe_insert("rotation_euler", frame=1860)
tri_head.keyframe_insert("rotation_euler", frame=1860)
tri_arm_up_l.keyframe_insert("rotation_euler", frame=1860)
tri_arm_up_r.keyframe_insert("rotation_euler", frame=1860)

# Snap Zoom into Triboulet's face when delivering the Queen punchline (Frame 1920)
cam_obj.location = (-0.5, -4.2, -0.1)
cam_obj.keyframe_insert("location", frame=1940)
cam_obj.location = (-0.5, -4.2, -0.1)
cam_obj.keyframe_insert("location", frame=2100)

# SHOT 5 (Frames 2161 - 2700): The Death Sentence & Royal Grace
cam_obj.location = (0.2, -7.2, 0.1)
cam_obj.rotation_euler = (math.radians(90), 0, 0)
cam_obj.keyframe_insert("location", frame=2161)
cam_obj.keyframe_insert("rotation_euler", frame=2161)

# King gestures solemnly
king_arm_up_l.rotation_euler = (0, 0, math.radians(-30))
king_arm_low_l.rotation_euler = (0, 0, math.radians(-15))
king_torso.rotation_euler = (0, 0, math.radians(5))
king_arm_up_l.keyframe_insert("rotation_euler", frame=2300)
king_arm_low_l.keyframe_insert("rotation_euler", frame=2300)
king_torso.keyframe_insert("rotation_euler", frame=2300)

# SHOT 6 (Frames 2701 - 3472): The Punchline & Court Laughter!
# Snap Push-in on Triboulet: "I choose to die of old age!"
cam_obj.location = (-0.5, -4.5, -0.1)
cam_obj.keyframe_insert("location", frame=2701)

# Triboulet points triumphantly to the heavens!
tri_arm_up_r.rotation_euler = (0, 0, math.radians(85))
tri_arm_low_r.rotation_euler = (0, 0, math.radians(45))
tri_head.rotation_euler = (0, 0, math.radians(-15))
tri_arm_up_r.keyframe_insert("rotation_euler", frame=2780)
tri_arm_low_r.keyframe_insert("rotation_euler", frame=2780)
tri_head.keyframe_insert("rotation_euler", frame=2780)

# Cut to King Francis bursting into laughter! (Frame 2880)
cam_obj.location = (1.1, -4.6, 0.1)
cam_obj.keyframe_insert("location", frame=2880)

# King Francis head tilts back in roaring laughter
for f in range(2900, 3200, 30):
    king_head.rotation_euler = (0, 0, math.radians(-25))
    king_torso.rotation_euler = (0, 0, math.radians(-10))
    king_head.keyframe_insert("rotation_euler", frame=f)
    king_torso.keyframe_insert("rotation_euler", frame=f)
    
    king_head.rotation_euler = (0, 0, math.radians(5))
    king_torso.rotation_euler = (0, 0, math.radians(2))
    king_head.keyframe_insert("rotation_euler", frame=f+15)
    king_torso.keyframe_insert("rotation_euler", frame=f+15)

# Pull-out to grand cinematic wide resolution shot (Frames 3200 - 3472)
cam_obj.location = (0.0, -8.6, 0.2)
cam_obj.rotation_euler = (math.radians(90), 0, 0)
cam_obj.keyframe_insert("location", frame=3400)
cam_obj.keyframe_insert("rotation_euler", frame=3400)

# Increase sun rim intensity to golden victory rays
rim_light.energy = 5.0
rim_light.keyframe_insert("energy", frame=2900)

print("[*] Starting full 3,472 frame render to:", r"{output_video}")
bpy.ops.render.render(animation=True)
print("[+] Render finished successfully!")
"""

def render_blender_animation():
    script_path = os.path.abspath("temp_master_render.py")
    script_content = BLENDER_SCRIPT.replace("{output_video}", OUTPUT_RAW_VIDEO.replace("\\", "\\\\"))
    with open(script_path, "w", encoding="utf-8") as f:
        f.write(script_content)
        
    blender_exe = r"C:\Program Files\Blender Foundation\Blender 4.2\blender.exe"
    cmd = [blender_exe, "-b", "--python", script_path]
    print("[*] Launching Blender 4.2 animation render (3,472 frames)...")
    res = subprocess.run(cmd, text=True)
    if res.returncode != 0:
        print("[!] Error in Blender render!")
    else:
        print(f"[+] Blender animation rendered successfully to: {OUTPUT_RAW_VIDEO}")

def mux_final_video():
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    audio_voice = os.path.abspath("output/audio_triboulet.mp3")
    bgm_lute = os.path.abspath("assets/audio/bgm_renaissance_lute.wav")
    sfx_bells = os.path.abspath("assets/audio/sfx_jester_bells.wav")
    sfx_slap = os.path.abspath("assets/audio/sfx_slap_impact.wav")
    sfx_gasp = os.path.abspath("assets/audio/sfx_court_gasp.wav")
    sfx_chime = os.path.abspath("assets/audio/sfx_triumph_chime.wav")
    sfx_laughter = os.path.abspath("assets/audio/sfx_court_laughter.wav")
    subtitles_ass = os.path.abspath("output/subtitles_triboulet.ass").replace("\\", "/")
    
    print("[*] Compositing multi-track audio and burning kinetic subtitles...")
    
    # Complex audio filtergraph:
    # 0: video
    # 1: voiceover
    # 2: bgm lute (volume=0.18)
    # 3: sfx bells (delay=1000ms and 10000ms)
    # 4: sfx slap (delay=38160ms)
    # 5: sfx gasp (delay=38700ms)
    # 6: sfx chime (delay=92500ms)
    # 7: sfx laughter (delay=96000ms)
    filter_complex = (
        "[2:a]volume=0.18[bgm];"
        "[3:a]adelay=1000|1000,volume=0.6[b1];"
        "[4:a]adelay=38160|38160,volume=1.2[slap];"
        "[5:a]adelay=38700|38700,volume=0.8[gasp];"
        "[6:a]adelay=92500|92500,volume=0.9[chime];"
        "[7:a]adelay=96000|96000,volume=0.8[laugh];"
        "[1:a][bgm][b1][slap][gasp][chime][laugh]amix=inputs=7:duration=longest:dropout_transition=2[aout];"
        f"[0:v]subtitles='{subtitles_ass}'[vout]"
    )
    
    cmd = [
        ffmpeg_exe, "-y",
        "-i", OUTPUT_RAW_VIDEO,
        "-i", audio_voice,
        "-i", bgm_lute,
        "-i", sfx_bells,
        "-i", sfx_slap,
        "-i", sfx_gasp,
        "-i", sfx_chime,
        "-i", sfx_laughter,
        "-filter_complex", filter_complex,
        "-map", "[vout]",
        "-map", "[aout]",
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "18",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        FINAL_EXPORT_VIDEO
    ]
    
    print(f"[*] Running FFmpeg composite export -> {FINAL_EXPORT_VIDEO}...")
    res = subprocess.run(cmd, text=True)
    if res.returncode == 0:
        print(f"[+] FINAL MASTERPIECE EXPORTED SUCCESSFULLY: {FINAL_EXPORT_VIDEO}")
    else:
        print("[!] FFmpeg export error!")

if __name__ == "__main__":
    render_blender_animation()
    mux_final_video()
