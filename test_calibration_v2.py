"""
=============================================================================
RENDER CALIBRATION TEST WITH V2 CARTOON ASSETS
=============================================================================
"""

import bpy
import math
import os

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.render.resolution_x = 1080
scene.render.resolution_y = 1920
scene.render.engine = 'BLENDER_EEVEE_NEXT'

# Camera
cam_data = bpy.data.cameras.new("Cam")
cam_data.lens = 38
cam_obj = bpy.data.objects.new("Camera", cam_data)
bpy.context.collection.objects.link(cam_obj)
scene.camera = cam_obj
cam_obj.location = (0.0, -8.0, 0.0)
cam_obj.rotation_euler = (math.radians(90), 0, 0)

# World
world = bpy.data.worlds.new("W")
scene.world = world
world.use_nodes = True
bg = world.node_tree.nodes.get("Background")
bg.inputs['Color'].default_value = (0.05, 0.04, 0.07, 1.0)
bg.inputs['Strength'].default_value = 1.0

# 3-Point Lights
key_light = bpy.data.lights.new("Key", type='SPOT')
key_light.energy = 2500
key_light.color = (1.0, 0.95, 0.85)
key_light.spot_size = math.radians(75)
key_obj = bpy.data.objects.new("Light_Key", key_light)
bpy.context.collection.objects.link(key_obj)
key_obj.location = (-2.5, -5.0, 3.5)
key_obj.rotation_euler = (math.radians(45), math.radians(-15), 0)

fill_light = bpy.data.lights.new("Fill", type='POINT')
fill_light.energy = 700
fill_light.color = (0.6, 0.7, 0.95)
fill_obj = bpy.data.objects.new("Light_Fill", fill_light)
bpy.context.collection.objects.link(fill_obj)
fill_obj.location = (3.0, -4.0, 1.5)

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
    
    verts = [
        (x_min, 0, z_min),
        (x_max, 0, z_min),
        (x_max, 0, z_max),
        (x_min, 0, z_max)
    ]
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

def build_v2_triboulet(root_loc=(-0.9, 0, -1.3), scale=1.4):
    char_dir = os.path.join("assets", "character_rigs_v2", "triboulet")
    s = scale
    
    root = bpy.data.objects.new("Triboulet_Root", None)
    root.location = root_loc
    bpy.context.collection.objects.link(root)
    
    torso_h = 0.75 * s
    torso = create_sprite_mesh("Tri_Torso", os.path.join(char_dir, "torso.png"),
                               width=0.6*s, height=torso_h, pivot=(0.5, 0.0))
    torso.parent = root
    torso.location = (0, 0, 0.65*s)
    
    head_h = 0.6 * s
    head = create_sprite_mesh("Tri_Head", os.path.join(char_dir, "head_smirk.png"),
                              width=0.6*s, height=head_h, pivot=(0.5, 0.1))
    head.parent = torso
    head.location = (0, -0.01, torso_h - 0.12*s)
    
    cap = create_sprite_mesh("Tri_Cap", os.path.join(char_dir, "jester_cap.png"),
                             width=0.9*s, height=0.65*s, pivot=(0.5, 0.35))
    cap.parent = head
    cap.location = (0, -0.02, head_h * 0.52)
    
    # Left Arm
    arm_up_l = create_sprite_mesh("Tri_ArmUp_L", os.path.join(char_dir, "upper_arm_left.png"),
                                  width=0.22*s, height=0.42*s, pivot=(0.5, 0.9))
    arm_up_l.parent = torso
    arm_up_l.location = (0.22*s, 0.01, torso_h * 0.8)
    arm_up_l.rotation_euler = (0, 0, math.radians(-18))
    
    arm_low_l = create_sprite_mesh("Tri_ArmLow_L", os.path.join(char_dir, "lower_arm_left.png"),
                                   width=0.18*s, height=0.38*s, pivot=(0.5, 0.9))
    arm_low_l.parent = arm_up_l
    arm_low_l.location = (0.0, 0.01, -0.34*s)
    arm_low_l.rotation_euler = (0, 0, math.radians(-28))
    
    hand_l = create_sprite_mesh("Tri_Hand_L", os.path.join(char_dir, "hand_open.png"),
                                width=0.25*s, height=0.25*s, pivot=(0.5, 0.85))
    hand_l.parent = arm_low_l
    hand_l.location = (0.0, 0.01, -0.32*s)
    
    # Right Arm (pointing)
    arm_up_r = create_sprite_mesh("Tri_ArmUp_R", os.path.join(char_dir, "upper_arm_right.png"),
                                  width=0.22*s, height=0.42*s, pivot=(0.5, 0.9))
    arm_up_r.parent = torso
    arm_up_r.location = (-0.22*s, -0.01, torso_h * 0.8)
    arm_up_r.rotation_euler = (0, 0, math.radians(25))
    
    arm_low_r = create_sprite_mesh("Tri_ArmLow_R", os.path.join(char_dir, "lower_arm_right.png"),
                                   width=0.18*s, height=0.38*s, pivot=(0.5, 0.9))
    arm_low_r.parent = arm_up_r
    arm_low_r.location = (0.0, -0.01, -0.34*s)
    arm_low_r.rotation_euler = (0, 0, math.radians(40))
    
    hand_r = create_sprite_mesh("Tri_Hand_R", os.path.join(char_dir, "hand_point.png"),
                                width=0.28*s, height=0.24*s, pivot=(0.5, 0.85))
    hand_r.parent = arm_low_r
    hand_r.location = (0.0, -0.01, -0.32*s)
    
    # Legs
    leg_up_l = create_sprite_mesh("Tri_LegUp_L", os.path.join(char_dir, "upper_leg_left.png"),
                                  width=0.22*s, height=0.45*s, pivot=(0.5, 0.95))
    leg_up_l.parent = root
    leg_up_l.location = (0.12*s, 0.01, 0.65*s)
    
    leg_low_l = create_sprite_mesh("Tri_LegLow_L", os.path.join(char_dir, "lower_leg_left.png"),
                                   width=0.19*s, height=0.45*s, pivot=(0.5, 0.95))
    leg_low_l.parent = leg_up_l
    leg_low_l.location = (0.0, 0.01, -0.38*s)
    
    foot_l = create_sprite_mesh("Tri_Foot_L", os.path.join(char_dir, "foot_left.png"),
                                width=0.36*s, height=0.24*s, pivot=(0.3, 0.85))
    foot_l.parent = leg_low_l
    foot_l.location = (0.03*s, 0.01, -0.4*s)
    
    # Right Leg
    leg_up_r = create_sprite_mesh("Tri_LegUp_R", os.path.join(char_dir, "upper_leg_right.png"),
                                  width=0.22*s, height=0.45*s, pivot=(0.5, 0.95))
    leg_up_r.parent = root
    leg_up_r.location = (-0.12*s, -0.01, 0.65*s)
    
    leg_low_r = create_sprite_mesh("Tri_LegLow_R", os.path.join(char_dir, "lower_leg_right.png"),
                                   width=0.19*s, height=0.45*s, pivot=(0.5, 0.95))
    leg_low_r.parent = leg_up_r
    leg_low_r.location = (0.0, -0.01, -0.38*s)
    
    foot_r = create_sprite_mesh("Tri_Foot_R", os.path.join(char_dir, "foot_right.png"),
                                width=0.36*s, height=0.24*s, pivot=(0.7, 0.85))
    foot_r.parent = leg_low_r
    foot_r.location = (-0.03*s, -0.01, -0.4*s)
    
    return root

def build_v2_king(root_loc=(1.1, 0.2, -0.9), scale=1.55):
    char_dir = os.path.join("assets", "character_rigs_v2", "king_francis")
    s = scale
    
    root = bpy.data.objects.new("King_Root", None)
    root.location = root_loc
    bpy.context.collection.objects.link(root)
    
    torso_h = 0.85 * s
    torso = create_sprite_mesh("King_Torso", os.path.join(char_dir, "torso.png"),
                               width=0.85*s, height=torso_h, pivot=(0.5, 0.0))
    torso.parent = root
    torso.location = (0, 0, 0.25*s)
    
    head_h = 0.65 * s
    head = create_sprite_mesh("King_Head", os.path.join(char_dir, "head_furious.png"),
                              width=0.6*s, height=head_h, pivot=(0.5, 0.15))
    head.parent = torso
    head.location = (0, -0.01, torso_h - 0.15*s)
    
    crown = create_sprite_mesh("King_Crown", os.path.join(char_dir, "royal_crown.png"),
                               width=0.68*s, height=0.4*s, pivot=(0.5, 0.35))
    crown.parent = head
    crown.location = (0, -0.02, head_h * 0.6)
    
    # Left Arm (pointing toward Triboulet)
    arm_up_l = create_sprite_mesh("King_ArmUp_L", os.path.join(char_dir, "upper_arm_left.png"),
                                  width=0.36*s, height=0.46*s, pivot=(0.5, 0.9))
    arm_up_l.parent = torso
    arm_up_l.location = (-0.34*s, -0.01, torso_h * 0.75)
    arm_up_l.rotation_euler = (0, 0, math.radians(-40))
    
    arm_low_l = create_sprite_mesh("King_ArmLow_L", os.path.join(char_dir, "lower_arm_left.png"),
                                   width=0.25*s, height=0.42*s, pivot=(0.5, 0.9))
    arm_low_l.parent = arm_up_l
    arm_low_l.location = (0.0, -0.01, -0.38*s)
    arm_low_l.rotation_euler = (0, 0, math.radians(-30))
    
    hand_l = create_sprite_mesh("King_Hand_L", os.path.join(char_dir, "hand_left.png"),
                                width=0.28*s, height=0.24*s, pivot=(0.5, 0.85))
    hand_l.parent = arm_low_l
    hand_l.location = (0.0, -0.01, -0.35*s)
    
    # Right Arm
    arm_up_r = create_sprite_mesh("King_ArmUp_R", os.path.join(char_dir, "upper_arm_right.png"),
                                  width=0.36*s, height=0.46*s, pivot=(0.5, 0.9))
    arm_up_r.parent = torso
    arm_up_r.location = (0.34*s, 0.01, torso_h * 0.75)
    arm_up_r.rotation_euler = (0, 0, math.radians(15))
    
    arm_low_r = create_sprite_mesh("King_ArmLow_R", os.path.join(char_dir, "lower_arm_right.png"),
                                   width=0.25*s, height=0.42*s, pivot=(0.5, 0.9))
    arm_low_r.parent = arm_up_r
    arm_low_r.location = (0.0, 0.01, -0.38*s)
    
    hand_r = create_sprite_mesh("King_Hand_R", os.path.join(char_dir, "hand_right.png"),
                                width=0.26*s, height=0.26*s, pivot=(0.5, 0.85))
    hand_r.parent = arm_low_r
    hand_r.location = (0.0, 0.01, -0.35*s)
    
    return root

# Multiplane Environment Staging
env_dir = os.path.join("assets", "environments", "renaissance_court")

deep_bg = create_sprite_mesh("Env_DeepBG", os.path.join(env_dir, "deep_background.png"), 13.0, 8.0, (0.5, 0.5))
deep_bg.location = (0, 10.0, 1.2)

wall = create_sprite_mesh("Env_Wall", os.path.join(env_dir, "midground_wall.png"), 10.0, 6.5, (0.5, 0.5))
wall.location = (0, 4.5, 0.6)

throne = create_sprite_mesh("Env_Throne", os.path.join(env_dir, "throne_dais.png"), 3.4, 3.4, (0.5, 0.5))
throne.location = (1.1, 0.6, -0.4)

floor = create_sprite_mesh("Env_Floor", os.path.join(env_dir, "marble_floor.png"), 12.0, 10.0, (0.5, 0.5))
floor.rotation_euler = (math.radians(-90), 0, 0)
floor.location = (0, 1.5, -2.1)

# Foreground framing pillars (providing depth)
fg = create_sprite_mesh("Env_FG", os.path.join(env_dir, "foreground_framing.png"), 5.6, 9.8, (0.5, 0.5))
fg.location = (0, -4.5, 0.0)

# Build characters
build_v2_triboulet()
build_v2_king()

out_path = os.path.abspath("output/test_v2_frame.png")
scene.render.filepath = out_path
bpy.ops.render.render(write_still=True)
print(f"[+] Rendered V2 frame -> {out_path}")
