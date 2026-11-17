"""
=============================================================================
BLENDER 2D/2.5D CINEMATIC PIPELINE - RENAISSANCE COURT & CHARACTER RIGS
=============================================================================
Assembles a complete multiplane 2.5D environment in Blender 4.2 with
EEVEE-Next, constructs skeletal armatures with textured 2D sprite cards,
animates locomotion, gestures, expressions, camera parallax, and renders
vertical 1080x1920 video.
=============================================================================
"""

import sys
import os
import math

# Parse arguments passed after "--"
argv = sys.argv
args = []
if "--" in argv:
    args = argv[argv.index("--") + 1:]

is_preview = "--preview" in args
total_frames = 300 if is_preview else 900  # 10s preview or full scene
output_file = "output/preview_2d_25d.mp4" if is_preview else "output/triboulet_raw.mp4"

for i, arg in enumerate(args):
    if arg == "--output" and i + 1 < len(args):
        output_file = args[i + 1]
    if arg == "--frames" and i + 1 < len(args):
        total_frames = int(args[i + 1])

import bpy

def setup_scene():
    """Initializes clean scene, render settings, and camera."""
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    
    # Render Settings for 1080x1920 Vertical Video @ 30 FPS
    scene.render.resolution_x = 1080
    scene.render.resolution_y = 1920
    scene.render.resolution_percentage = 100
    scene.render.fps = 30
    scene.frame_start = 1
    scene.frame_end = total_frames
    
    scene.render.engine = 'BLENDER_EEVEE_NEXT'
    
    # Color management: Filmic or AgX with High Contrast
    if hasattr(scene, "view_settings"):
        try:
            scene.view_settings.view_transform = 'AgX'
            scene.view_settings.look = 'Medium High Contrast'
        except Exception:
            scene.view_settings.view_transform = 'Filmic'
            
    # Video output configuration
    scene.render.image_settings.file_format = 'FFMPEG'
    scene.render.ffmpeg.format = 'MPEG4'
    scene.render.ffmpeg.codec = 'H264'
    scene.render.ffmpeg.constant_rate_factor = 'MEDIUM'
    scene.render.ffmpeg.ffmpeg_preset = 'REALTIME' if is_preview else 'GOOD'
    scene.render.filepath = os.path.abspath(output_file)
    
    # Ambient World Color
    world = bpy.data.worlds.new("RenaissanceWorld")
    scene.world = world
    world.use_nodes = True
    bg_node = world.node_tree.nodes.get("Background")
    if bg_node:
        bg_node.inputs['Color'].default_value = (0.04, 0.03, 0.06, 1.0)
        bg_node.inputs['Strength'].default_value = 0.6
        
    return scene

def create_sprite_material(name, image_path, is_emission=False):
    """Creates a transparent Principled BSDF material for 2D sprites."""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    output_node = nodes.new(type='ShaderNodeOutputMaterial')
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    tex_node = nodes.new(type='ShaderNodeTexImage')
    
    if os.path.exists(image_path):
        img = bpy.data.images.load(os.path.abspath(image_path))
        tex_node.image = img
    else:
        print(f"[!] Warning: Image not found: {image_path}")
        
    # Connect color and alpha
    links.new(tex_node.outputs['Color'], bsdf.inputs['Base Color'])
    links.new(tex_node.outputs['Alpha'], bsdf.inputs['Alpha'])
    
    if is_emission:
        links.new(tex_node.outputs['Color'], bsdf.inputs['Emission Color'])
        bsdf.inputs['Emission Strength'].default_value = 0.5
        
    bsdf.inputs['Roughness'].default_value = 0.8
    links.new(bsdf.outputs['BSDF'], output_node.inputs['Surface'])
    
    # Alpha blend mode in EEVEE
    if hasattr(mat, 'blend_method'):
        mat.blend_method = 'BLEND'
    if hasattr(mat, 'shadow_method'):
        mat.shadow_method = 'CLIP'
        
    return mat

def create_environment_layers():
    """Builds multiplane Renaissance staging layers."""
    env_dir = os.path.join("assets", "environments", "renaissance_court")
    
    # 1. Deep Background Window (Y = 14.0, Z = 0.8)
    bg_mat = create_sprite_material("Mat_DeepBG", os.path.join(env_dir, "deep_background.png"), is_emission=True)
    bpy.ops.mesh.primitive_plane_add(size=1.0, location=(0, 14.0, 1.2))
    bg_plane = bpy.context.active_object
    bg_plane.name = "Env_DeepBG"
    bg_plane.rotation_euler = (math.radians(90), 0, 0)
    bg_plane.scale = (14.0, 1.0, 7.8)
    bg_plane.data.materials.append(bg_mat)
    
    # 2. Midground Wall & Banners (Y = 7.0, Z = 0.2)
    mg_mat = create_sprite_material("Mat_MidWall", os.path.join(env_dir, "midground_wall.png"))
    bpy.ops.mesh.primitive_plane_add(size=1.0, location=(0, 7.0, 0.4))
    mg_plane = bpy.context.active_object
    mg_plane.name = "Env_MidWall"
    mg_plane.rotation_euler = (math.radians(90), 0, 0)
    mg_plane.scale = (11.0, 1.0, 7.3)
    mg_plane.data.materials.append(mg_mat)
    
    # 3. Throne Dais (Y = 1.6, X = 1.3, Z = -0.5)
    throne_mat = create_sprite_material("Mat_Throne", os.path.join(env_dir, "throne_dais.png"))
    bpy.ops.mesh.primitive_plane_add(size=1.0, location=(1.3, 1.6, -0.4))
    throne_plane = bpy.context.active_object
    throne_plane.name = "Env_ThroneDais"
    throne_plane.rotation_euler = (math.radians(90), 0, 0)
    throne_plane.scale = (3.4, 1.0, 3.4)
    throne_plane.data.materials.append(throne_mat)
    
    # 4. Polished Marble Floor (Y = 2.0, Z = -2.1)
    floor_mat = create_sprite_material("Mat_Floor", os.path.join(env_dir, "marble_floor.png"))
    bpy.ops.mesh.primitive_plane_add(size=1.0, location=(0, 3.0, -2.1))
    floor_plane = bpy.context.active_object
    floor_plane.name = "Env_Floor"
    floor_plane.rotation_euler = (0, 0, 0)
    floor_plane.scale = (12.0, 16.0, 1.0)
    floor_plane.data.materials.append(floor_mat)
    
    # 5. Foreground Framing Pillars & Valance (Y = -4.0, Z = 0.0)
    fg_mat = create_sprite_material("Mat_Foreground", os.path.join(env_dir, "foreground_framing.png"))
    bpy.ops.mesh.primitive_plane_add(size=1.0, location=(0, -4.0, 0.0))
    fg_plane = bpy.context.active_object
    fg_plane.name = "Env_ForegroundFraming"
    fg_plane.rotation_euler = (math.radians(90), 0, 0)
    fg_plane.scale = (5.6, 1.0, 9.8)
    fg_plane.data.materials.append(fg_mat)

def setup_lighting():
    """Sets up 3-point cinematic Renaissance lighting."""
    # 1. Warm Key Spotlight (Amber chandelier illumination)
    key_light_data = bpy.data.lights.new(name="Key_Chandelier", type='SPOT')
    key_light_data.energy = 1200
    key_light_data.color = (1.0, 0.88, 0.72)
    key_light_data.spot_size = math.radians(65)
    key_light_data.spot_blend = 0.4
    key_light_obj = bpy.data.objects.new(name="Light_Key", object_data=key_light_data)
    bpy.context.collection.objects.link(key_light_obj)
    key_light_obj.location = (-2.5, -4.5, 4.5)
    key_light_obj.rotation_euler = (math.radians(35), math.radians(-15), math.radians(-25))
    
    # 2. Cool Fill Light (Azure ambient court fill)
    fill_light_data = bpy.data.lights.new(name="Fill_Court", type='POINT')
    fill_light_data.energy = 450
    fill_light_data.color = (0.55, 0.65, 0.95)
    fill_light_obj = bpy.data.objects.new(name="Light_Fill", object_data=fill_light_data)
    bpy.context.collection.objects.link(fill_light_obj)
    fill_light_obj.location = (3.5, -3.0, 2.5)
    
    # 3. Dramatic Rim / Sunlight from Rose Window
    rim_light_data = bpy.data.lights.new(name="Rim_Sunlight", type='SUN')
    rim_light_data.energy = 2.5
    rim_light_data.color = (0.95, 0.90, 1.0)
    rim_light_obj = bpy.data.objects.new(name="Light_Rim", object_data=rim_light_data)
    bpy.context.collection.objects.link(rim_light_obj)
    rim_light_obj.location = (0, 12.0, 5.0)
    rim_light_obj.rotation_euler = (math.radians(-40), 0, math.radians(180))

def create_sprite_card(name, mat, scale, location=(0,0,0)):
    """Helper to create a textured quad sprite card."""
    bpy.ops.mesh.primitive_plane_add(size=1.0, location=location)
    plane = bpy.context.active_object
    plane.name = name
    plane.rotation_euler = (math.radians(90), 0, 0)
    plane.scale = (scale[0], 1.0, scale[1])
    plane.data.materials.append(mat)
    return plane

def build_triboulet_rig():
    """Builds skeletal armature and mounts 2D modular sprite parts for Triboulet."""
    char_dir = os.path.join("assets", "character_rigs", "triboulet")
    
    # Create Armature
    bpy.ops.object.armature_add(enter_editmode=True, align='WORLD', location=(0, 0, 0))
    arm_obj = bpy.context.active_object
    arm_obj.name = "Rig_Triboulet"
    arm_data = arm_obj.data
    
    ebones = arm_data.edit_bones
    root = ebones[0]
    root.name = "root"
    root.head = (0, 0, -1.8)
    root.tail = (0, 0, -1.0)
    
    # Torso
    torso = ebones.new("torso")
    torso.head = (0, 0, -1.0)
    torso.tail = (0, 0, -0.3)
    torso.parent = root
    
    # Head
    head = ebones.new("head")
    head.head = (0, 0, -0.3)
    head.tail = (0, 0, 0.4)
    head.parent = torso
    
    # Left Arm
    arm_up_l = ebones.new("arm_upper_L")
    arm_up_l.head = (-0.35, 0, -0.4)
    arm_up_l.tail = (-0.6, 0, -0.8)
    arm_up_l.parent = torso
    
    arm_low_l = ebones.new("arm_lower_L")
    arm_low_l.head = (-0.6, 0, -0.8)
    arm_low_l.tail = (-0.8, 0, -1.2)
    arm_low_l.parent = arm_up_l
    
    hand_l = ebones.new("hand_L")
    hand_l.head = (-0.8, 0, -1.2)
    hand_l.tail = (-0.95, 0, -1.35)
    hand_l.parent = arm_low_l
    
    # Right Arm
    arm_up_r = ebones.new("arm_upper_R")
    arm_up_r.head = (0.35, 0, -0.4)
    arm_up_r.tail = (0.6, 0, -0.8)
    arm_up_r.parent = torso
    
    arm_low_r = ebones.new("arm_lower_R")
    arm_low_r.head = (0.6, 0, -0.8)
    arm_low_r.tail = (0.8, 0, -1.2)
    arm_low_r.parent = arm_up_r
    
    hand_r = ebones.new("hand_R")
    hand_r.head = (0.8, 0, -1.2)
    hand_r.tail = (0.95, 0, -1.35)
    hand_r.parent = arm_low_r
    
    # Left Leg
    leg_up_l = ebones.new("leg_upper_L")
    leg_up_l.head = (-0.2, 0, -1.0)
    leg_up_l.tail = (-0.22, 0, -1.5)
    leg_up_l.parent = root
    
    leg_low_l = ebones.new("leg_lower_L")
    leg_low_l.head = (-0.22, 0, -1.5)
    leg_low_l.tail = (-0.22, 0, -1.95)
    leg_low_l.parent = leg_up_l
    
    foot_l = ebones.new("foot_L")
    foot_l.head = (-0.22, 0, -1.95)
    foot_l.tail = (-0.45, 0, -2.05)
    foot_l.parent = leg_low_l
    
    # Right Leg
    leg_up_r = ebones.new("leg_upper_R")
    leg_up_r.head = (0.2, 0, -1.0)
    leg_up_r.tail = (0.22, 0, -1.5)
    leg_up_r.parent = root
    
    leg_low_r = ebones.new("leg_lower_R")
    leg_low_r.head = (0.22, 0, -1.5)
    leg_low_r.tail = (0.22, 0, -1.95)
    leg_low_r.parent = leg_up_r
    
    foot_r = ebones.new("foot_R")
    foot_r.head = (0.22, 0, -1.95)
    foot_r.tail = (0.45, 0, -2.05)
    foot_r.parent = leg_low_r
    
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # Create Materials and attach Sprite Cards to Bones
    parts = [
        ("torso", os.path.join(char_dir, "torso.png"), (0.75, 0.95), "torso", (0, -0.01, -0.65)),
        ("head_neutral", os.path.join(char_dir, "head_neutral.png"), (0.65, 0.75), "head", (0, -0.02, 0.05)),
        ("jester_cap", os.path.join(char_dir, "jester_cap.png"), (1.1, 0.9), "head", (0, -0.03, 0.35)),
        ("arm_upper_L", os.path.join(char_dir, "upper_arm_left.png"), (0.35, 0.55), "arm_upper_L", (-0.45, 0.01, -0.6)),
        ("arm_lower_L", os.path.join(char_dir, "lower_arm_left.png"), (0.3, 0.55), "arm_lower_L", (-0.7, 0.01, -1.0)),
        ("hand_L", os.path.join(char_dir, "hand_open.png"), (0.35, 0.35), "hand_L", (-0.88, 0.01, -1.28)),
        ("arm_upper_R", os.path.join(char_dir, "upper_arm_right.png"), (0.35, 0.55), "arm_upper_R", (0.45, -0.01, -0.6)),
        ("arm_lower_R", os.path.join(char_dir, "lower_arm_right.png"), (0.3, 0.55), "arm_lower_R", (0.7, -0.01, -1.0)),
        ("hand_R", os.path.join(char_dir, "hand_point.png"), (0.35, 0.35), "hand_R", (0.88, -0.01, -1.28)),
        ("leg_upper_L", os.path.join(char_dir, "upper_leg_left.png"), (0.38, 0.6), "leg_upper_L", (-0.2, 0.01, -1.25)),
        ("leg_lower_L", os.path.join(char_dir, "lower_leg_left.png"), (0.32, 0.6), "leg_lower_L", (-0.22, 0.01, -1.7)),
        ("foot_L", os.path.join(char_dir, "foot_left.png"), (0.5, 0.35), "foot_L", (-0.32, 0.01, -2.0)),
        ("leg_upper_R", os.path.join(char_dir, "upper_leg_right.png"), (0.38, 0.6), "leg_upper_R", (0.2, -0.01, -1.25)),
        ("leg_lower_R", os.path.join(char_dir, "lower_leg_right.png"), (0.32, 0.6), "leg_lower_R", (0.22, -0.01, -1.7)),
        ("foot_R", os.path.join(char_dir, "foot_right.png"), (0.5, 0.35), "foot_R", (0.32, -0.01, -2.0)),
    ]
    
    for pname, pimg, pscale, pbone, ploc in parts:
        mat = create_sprite_material(f"Mat_Tri_{pname}", pimg)
        card = create_sprite_card(f"Sprite_Tri_{pname}", mat, pscale, location=ploc)
        card.parent = arm_obj
        card.parent_type = 'BONE'
        card.parent_bone = pbone
        
    return arm_obj

def build_king_francis_rig():
    """Builds skeletal armature and mounts 2D modular sprite parts for King Francis I."""
    char_dir = os.path.join("assets", "character_rigs", "king_francis")
    
    # King is seated at throne location (X = 1.35, Y = 1.3, Z = 0.0)
    bpy.ops.object.armature_add(enter_editmode=True, align='WORLD', location=(1.35, 1.3, 0.0))
    arm_obj = bpy.context.active_object
    arm_obj.name = "Rig_KingFrancis"
    arm_data = arm_obj.data
    
    ebones = arm_data.edit_bones
    root = ebones[0]
    root.name = "root"
    root.head = (0, 0, -1.4)
    root.tail = (0, 0, -0.6)
    
    torso = ebones.new("torso")
    torso.head = (0, 0, -0.6)
    torso.tail = (0, 0, 0.2)
    torso.parent = root
    
    head = ebones.new("head")
    head.head = (0, 0, 0.2)
    head.tail = (0, 0, 1.0)
    head.parent = torso
    
    # Left Arm (King's right hand gestures or grips armrest)
    arm_up_l = ebones.new("arm_upper_L")
    arm_up_l.head = (-0.5, 0, 0.0)
    arm_up_l.tail = (-0.85, 0, -0.4)
    arm_up_l.parent = torso
    
    arm_low_l = ebones.new("arm_lower_L")
    arm_low_l.head = (-0.85, 0, -0.4)
    arm_low_l.tail = (-1.05, 0, -0.7)
    arm_low_l.parent = arm_up_l
    
    hand_l = ebones.new("hand_L")
    hand_l.head = (-1.05, 0, -0.7)
    hand_l.tail = (-1.25, 0, -0.85)
    hand_l.parent = arm_low_l
    
    # Right Arm (holds royal scepter / points decree)
    arm_up_r = ebones.new("arm_upper_R")
    arm_up_r.head = (0.5, 0, 0.0)
    arm_up_r.tail = (0.85, 0, -0.4)
    arm_up_r.parent = torso
    
    arm_low_r = ebones.new("arm_lower_R")
    arm_low_r.head = (0.85, 0, -0.4)
    arm_low_r.tail = (1.05, 0, -0.7)
    arm_low_r.parent = arm_up_r
    
    hand_r = ebones.new("hand_R")
    hand_r.head = (1.05, 0, -0.7)
    hand_r.tail = (1.25, 0, -0.85)
    hand_r.parent = arm_low_r
    
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # Attach sprite cards
    parts = [
        ("torso", os.path.join(char_dir, "torso.png"), (1.1, 1.3), "torso", (1.35, 1.28, -0.3)),
        ("head_regal", os.path.join(char_dir, "head_regal.png"), (0.8, 0.95), "head", (1.35, 1.27, 0.6)),
        ("crown", os.path.join(char_dir, "royal_crown.png"), (0.9, 0.55), "head", (1.35, 1.26, 1.05)),
        ("arm_upper_L", os.path.join(char_dir, "upper_arm_left.png"), (0.5, 0.65), "arm_upper_L", (0.8, 1.31, -0.2)),
        ("arm_lower_L", os.path.join(char_dir, "lower_arm_left.png"), (0.35, 0.55), "arm_lower_L", (0.45, 1.31, -0.55)),
        ("hand_L", os.path.join(char_dir, "hand_left.png"), (0.35, 0.35), "hand_L", (0.2, 1.31, -0.8)),
        ("arm_upper_R", os.path.join(char_dir, "upper_arm_right.png"), (0.5, 0.65), "arm_upper_R", (1.9, 1.29, -0.2)),
        ("arm_lower_R", os.path.join(char_dir, "lower_arm_right.png"), (0.35, 0.55), "arm_lower_R", (2.25, 1.29, -0.55)),
        ("hand_R", os.path.join(char_dir, "hand_right.png"), (0.35, 0.35), "hand_R", (2.5, 1.29, -0.8)),
    ]
    
    for pname, pimg, pscale, pbone, ploc in parts:
        mat = create_sprite_material(f"Mat_King_{pname}", pimg)
        card = create_sprite_card(f"Sprite_King_{pname}", mat, pscale, location=ploc)
        card.parent = arm_obj
        card.parent_type = 'BONE'
        card.parent_bone = pbone
        
    return arm_obj

def animate_scene(tri_rig, king_rig):
    """Keyframes walk cycles, bows, gestures, and cinematic camera choreography."""
    scene = bpy.context.scene
    
    # 1. Virtual Camera
    cam_data = bpy.data.cameras.new("CinematicCamera")
    cam_data.lens = 42  # 42mm portrait / cinematic lens
    cam_data.sensor_width = 36
    cam_obj = bpy.data.objects.new("Camera", cam_data)
    bpy.context.collection.objects.link(cam_obj)
    scene.camera = cam_obj
    
    # Camera choreography
    # Frame 1: Wide establishing shot framing the throne room through pillars
    cam_obj.location = (-1.2, -8.2, 0.4)
    cam_obj.rotation_euler = (math.radians(88), 0, math.radians(-8))
    cam_obj.keyframe_insert(data_path="location", frame=1)
    cam_obj.keyframe_insert(data_path="rotation_euler", frame=1)
    
    # Frame 90: Push-in tracking Triboulet's entrance
    cam_obj.location = (-0.5, -7.0, 0.2)
    cam_obj.rotation_euler = (math.radians(89), 0, math.radians(-4))
    cam_obj.keyframe_insert(data_path="location", frame=90)
    cam_obj.keyframe_insert(data_path="rotation_euler", frame=90)
    
    # Frame 180: Close-medium shot of Triboulet executing his theatrical bow
    cam_obj.location = (0.2, -6.0, 0.1)
    cam_obj.rotation_euler = (math.radians(90), 0, math.radians(2))
    cam_obj.keyframe_insert(data_path="location", frame=180)
    cam_obj.keyframe_insert(data_path="rotation_euler", frame=180)
    
    # Frame 300: Dramatic two-shot framing Triboulet and King Francis
    cam_obj.location = (0.5, -6.6, 0.3)
    cam_obj.rotation_euler = (math.radians(89), 0, math.radians(5))
    cam_obj.keyframe_insert(data_path="location", frame=300)
    cam_obj.keyframe_insert(data_path="rotation_euler", frame=300)
    
    # 2. Triboulet Walk Cycle & Entrance (Frames 1 - 90)
    # Starts at X = -2.8, walks to center stage X = -0.3
    tri_rig.location = (-2.8, 0, 0)
    tri_rig.keyframe_insert(data_path="location", frame=1)
    
    tri_rig.location = (-0.3, 0, 0)
    tri_rig.keyframe_insert(data_path="location", frame=90)
    
    # Walk cycle keyframes in Pose Mode
    pbones_tri = tri_rig.pose.bones
    for b in pbones_tri:
        b.rotation_mode = 'XYZ'
        
    step_duration = 18  # frames per full step cycle
    for f in range(1, 91, step_duration):
        # Step phase A: Left leg forward, Right leg back, arms counter-swing
        half = step_duration // 2
        # Frame f
        pbones_tri["leg_upper_L"].rotation_euler = (math.radians(25), 0, 0)
        pbones_tri["leg_upper_R"].rotation_euler = (math.radians(-25), 0, 0)
        pbones_tri["arm_upper_L"].rotation_euler = (math.radians(-20), 0, 0)
        pbones_tri["arm_upper_R"].rotation_euler = (math.radians(20), 0, 0)
        pbones_tri["torso"].location = (0, 0, 0.04)  # rhythmic bobbing
        
        pbones_tri["leg_upper_L"].keyframe_insert(data_path="rotation_euler", frame=f)
        pbones_tri["leg_upper_R"].keyframe_insert(data_path="rotation_euler", frame=f)
        pbones_tri["arm_upper_L"].keyframe_insert(data_path="rotation_euler", frame=f)
        pbones_tri["arm_upper_R"].keyframe_insert(data_path="rotation_euler", frame=f)
        pbones_tri["torso"].keyframe_insert(data_path="location", frame=f)
        
        # Frame f + half: Right leg forward, Left leg back
        f2 = min(f + half, 90)
        pbones_tri["leg_upper_L"].rotation_euler = (math.radians(-25), 0, 0)
        pbones_tri["leg_upper_R"].rotation_euler = (math.radians(25), 0, 0)
        pbones_tri["arm_upper_L"].rotation_euler = (math.radians(20), 0, 0)
        pbones_tri["arm_upper_R"].rotation_euler = (math.radians(-20), 0, 0)
        pbones_tri["torso"].location = (0, 0, -0.02)
        
        pbones_tri["leg_upper_L"].keyframe_insert(data_path="rotation_euler", frame=f2)
        pbones_tri["leg_upper_R"].keyframe_insert(data_path="rotation_euler", frame=f2)
        pbones_tri["arm_upper_L"].keyframe_insert(data_path="rotation_euler", frame=f2)
        pbones_tri["arm_upper_R"].keyframe_insert(data_path="rotation_euler", frame=f2)
        pbones_tri["torso"].keyframe_insert(data_path="location", frame=f2)
        
    # Return to neutral stance at frame 100
    pbones_tri["leg_upper_L"].rotation_euler = (0, 0, 0)
    pbones_tri["leg_upper_R"].rotation_euler = (0, 0, 0)
    pbones_tri["arm_upper_L"].rotation_euler = (0, 0, 0)
    pbones_tri["arm_upper_R"].rotation_euler = (0, 0, 0)
    pbones_tri["torso"].location = (0, 0, 0)
    pbones_tri["leg_upper_L"].keyframe_insert(data_path="rotation_euler", frame=100)
    pbones_tri["leg_upper_R"].keyframe_insert(data_path="rotation_euler", frame=100)
    pbones_tri["arm_upper_L"].keyframe_insert(data_path="rotation_euler", frame=100)
    pbones_tri["arm_upper_R"].keyframe_insert(data_path="rotation_euler", frame=100)
    pbones_tri["torso"].keyframe_insert(data_path="location", frame=100)
    
    # 3. Theatrical Bow (Frames 110 - 180)
    # Torso pitches forward, arms sweep outward in grand flourish
    pbones_tri["torso"].rotation_euler = (0, 0, math.radians(-35))  # deep bow
    pbones_tri["head"].rotation_euler = (0, 0, math.radians(20))
    pbones_tri["arm_upper_L"].rotation_euler = (0, math.radians(-40), math.radians(-25))
    pbones_tri["arm_upper_R"].rotation_euler = (0, math.radians(40), math.radians(25))
    pbones_tri["torso"].keyframe_insert(data_path="rotation_euler", frame=140)
    pbones_tri["head"].keyframe_insert(data_path="rotation_euler", frame=140)
    pbones_tri["arm_upper_L"].keyframe_insert(data_path="rotation_euler", frame=140)
    pbones_tri["arm_upper_R"].keyframe_insert(data_path="rotation_euler", frame=140)
    
    # Rise back from bow at frame 180
    pbones_tri["torso"].rotation_euler = (0, 0, 0)
    pbones_tri["head"].rotation_euler = (0, 0, 0)
    pbones_tri["arm_upper_L"].rotation_euler = (0, 0, 0)
    pbones_tri["arm_upper_R"].rotation_euler = (0, 0, 0)
    pbones_tri["torso"].keyframe_insert(data_path="rotation_euler", frame=180)
    pbones_tri["head"].keyframe_insert(data_path="rotation_euler", frame=180)
    pbones_tri["arm_upper_L"].keyframe_insert(data_path="rotation_euler", frame=180)
    pbones_tri["arm_upper_R"].keyframe_insert(data_path="rotation_euler", frame=180)
    
    # 4. Pointing & Audacious Mocking (Frames 200 - 300)
    pbones_tri["arm_upper_R"].rotation_euler = (0, math.radians(-50), math.radians(45))
    pbones_tri["arm_lower_R"].rotation_euler = (0, 0, math.radians(30))
    pbones_tri["head"].rotation_euler = (0, 0, math.radians(-12))
    pbones_tri["arm_upper_R"].keyframe_insert(data_path="rotation_euler", frame=230)
    pbones_tri["arm_lower_R"].keyframe_insert(data_path="rotation_euler", frame=230)
    pbones_tri["head"].keyframe_insert(data_path="rotation_euler", frame=230)
    
    # 5. King Francis Gestures & Reaction
    pbones_king = king_rig.pose.bones
    for b in pbones_king:
        b.rotation_mode = 'XYZ'
        
    # King starts regal, arm resting on throne
    pbones_king["arm_upper_R"].rotation_euler = (0, 0, 0)
    pbones_king["arm_upper_R"].keyframe_insert(data_path="rotation_euler", frame=1)
    
    # Frame 130: King leans forward attentively
    pbones_king["torso"].rotation_euler = (0, 0, math.radians(10))
    pbones_king["torso"].keyframe_insert(data_path="rotation_euler", frame=130)
    
    # Frame 210: King raises hand in stern authority
    pbones_king["arm_upper_R"].rotation_euler = (0, math.radians(-65), math.radians(30))
    pbones_king["arm_lower_R"].rotation_euler = (0, math.radians(-20), 0)
    pbones_king["arm_upper_R"].keyframe_insert(data_path="rotation_euler", frame=210)
    pbones_king["arm_lower_R"].keyframe_insert(data_path="rotation_euler", frame=210)
    
    # Frame 280: Amused reaction (head tilts back in laughter)
    pbones_king["head"].rotation_euler = (0, 0, math.radians(-15))
    pbones_king["torso"].rotation_euler = (0, 0, math.radians(-8))
    pbones_king["head"].keyframe_insert(data_path="rotation_euler", frame=280)
    pbones_king["torso"].keyframe_insert(data_path="rotation_euler", frame=280)

def main():
    print("=" * 60)
    print(f"[*] Starting Blender 2D/2.5D Multiplane Pipeline...")
    print(f"[*] Target frames: {total_frames} (Preview: {is_preview})")
    print(f"[*] Output: {output_file}")
    print("=" * 60)
    
    scene = setup_scene()
    print("[+] Scene setup complete.")
    
    create_environment_layers()
    print("[+] Multiplane environment layers assembled.")
    
    setup_lighting()
    print("[+] 3-point cinematic lighting configured.")
    
    tri_rig = build_triboulet_rig()
    print("[+] Triboulet 2D rig constructed & sprite cards mounted.")
    
    king_rig = build_king_francis_rig()
    print("[+] King Francis I rig constructed & mounted on throne dais.")
    
    animate_scene(tri_rig, king_rig)
    print("[+] Walk cycles, gestures, and camera parallax animated.")
    
    # Save the .blend file for inspection & fast re-rendering
    blend_path = os.path.abspath("assets/triboulet_scene.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print(f"[+] Saved Blender project file to: {blend_path}")
    
    # Render animation
    print(f"[*] Rendering {total_frames} frames to {output_file}...")
    bpy.ops.render.render(animation=True)
    print(f"[+] Rendering finished successfully -> {output_file}")

if __name__ == "__main__":
    main()
