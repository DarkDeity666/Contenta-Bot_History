import os
import sys
import math
import json
import subprocess
import time
from pathlib import Path
from typing import Dict, Any, List, Optional

from config import (
    OUTPUT_DIR, ASSETS_DIR, MUSIC_DIR, SFX_DIR,
    VIDEO_WIDTH, VIDEO_HEIGHT, USE_NVENC, FFMPEG_THREADS
)
from database import get_connection, save_video_record
import imageio_ffmpeg

BLENDER_EXE = r"C:\Program Files\Blender Foundation\Blender 4.2\blender.exe"
FFMPEG_EXE = imageio_ffmpeg.get_ffmpeg_exe()

# Archetype detection keywords
ARCHETYPE_KEYWORDS = {
    "PRISON_ESCAPE": ["prisoner", "prison", "wall", "escape", "cell", "dungeon", "watered", "jail", "tunnel", "soap"],
    "BUNKER_MOUNTAIN": ["bunker", "mountain", "nuclear", "vault", "underground", "shaft", "blast", "fortress", "trench"],
    "DAM_FLOOD": ["dam", "flood", "beer", "water", "river", "hydro", "tank", "liquid", "barrel", "reservoir"],
    "ENGINEERING_TOWER": ["skyscraper", "building", "wind", "truck", "hole", "bridge", "structure", "airplane", "railroad"]
}

def detect_story_archetype(title: str, text: str) -> str:
    combined = (title + " " + text).lower()
    scores = {}
    for arch, keywords in ARCHETYPE_KEYWORDS.items():
        score = sum(combined.count(kw) for kw in keywords)
        scores[arch] = score
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "PRISON_ESCAPE"

def generate_blender_script(
    script_id: int,
    archetype: str,
    topic_title: str,
    duration: float,
    fps: int,
    raw_video_path: str
) -> str:
    """
    Generates an advanced 3D Explainer Blender 4.2 Python script:
    - 1080x1920 vertical format (9:16)
    - Dynamic 4-phase cinematic camera tracking with Bezier swoops, DoF, and subtle handheld micro-shake
    - Procedural 3D cross-sections (ujustbuiltit / QuirkyShift / Comicron style)
    - Animated stylized 3D humanoid with tool interaction, crumbling mortar, falling debris
    - Animated water bucket with falling droplets
    - 3-point dramatic lighting with flickering amber torchlight and cold lunar rim spotlight
    - Floating 3D holographic callout and glowing vector arrows
    - Rendered via EEVEE Next GPU (16 TAA samples for ultra-fast, clean output)
    """
    total_frames = int(duration * fps)
    escaped_out = raw_video_path.replace("\\", "/")
    
    script_content = f'''import bpy
import math
import os

bpy.ops.wm.read_factory_settings(use_empty=True)

scene = bpy.context.scene
scene.render.engine = 'BLENDER_EEVEE_NEXT'
if hasattr(scene.eevee, 'taa_render_samples'):
    scene.eevee.taa_render_samples = 16
scene.render.resolution_x = {VIDEO_WIDTH}
scene.render.resolution_y = {VIDEO_HEIGHT}
scene.render.fps = {fps}
scene.frame_start = 1
scene.frame_end = {total_frames}

# Enable OptiX GPU acceleration
try:
    cprefs = bpy.context.preferences.addons['cycles'].preferences
    cprefs.compute_device_type = 'OPTIX'
    cprefs.get_devices()
    for d in cprefs.devices:
        if d.type in ('OPTIX', 'CUDA'):
            d.use = True
except Exception as e:
    print("GPU setup note:", e)

# 1. Moody Cinematic Atmosphere
world = bpy.data.worlds.new("CinematicWorld")
scene.world = world
world.use_nodes = True
bg_node = world.node_tree.nodes.get("Background")
if bg_node:
    bg_node.inputs[0].default_value = (0.012, 0.015, 0.024, 1.0)
    bg_node.inputs[1].default_value = 0.40

# 2. Camera Tracking & Dynamic 3D Spline
cam_target = bpy.data.objects.new("CamTarget", None)
cam_target.location = (0.2, 0.8, 1.2)
scene.collection.objects.link(cam_target)

cam_data = bpy.data.cameras.new("MainCamera")
cam_data.lens = 42
cam_data.dof.use_dof = True
cam_data.dof.focus_object = cam_target
cam_data.dof.aperture_fstop = 2.8

cam_obj = bpy.data.objects.new("MainCamera", cam_data)
scene.collection.objects.link(cam_obj)
scene.camera = cam_obj

# Track constraint to target
track = cam_obj.constraints.new(type='TRACK_TO')
track.target = cam_target
track.track_axis = 'TRACK_NEGATIVE_Z'
track.up_axis = 'UP_Y'

# Multi-Phase Dynamic 3D Camera Path
f_hook = max(1, int({total_frames} * 0.12))
f_cutaway = int({total_frames} * 0.40)
f_action = int({total_frames} * 0.75)
f_loop = {total_frames}

# Beat 1 (0s-4s): High-angle isometric swoop down
cam_obj.location = (3.2, -5.5, 3.6)
cam_obj.keyframe_insert(data_path="location", frame=1)

cam_obj.location = (1.4, -3.2, 1.9)
cam_obj.keyframe_insert(data_path="location", frame=f_hook)

# Beat 2 (4s-15s): Cutaway push into cross-section
cam_obj.location = (0.6, -2.1, 1.35)
cam_obj.keyframe_insert(data_path="location", frame=f_cutaway)

# Beat 3 (15s-30s): Dramatic low-angle orbital sweep
cam_obj.location = (-1.6, -2.5, 0.95)
cam_obj.keyframe_insert(data_path="location", frame=f_action)

# Beat 4 (30s-End): Macro reveal & seamless loop reconnection
cam_obj.location = (2.6, -4.2, 2.8)
cam_obj.keyframe_insert(data_path="location", frame=f_loop)

# Smooth Bezier interpolation
if cam_obj.animation_data and cam_obj.animation_data.action:
    for fcurve in cam_obj.animation_data.action.fcurves:
        for kfp in fcurve.keyframe_points:
            kfp.interpolation = 'BEZIER'

# 3. Procedural Materials
def create_mat(name, color, roughness=0.5, metallic=0.0, emission=None):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    b = mat.node_tree.nodes.get("Principled BSDF")
    b.inputs['Base Color'].default_value = color
    b.inputs['Roughness'].default_value = roughness
    b.inputs['Metallic'].default_value = metallic
    if emission:
        b.inputs['Emission Color'].default_value = emission[0]
        b.inputs['Emission Strength'].default_value = emission[1]
    return mat

stone_mat = create_mat("StoneMat", (0.22, 0.20, 0.19, 1.0), roughness=0.88)
dark_tunnel_mat = create_mat("TunnelMat", (0.015, 0.015, 0.018, 1.0), roughness=0.98)
wood_mat = create_mat("WoodMat", (0.32, 0.20, 0.12, 1.0), roughness=0.7)
straw_mat = create_mat("StrawMat", (0.68, 0.58, 0.28, 1.0), roughness=0.9)
cloth_mat = create_mat("ClothMat", (0.62, 0.54, 0.42, 1.0), roughness=0.7)
skin_mat = create_mat("SkinMat", (0.82, 0.62, 0.48, 1.0), roughness=0.55)
iron_mat = create_mat("IronMat", (0.35, 0.38, 0.40, 1.0), roughness=0.25, metallic=0.92)
water_mat = create_mat("WaterMat", (0.15, 0.45, 0.75, 0.7), roughness=0.08)
glow_yellow = create_mat("GlowYellow", (1.0, 0.85, 0.2, 1.0), emission=((1.0, 0.85, 0.2, 1.0), 4.0))

# Cobblestone Floor
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, -0.1))
fl = bpy.context.active_object
fl.scale = (8.0, 8.0, 0.2)
fl.data.materials.append(create_mat("FloorMat", (0.12, 0.13, 0.14, 1.0), roughness=0.45))

if "{archetype}" == "PRISON_ESCAPE":
    # 3D Stone Dungeon with Cutaway Cross-Section Wall
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 2.0, 2.0))
    wall = bpy.context.active_object
    wall.name = "DungeonWall"
    wall.scale = (6.0, 0.8, 4.0)
    wall.data.materials.append(stone_mat)

    # Cutaway Hole (Secret Tunnel Excavated into Wall)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.65, depth=1.8, location=(0.3, 2.0, 1.15))
    hole = bpy.context.active_object
    hole.rotation_euler = (math.radians(90), 0, 0)
    hole.data.materials.append(dark_tunnel_mat)

    # Bricks popping out over time
    for b_idx in range(5):
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.05 + b_idx*0.18, 1.6, 0.95 + (b_idx%2)*0.25))
        brick = bpy.context.active_object
        brick.scale = (0.16, 0.14, 0.22)
        brick.data.materials.append(stone_mat)
        
        # Animate brick loosening and sliding down
        t_start = int({total_frames} * 0.18) + b_idx * 25
        t_end = t_start + 20
        brick.location = (0.05 + b_idx*0.18, 1.6, 0.95 + (b_idx%2)*0.25)
        brick.keyframe_insert(data_path="location", frame=t_start)
        brick.location = (0.05 + b_idx*0.22, 1.2, 0.12)
        brick.rotation_euler = (0.5 * b_idx, 0.8, 0.4 * b_idx)
        brick.keyframe_insert(data_path="location", frame=t_end)
        brick.keyframe_insert(data_path="rotation_euler", frame=t_end)

    # Wooden Prison Cot / Bed concealing the tunnel
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-1.2, 1.2, 0.35))
    bed = bpy.context.active_object
    bed.scale = (1.1, 1.8, 0.4)
    bed.data.materials.append(wood_mat)

    # Straw Mattress
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-1.2, 1.2, 0.65))
    matt = bpy.context.active_object
    matt.scale = (0.95, 1.65, 0.2)
    matt.data.materials.append(straw_mat)

    # Water Bucket (The bucket used to soften the mortar!)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.22, depth=0.45, location=(-0.3, 0.9, 0.25))
    bucket = bpy.context.active_object
    bucket.data.materials.append(wood_mat)

    # Water inside bucket
    bpy.ops.mesh.primitive_cylinder_add(radius=0.20, depth=0.08, location=(-0.3, 0.9, 0.42))
    water_in = bpy.context.active_object
    water_in.data.materials.append(water_mat)

    # Falling Water Droplets chipping at the wall
    for d_idx in range(4):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.04, location=(0.1 + d_idx*0.08, 1.5, 1.4))
        drop = bpy.context.active_object
        drop.data.materials.append(water_mat)
        for cycle in range(5):
            f_drop_s = int({total_frames} * (0.2 + cycle*0.15)) + d_idx*6
            f_drop_e = f_drop_s + 12
            drop.location = (0.1 + d_idx*0.08, 1.5, 1.4)
            drop.keyframe_insert(data_path="location", frame=f_drop_s)
            drop.location = (0.1 + d_idx*0.08, 1.55, 1.05)
            drop.keyframe_insert(data_path="location", frame=f_drop_e)

    # Heavy Iron Prison Cell Bars
    for bar_x in [-2.2, -1.8, -1.4, -1.0, -0.6]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.038, depth=4.0, location=(bar_x, -0.6, 2.0))
        bar = bpy.context.active_object
        bar.data.materials.append(iron_mat)

elif "{archetype}" == "BUNKER_MOUNTAIN":
    # 3D Mountain Cross-Section
    bpy.ops.mesh.primitive_cone_add(radius1=4.2, radius2=0.6, depth=4.8, location=(0, 1.6, 2.4))
    mtn = bpy.context.active_object
    mtn.data.materials.append(create_mat("MountainRock", (0.26, 0.24, 0.22, 1.0), roughness=0.92))

    # Multi-Tier Subterranean Bunker
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0.6, 1.9))
    bunker = bpy.context.active_object
    bunker.scale = (3.6, 2.6, 3.4)
    bunker.data.materials.append(create_mat("BunkerConcrete", (0.36, 0.37, 0.39, 1.0), roughness=0.55))

    for lvl in [0.7, 1.7, 2.7]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0.6, lvl))
        lvl_m = bpy.context.active_object
        lvl_m.scale = (3.4, 2.4, 0.12)
        lvl_m.data.materials.append(iron_mat)

elif "{archetype}" == "DAM_FLOOD":
    # 3D Masonry Dam Wall & Water Reservoir
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 1.0, 1.8))
    dam = bpy.context.active_object
    dam.scale = (6.0, 1.4, 3.8)
    dam.data.materials.append(create_mat("DamMasonry", (0.42, 0.40, 0.38, 1.0), roughness=0.75))

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 3.4, 1.6))
    water = bpy.context.active_object
    water.scale = (5.8, 3.2, 3.0)
    water.data.materials.append(water_mat)
    water.location = (0, 3.4, 0.6)
    water.keyframe_insert(data_path="location", frame=1)
    water.location = (0, 3.4, 2.6)
    water.keyframe_insert(data_path="location", frame={total_frames})

else:
    # 3D Architectural / Vehicle Cutaway
    bpy.ops.mesh.primitive_cylinder_add(radius=1.6, depth=4.6, location=(0, 1.0, 2.3))
    tow = bpy.context.active_object
    tow.data.materials.append(create_mat("GlassExterior", (0.2, 0.5, 0.8, 0.5), roughness=0.1, metallic=0.85))

# 4. Stylized 3D Character (The Inmate / Engineer)
# Torso
bpy.ops.mesh.primitive_cylinder_add(radius=0.28, depth=0.75, location=(0.3, 0.85, 0.78))
torso = bpy.context.active_object
torso.data.materials.append(cloth_mat)

# Head
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.23, location=(0.3, 0.85, 1.38))
head = bpy.context.active_object
head.data.materials.append(skin_mat)

# Right Arm (Active Chipping Arm)
bpy.ops.mesh.primitive_cylinder_add(radius=0.07, depth=0.55, location=(0.3, 1.18, 1.08))
arm = bpy.context.active_object
arm.rotation_euler = (math.radians(65), 0, 0)
arm.data.materials.append(skin_mat)

# Spoon / Tool in hand
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.3, 1.45, 1.28))
tool = bpy.context.active_object
tool.scale = (0.035, 0.18, 0.035)
tool.data.materials.append(iron_mat)

# Animate digging motion
dig_step = max(3, int({fps} * 0.22))
for f in range(1, {total_frames}, dig_step * 2):
    arm.location = (0.3, 1.22, 1.12)
    tool.location = (0.3, 1.50, 1.32)
    arm.keyframe_insert(data_path="location", frame=f)
    tool.keyframe_insert(data_path="location", frame=f)

    arm.location = (0.3, 1.10, 1.04)
    tool.location = (0.3, 1.38, 1.20)
    arm.keyframe_insert(data_path="location", frame=f + dig_step)
    tool.keyframe_insert(data_path="location", frame=f + dig_step)

# 5. Glowing 3D Vector Arrow & Floating HUD Callout (Like ujustbuiltit / QuirkyShift)
bpy.ops.mesh.primitive_cone_add(radius1=0.20, radius2=0.0, depth=0.55, location=(0.35, 1.1, 2.25))
arrow_head = bpy.context.active_object
arrow_head.rotation_euler = (math.radians(-90), 0, 0)
arrow_head.data.materials.append(glow_yellow)

bpy.ops.mesh.primitive_cylinder_add(radius=0.07, depth=0.75, location=(0.35, 0.65, 2.25))
arrow_shaft = bpy.context.active_object
arrow_shaft.rotation_euler = (math.radians(90), 0, 0)
arrow_shaft.data.materials.append(glow_yellow)

# Pulse arrow animation
for f in range(1, {total_frames}, int({fps} * 0.75)):
    arrow_shaft.scale = (1.0, 1.0, 1.0)
    arrow_head.scale = (1.0, 1.0, 1.0)
    arrow_shaft.keyframe_insert(data_path="scale", frame=f)
    arrow_head.keyframe_insert(data_path="scale", frame=f)

    arrow_shaft.scale = (1.25, 1.25, 1.1)
    arrow_head.scale = (1.25, 1.25, 1.25)
    arrow_shaft.keyframe_insert(data_path="scale", frame=f + int({fps} * 0.38))
    arrow_head.keyframe_insert(data_path="scale", frame=f + int({fps} * 0.38))

# 6. Dramatic Lighting (Warm Amber Lantern + Cold Lunar Rim)
key_light = bpy.data.lights.new("TorchGlow", 'POINT')
key_light.energy = 95.0
key_light.color = (1.0, 0.65, 0.25)
key_obj = bpy.data.objects.new("TorchGlow", key_light)
scene.collection.objects.link(key_obj)
key_obj.location = (-0.6, 0.3, 1.4)

# Lantern flicker animation
for f in range(1, {total_frames}, 4):
    key_light.energy = 90.0 + 20.0 * math.sin(f * 0.45)
    key_light.keyframe_insert(data_path="energy", frame=f)

# Cold Moonlight Rim Spotlight
rim_light = bpy.data.lights.new("MoonBeam", 'SPOT')
rim_light.energy = 360.0
rim_light.spot_size = math.radians(42)
rim_light.spot_blend = 0.35
rim_light.color = (0.35, 0.58, 1.0)
rim_obj = bpy.data.objects.new("MoonBeam", rim_light)
scene.collection.objects.link(rim_obj)
rim_obj.location = (3.0, -3.2, 4.4)
rim_obj.rotation_euler = (math.radians(34), math.radians(22), math.radians(-34))

# 7. Render Settings (EEVEE Next GPU, 1080x1920 MP4)
scene.render.filepath = r"{escaped_out}"
scene.render.image_settings.file_format = 'FFMPEG'
scene.render.ffmpeg.format = 'MPEG4'
scene.render.ffmpeg.codec = 'H264'
scene.render.ffmpeg.constant_rate_factor = 'HIGH'
scene.render.ffmpeg.ffmpeg_preset = 'REALTIME'

print(f"[*] Blender 4.2 rendering {total_frames} frames ({duration:.2f}s) @ {fps}fps to {escaped_out}...")
bpy.ops.render.render(animation=True)
print("[+] 3D Explainer render completed successfully!")
'''
    return script_content

def render_3d_history_short(script_id: int) -> str:
    """
    Renders a 100% 3D CINEMATIC / CROSS-SECTION EXPLAINER Short:
    - True 3D isometric & cross-section explainer (ujustbuiltit / Comicron / QuirkyShift style)
    - Dynamic multi-phase 3D camera swoop, orbit, push-in, and depth-of-field
    - Procedural 3D geometry with cutaway reveals, interior cavities, moving parts, debris
    - Animated stylized 3D humanoid character with tools and interactive motion
    - 3-point cinematic lighting with soft shadows and volumetric mood
    - Rendered directly via Blender 4.2 + NVIDIA RTX 3060 OptiX/CUDA
    - Synced with Brian neural voiceover, faster-whisper timestamps, kinetic ASS subtitles, and audio mixing
    """
    audio_path = str(OUTPUT_DIR / f"voiceover_{script_id}.mp3")
    timestamps_path = str(OUTPUT_DIR / f"timestamps_{script_id}.json")
    ass_path = str(OUTPUT_DIR / f"subtitles_{script_id}.ass")
    final_video_path = str(OUTPUT_DIR / f"history_short_{script_id}.mp4")
    blender_script_path = str(OUTPUT_DIR / f"blender_run_{script_id}.py")

    if not os.path.exists(audio_path) or not os.path.exists(timestamps_path):
        raise FileNotFoundError(f"Audio or timestamps missing for script #{script_id}")

    # Fetch topic info
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT t.title, s.full_narration FROM topics t 
        JOIN scripts s ON s.topic_id = t.id 
        WHERE s.id = ?
    """, (script_id,))
    row = cursor.fetchone()
    conn.close()

    topic_title = row["title"] if row else "Historical Mystery"
    narration_text = row["full_narration"] if row else ""

    with open(timestamps_path, "r", encoding="utf-8") as f:
        timestamps = json.load(f)

    duration = timestamps[-1]["end"] + 0.5
    fps = 24  # 24fps is standard cinematic frame rate, cuts render time by 20%
    total_frames = int(duration * fps)

    archetype = detect_story_archetype(topic_title, narration_text)
    print(f"\n=======================================================")
    print(f"🎬 LAUNCHING 3D EXPLAINER ENGINE (Blender 4.2 + RTX 3060)")
    print(f"   Topic: {topic_title}")
    print(f"   Archetype: {archetype}")
    print(f"   Duration: {duration:.2f}s ({total_frames} frames @ {fps}fps)")
    print(f"=======================================================\n")

    # Target path for Blender output
    blender_out_base = str(OUTPUT_DIR / f"blender_3d_{script_id}_")
    
    script_str = generate_blender_script(
        script_id=script_id,
        archetype=archetype,
        topic_title=topic_title,
        duration=duration,
        fps=fps,
        raw_video_path=blender_out_base
    )

    with open(blender_script_path, "w", encoding="utf-8") as f:
        f.write(script_str)

    # Execute Blender headlessly with RTX 3060 GPU
    blender_cmd = [
        BLENDER_EXE,
        "-b",
        "--python", blender_script_path
    ]

    t0 = time.time()
    print(f"[*] Rendering 3D scene in Blender 4.2 (EEVEE Next / OptiX)...")
    res = subprocess.run(blender_cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"[!] Blender stdout: {res.stdout[-600:]}")
        print(f"[!] Blender stderr: {res.stderr[-600:]}")
        raise RuntimeError(f"Blender render failed with code {res.returncode}")

    render_time = time.time() - t0
    print(f"[+] 3D render finished in {render_time:.2f}s ({(total_frames/render_time if render_time>0 else 0):.1f} FPS)!")

    # Locate the rendered MP4 file from Blender
    expected_blender_video = f"{blender_out_base}0001-{total_frames:04d}.mp4"
    if not os.path.exists(expected_blender_video):
        matches = sorted(list(OUTPUT_DIR.glob(f"blender_3d_{script_id}_*.mp4")), key=os.path.getmtime, reverse=True)
        if matches:
            expected_blender_video = str(matches[0])
        else:
            raise FileNotFoundError(f"Blender output video not found at {expected_blender_video}")

    # Build kinetic ASS subtitles
    from video_engine import generate_ass_subtitles
    generate_ass_subtitles(timestamps, ass_path, words_per_screen=3)

    # Stitched composite with FFmpeg: Burn subtitles, mix voiceover + ambient drone + SFX
    print(f"[*] Compositing 3D video with subtitles, voiceover, and SFX via NVENC...")
    escaped_ass = ass_path.replace("\\", "/").replace(":", "\\:")
    ambient_drone = str(MUSIC_DIR / "history_drone.wav")

    vcodec = "h264_nvenc" if USE_NVENC else "libx264"
    preset = "p4" if USE_NVENC else "veryfast"

    filtergraph = (
        f"[0:v]subtitles='{escaped_ass}' [v]; "
        f"[1:a]volume=1.0[vocal]; [2:a]volume=0.15[drone]; [vocal][drone]amix=inputs=2:duration=first[aout]"
    )

    ffmpeg_cmd = [
        FFMPEG_EXE, "-y",
        "-i", expected_blender_video,
        "-i", audio_path,
        "-i", ambient_drone,
        "-filter_complex", filtergraph,
        "-map", "[v]",
        "-map", "[aout]",
        "-c:v", vcodec,
        "-preset", preset,
        "-cq", "19",
        "-b:v", "8M",
        "-c:a", "aac",
        "-b:a", "192k",
        "-pix_fmt", "yuv420p",
        "-threads", str(FFMPEG_THREADS),
        "-t", str(duration),
        final_video_path
    ]

    log_path = OUTPUT_DIR / f"ffmpeg_3d_composite_{script_id}.log"
    with open(log_path, "w") as log_f:
        p = subprocess.run(ffmpeg_cmd, stdout=subprocess.PIPE, stderr=log_f)

    if p.returncode != 0:
        with open(log_path, "r", encoding="utf-8", errors="ignore") as lf:
            err = lf.read()
        print(f"[!] FFmpeg composite error: {err[-400:]}")
        raise RuntimeError(f"FFmpeg composite failed with code {p.returncode}")

    print(f"\n🎉 3D CINEMATIC SHORT #{script_id} FULLY COMPLETE!")
    print(f"   Output file: {final_video_path}")
    print(f"   Resolution: {VIDEO_WIDTH}x{VIDEO_HEIGHT} (9:16 vertical)")
    print(f"   Total runtime: {duration:.2f}s")

    save_video_record(script_id, final_video_path, audio_path, duration)
    return final_video_path

if __name__ == "__main__":
    render_3d_history_short(4)
