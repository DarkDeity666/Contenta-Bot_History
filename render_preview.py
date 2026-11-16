import os
import json
import subprocess
import imageio_ffmpeg
from documentary_engine import render_documentary_frame
from video_engine import generate_ass_subtitles, format_ass_time
from config import VIDEO_WIDTH, VIDEO_HEIGHT, OUTPUT_DIR, MUSIC_DIR

FFMPEG_EXE = imageio_ffmpeg.get_ffmpeg_exe()

preview_dur = 4.5
fps = 30
total_frames = int(preview_dur * fps)
preview_video_path = str(OUTPUT_DIR / "preview_scene_1.mp4")

# Load timestamps from script #5
with open("output/timestamps_5.json", "r", encoding="utf-8") as f:
    all_ts = json.load(f)

preview_ts = [w for w in all_ts if w["start"] < preview_dur]
ass_preview_path = str(OUTPUT_DIR / "preview_subtitles.ass")
generate_ass_subtitles(preview_ts, ass_preview_path, words_per_screen=3)

audio_path = str(OUTPUT_DIR / "voiceover_5.mp3")
ambient_drone = str(MUSIC_DIR / "history_drone.wav")

escaped_ass = ass_preview_path.replace("\\", "/").replace(":", "\\:")
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
    "-r", str(fps),
    "-i", "-",
    "-ss", "00:00:00", "-t", str(preview_dur), "-i", audio_path,
    "-ss", "00:00:00", "-t", str(preview_dur), "-i", ambient_drone,
    "-filter_complex", filtergraph,
    "-map", "[v]",
    "-map", "[aout]",
    "-c:v", "h264_nvenc",
    "-preset", "p4",
    "-cq", "18",
    "-b:v", "7M",
    "-c:a", "aac",
    "-b:a", "192k",
    "-pix_fmt", "yuv420p",
    "-t", str(preview_dur),
    preview_video_path
]

print(f"[*] Rendering {total_frames} frames for preview scene (4.5s)...")
proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)

for f_idx in range(total_frames):
    cur_t = f_idx / fps
    frame = render_documentary_frame(cur_t, 64.0)
    proc.stdin.write(frame.tobytes())

proc.stdin.close()
proc.wait()

print(f"[+] Preview scene successfully rendered: {preview_video_path}")

