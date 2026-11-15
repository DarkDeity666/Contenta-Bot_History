import os
import json
import subprocess
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
import imageio_ffmpeg

from config import (
    OUTPUT_DIR, ASSETS_DIR, MUSIC_DIR, SFX_DIR,
    VIDEO_WIDTH, VIDEO_HEIGHT, FPS, USE_NVENC, FFMPEG_THREADS
)
from database import get_connection, save_video_record
from stickman_cinematic_engine import render_master_stickman_frame
from sound_generator import generate_all_audio_assets

FFMPEG_EXE = imageio_ffmpeg.get_ffmpeg_exe()
RENDER_FPS = 30  # 30fps is butter-smooth for 2D stickman animation and renders 2x faster

def format_ass_time(seconds: float) -> str:
    """Converts seconds into ASS subtitle timestamp format: H:MM:SS.cs"""
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    centis = int(round((seconds - int(seconds)) * 100))
    if centis >= 100:
        secs += 1
        centis = 0
    return f"{hrs}:{mins:02d}:{secs:02d}.{centis:02d}"

def generate_ass_subtitles(timestamps: List[Dict[str, Any]], ass_path: str, words_per_screen: int = 3):
    """
    Creates dynamic kinetic subtitles positioned in the upper-safe area
    so they never block the live animated stickman action on the floor!
    """
    # MarginV=1450 positions captions in the upper-middle area
    header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {VIDEO_WIDTH}
PlayResY: {VIDEO_HEIGHT}
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Impact,72,&H00FFFFFF,&H0000FFFF,&H00101010,&HB0000000,-1,0,0,0,100,100,1,0,1,7,4,2,60,60,1480,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    events = []
    i = 0
    while i < len(timestamps):
        chunk = timestamps[i:i + words_per_screen]
        for active_idx, active_word in enumerate(chunk):
            w_start = active_word["start"]
            w_end = active_word["end"]
            
            line_parts = []
            for j, w in enumerate(chunk):
                word_text = w["word"].upper()
                if j == active_idx:
                    # Gold highlight with vivid emphasis
                    line_parts.append(f"{{\\c&H002BD4FF&}}{word_text}{{\\c&H00FFFFFF&}}")
                else:
                    line_parts.append(word_text)
                    
            dialogue_text = " ".join(line_parts)
            events.append(f"Dialogue: 0,{format_ass_time(w_start)},{format_ass_time(w_end)},Default,,0,0,0,,{dialogue_text}")
            
        i += words_per_screen

    with open(ass_path, "w", encoding="utf-8") as f:
        f.write(header + "\n".join(events))
        
    print(f"[+] Kinetic ASS subtitles generated at: {ass_path}")

def render_history_short(script_id: int) -> str:
    """
    Renders a 100% LIVE 2D ANIMATED STICKMAN Short:
    - Articulated moving characters (walking, running, panicking, talking, sword fighting, gavel slamming)
    - 4 distinct animated story scenes (Hook, Incident, Courtroom Chaos, Climax)
    - Live frame-by-frame rendering piped directly into NVENC on RTX 3060
    - Pure 100% original graphics (zero copyright, zero static photos)
    - Brian human storytelling voice + ambient audio ducking
    """
    generate_all_audio_assets()
    
    audio_path = str(OUTPUT_DIR / f"voiceover_{script_id}.mp3")
    timestamps_path = str(OUTPUT_DIR / f"timestamps_{script_id}.json")
    ass_path = str(OUTPUT_DIR / f"subtitles_{script_id}.ass")
    output_video_path = str(OUTPUT_DIR / f"history_short_{script_id}.mp4")
    
    if not os.path.exists(audio_path) or not os.path.exists(timestamps_path):
        raise FileNotFoundError(f"Audio or timestamps missing for script #{script_id}")

    # Fetch topic title
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT t.title FROM topics t 
        JOIN scripts s ON s.topic_id = t.id 
        WHERE s.id = ?
    """, (script_id,))
    row = cursor.fetchone()
    conn.close()
    
    topic_title = row["title"] if row else "Historical Anomaly"

    with open(timestamps_path, "r", encoding="utf-8") as f:
        timestamps = json.load(f)

    duration = timestamps[-1]["end"] + 0.8
    total_frames = int(duration * RENDER_FPS)
    
    generate_ass_subtitles(timestamps, ass_path, words_per_screen=3)
    
    print(f"[*] Rendering LIVE 2D STICKMAN ANIMATION ({total_frames} frames, {duration:.2f}s) via RTX 3060 NVENC...")
    start_render = time.time()
    
    escaped_ass = ass_path.replace("\\", "/").replace(":", "\\:")
    ambient_drone = str(MUSIC_DIR / "history_drone.wav")

    vcodec = "h264_nvenc" if USE_NVENC else "libx264"
    preset = "p4" if USE_NVENC else "veryfast"

    filtergraph = (
        f"[0:v]subtitles='{escaped_ass}' [v]; "
        f"[1:a]volume=1.0[vocal]; [2:a]volume=0.15[drone]; [vocal][drone]amix=inputs=2:duration=first[aout]"
    )

    cmd = [
        FFMPEG_EXE, "-y",
        "-f", "rawvideo",
        "-vcodec", "rawvideo",
        "-s", f"{VIDEO_WIDTH}x{VIDEO_HEIGHT}",
        "-pix_fmt", "rgb24",
        "-r", str(RENDER_FPS),
        "-i", "-",  # Video frames piped via stdin
        "-i", audio_path,
        "-i", ambient_drone,
        "-filter_complex", filtergraph,
        "-map", "[v]",
        "-map", "[aout]",
        "-c:v", vcodec,
        "-preset", preset,
        "-cq", "20",
        "-b:v", "7M",
        "-c:a", "aac",
        "-b:a", "192k",
        "-pix_fmt", "yuv420p",
        "-threads", str(FFMPEG_THREADS),
        "-t", str(duration),
        output_video_path
    ]

    log_file = open(OUTPUT_DIR / "ffmpeg_render.log", "w")
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=log_file)

    # Frame generation loop: renders animated stickman frames and streams to FFmpeg
    try:
        for f_idx in range(total_frames):
            cur_t = f_idx / RENDER_FPS
            frame_img = render_master_stickman_frame(cur_t, duration, topic_title)
            proc.stdin.write(frame_img.tobytes())

            if f_idx % 150 == 0:
                pct = int((f_idx / total_frames) * 100)
                print(f"    Animation progress: {pct}% ({f_idx}/{total_frames} frames)")

        proc.stdin.close()
        proc.wait()
        log_file.close()
    except Exception as e:
        proc.kill()
        log_file.close()
        raise e

    if proc.returncode != 0:
        with open(OUTPUT_DIR / "ffmpeg_render.log", "r", encoding="utf-8", errors="ignore") as lf:
            err = lf.read()
        print(f"[!] Primary NVENC render error: {err[-400:]}")
        raise RuntimeError(f"FFmpeg render failed with code {proc.returncode}")

    render_time = time.time() - start_render
    fps_achieved = total_frames / render_time if render_time > 0 else 0
    print(f"[+] LIVE 2D ANIMATED Stickman Short #{script_id} successfully rendered!")
    print(f"    Saved: {output_video_path}")
    print(f"    Speed: {fps_achieved:.1f} FPS (Rendered in {render_time:.2f}s on RTX 3060)")
    
    save_video_record(script_id, output_video_path, audio_path, duration)
    return output_video_path

if __name__ == "__main__":
    render_history_short(1)
