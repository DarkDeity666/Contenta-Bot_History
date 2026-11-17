"""
=============================================================================
TEST CHARACTER ASSEMBLY & HIERARCHICAL RIGGING (2D PIVOT SYSTEM)
=============================================================================
Tests hierarchical 2D cutout puppet assembly with exact joint pivots.
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
cam_data.lens = 50
cam_obj = bpy.data.objects.new("Camera", cam_data)
bpy.context.collection.objects.link(cam_obj)
scene.camera = cam_obj
cam_obj.location = (0, -6.5, 0.0)
cam_obj.rotation_euler = (math.radians(90), 0, 0)

# Ambient light
world = bpy.data.worlds.new("W")
scene.world = world
world.use_nodes = True
bg = world.node_tree.nodes.get("Background")
bg.inputs['Color'].default_value = (0.05, 0.05, 0.08, 1.0)
bg.inputs['Strength'].default_value = 1.0

# Key light
light_data = bpy.data.lights.new("Sun", type='SUN')
light_data.energy = 3.0
light_obj = bpy.data.objects.new("Light", light_data)
bpy.context.collection.objects.link(light_obj)
light_obj.rotation_euler = (math.radians(45), math.radians(-20), 0)

def create_sprite_mesh(name, img_path, width, height, pivot=(0.5, 0.5)):
    """
    Creates a quad mesh where vertices are offset so (0,0,0) is at the chosen pivot!
    pivot: (px, py) in 0..1 range.
    (0.5, 0.5) = center
    (0.5, 1.0) = top center (e.g. shoulder or hip joint)
    (0.5, 0.0) = bottom center (e.g. neck)
    """
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
        
    # Build mesh quad in X-Z plane (facing -Y toward camera)
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
    
    # UV mapping
    uv_layer = mesh.uv_layers.new(name="UVMap")
    uvs = [(0, 0), (1, 0), (1, 1), (0, 1)]
    for i, loop in enumerate(mesh.loops):
        uv_layer.data[loop.index].uv = uvs[i % 4]
        
    obj = bpy.data.objects.new(name, mesh)
    obj.data.materials.append(mat)
    bpy.context.collection.objects.link(obj)
    return obj

def assemble_triboulet(root_loc=(-0.5, 0, -1.0)):
    char_dir = os.path.join("assets", "character_rigs", "triboulet")
    
    # Root Empty
    root = bpy.data.objects.new("Triboulet_Root", None)
    root.location = root_loc
    bpy.context.collection.objects.link(root)
    
    # Scale factor
    s = 1.6
    
    # 1. Torso: pivot at bottom center (hips)
    torso = create_sprite_mesh("Tri_Torso", os.path.join(char_dir, "torso.png"),
                               width=0.6*s, height=0.84*s, pivot=(0.5, 0.0))
    torso.parent = root
    torso.location = (0, 0, 0.65*s)
    
    # 2. Head: pivot at bottom center (neck)
    head = create_sprite_mesh("Tri_Head", os.path.join(char_dir, "head_neutral.png"),
                              width=0.55*s, height=0.6*s, pivot=(0.5, 0.1))
    head.parent = torso
    head.location = (0, -0.01, 0.8*s)
    
    # Jester Cap: parented to head
    cap = create_sprite_mesh("Tri_Cap", os.path.join(char_dir, "jester_cap.png"),
                             width=0.96*s, height=0.78*s, pivot=(0.5, 0.2))
    cap.parent = head
    cap.location = (0, -0.02, 0.35*s)
    
    # 3. Left Arm (screen right / character left)
    # Upper Arm: pivot at shoulder (top right of torso)
    arm_up_l = create_sprite_mesh("Tri_ArmUp_L", os.path.join(char_dir, "upper_arm_left.png"),
                                  width=0.24*s, height=0.42*s, pivot=(0.5, 0.9))
    arm_up_l.parent = torso
    arm_up_l.location = (0.28*s, 0.01, 0.72*s)
    
    # Lower Arm: pivot at elbow
    arm_low_l = create_sprite_mesh("Tri_ArmLow_L", os.path.join(char_dir, "lower_arm_left.png"),
                                   width=0.21*s, height=0.39*s, pivot=(0.5, 0.9))
    arm_low_l.parent = arm_up_l
    arm_low_l.location = (0.0, 0.01, -0.38*s)
    
    # Hand L: pivot at wrist
    hand_l = create_sprite_mesh("Tri_Hand_L", os.path.join(char_dir, "hand_open.png"),
                                width=0.27*s, height=0.27*s, pivot=(0.5, 0.85))
    hand_l.parent = arm_low_l
    hand_l.location = (0.0, 0.01, -0.35*s)
    
    # 4. Right Arm (screen left / character right)
    arm_up_r = create_sprite_mesh("Tri_ArmUp_R", os.path.join(char_dir, "upper_arm_right.png"),
                                  width=0.24*s, height=0.42*s, pivot=(0.5, 0.9))
    arm_up_r.parent = torso
    arm_up_r.location = (-0.28*s, -0.01, 0.72*s)
    
    arm_low_r = create_sprite_mesh("Tri_ArmLow_R", os.path.join(char_dir, "lower_arm_right.png"),
                                   width=0.21*s, height=0.39*s, pivot=(0.5, 0.9))
    arm_low_r.parent = arm_up_r
    arm_low_r.location = (0.0, -0.01, -0.38*s)
    
    hand_r = create_sprite_mesh("Tri_Hand_R", os.path.join(char_dir, "hand_point.png"),
                                width=0.27*s, height=0.27*s, pivot=(0.5, 0.85))
    hand_r.parent = arm_low_r
    hand_r.location = (0.0, -0.01, -0.35*s)
    
    # 5. Left Leg: pivot at hip
    leg_up_l = create_sprite_mesh("Tri_LegUp_L", os.path.join(char_dir, "upper_leg_left.png"),
                                  width=0.27*s, height=0.45*s, pivot=(0.5, 0.9))
    leg_up_l.parent = root
    leg_up_l.location = (0.16*s, 0.01, 0.65*s)
    
    leg_low_l = create_sprite_mesh("Tri_LegLow_L", os.path.join(char_dir, "lower_leg_left.png"),
                                   width=0.24*s, height=0.45*s, pivot=(0.5, 0.9))
    leg_low_l.parent = leg_up_l
    leg_low_l.location = (0.0, 0.01, -0.42*s)
    
    foot_l = create_sprite_mesh("Tri_Foot_L", os.path.join(char_dir, "foot_left.png"),
                                width=0.39*s, height=0.27*s, pivot=(0.3, 0.8))
    foot_l.parent = leg_low_l
    foot_l.location = (0.05*s, 0.01, -0.42*s)
    
    # 6. Right Leg
    leg_up_r = create_sprite_mesh("Tri_LegUp_R", os.path.join(char_dir, "upper_leg_right.png"),
                                  width=0.27*s, height=0.45*s, pivot=(0.5, 0.9))
    leg_up_r.parent = root
    leg_up_r.location = (-0.16*s, -0.01, 0.65*s)
    
    leg_low_r = create_sprite_mesh("Tri_LegLow_R", os.path.join(char_dir, "lower_leg_right.png"),
                                   width=0.24*s, height=0.45*s, pivot=(0.5, 0.9))
    leg_low_r.parent = leg_up_r
    leg_low_r.location = (0.0, -0.01, -0.42*s)
    
    foot_r = create_sprite_mesh("Tri_Foot_R", os.path.join(char_dir, "foot_right.png"),
                                width=0.39*s, height=0.27*s, pivot=(0.7, 0.8))
    foot_r.parent = leg_low_r
    foot_r.location = (-0.05*s, -0.01, -0.42*s)
    
    return root

assemble_triboulet()

# Render test frame
scene.render.filepath = os.path.abspath("output/triboulet_test_frame.png")
bpy.ops.render.render(write_still=True)
print("[+] Test frame rendered to output/triboulet_test_frame.png")
