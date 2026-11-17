"""
Test armature and sprite plane parenting in Blender 4.2
"""
import bpy
import math

# Clear existing objects
bpy.ops.wm.read_factory_settings(use_empty=True)

# 1. Create Armature
bpy.ops.object.armature_add(enter_editmode=True, align='WORLD', location=(0, 0, 0))
arm_obj = bpy.context.active_object
arm_obj.name = "TestRig"
arm_data = arm_obj.data

# Edit bones
ebones = arm_data.edit_bones
root = ebones[0]
root.name = "root"
root.head = (0, 0, 0)
root.tail = (0, 0, 1.0)

# Torso bone
torso = ebones.new("torso")
torso.head = (0, 0, 1.0)
torso.tail = (0, 0, 2.0)
torso.parent = root

# Arm bone
arm_upper = ebones.new("arm_upper")
arm_upper.head = (0.5, 0, 1.9)
arm_upper.tail = (1.2, 0, 1.5)
arm_upper.parent = torso

bpy.ops.object.mode_set(mode='OBJECT')

# 2. Create Plane
bpy.ops.mesh.primitive_plane_add(size=0.5, enter_editmode=False, location=(0, 0, 0))
plane = bpy.context.active_object
plane.name = "ArmSprite"

# Parent plane to bone
plane.parent = arm_obj
plane.parent_type = 'BONE'
plane.parent_bone = "arm_upper"

# 3. Pose rotation test
bpy.context.view_layer.objects.active = arm_obj
bpy.ops.object.mode_set(mode='POSE')
pbone = arm_obj.pose.bones["arm_upper"]
pbone.rotation_mode = 'XYZ'
pbone.rotation_euler = (0, math.radians(45), 0)

print("[+] Successfully created bone rig and parented sprite plane!")
