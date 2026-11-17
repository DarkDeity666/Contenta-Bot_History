"""
=============================================================================
SUBTITLE GENERATOR - KINETIC ASS FORMAT FOR YOUTUBE SHORTS
=============================================================================
Converts Faster-Whisper word-level JSON into high-impact, mobile-optimized
ASS subtitles with bold typography, solid outlines, and safe-zone positioning.
=============================================================================
"""

import json
import os

INPUT_JSON = os.path.join("output", "subtitles_triboulet.json")
OUTPUT_ASS = os.path.join("output", "subtitles_triboulet.ass")

def format_ass_time(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = seconds % 60
    centis = int((secs - int(secs)) * 100)
    return f"{hours}:{minutes:02d}:{int(secs):02d}.{centis:02d}"

def generate_ass_subtitles():
    with open(INPUT_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    words = data.get("words", [])
    if not words:
        # Fallback to sentences if words missing
        words = []
        for s in data.get("sentences", []):
            parts = s["text"].split()
            dur = s["end"] - s["start"]
            step = dur / max(len(parts), 1)
            for idx, p in enumerate(parts):
                words.append({
                    "start": s["start"] + idx * step,
                    "end": s["start"] + (idx + 1) * step,
                    "word": p
                })
                
    ass_header = """[Script Info]
Title: Triboulet Animated Short
ScriptType: v4.00+
WrapStyle: 0
ScaledBorderAndShadow: yes
YCbCr Matrix: TV.709
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: ShortsDefault,Arial,56,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,5,2,2,40,40,380,1
Style: ShortsPunchline,Arial,64,&H0045D4FF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,6,3,2,40,40,380,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    events = []
    
    # Group words into 2-3 word chunks
    chunk_size = 2
    i = 0
    while i < len(words):
        chunk = words[i:i + chunk_size]
        t_start = chunk[0]["start"]
        t_end = chunk[-1]["end"]
        # Ensure minimum visible duration of 0.35s
        if t_end - t_start < 0.35:
            t_end = t_start + 0.35
            
        text = " ".join(w["word"] for w in chunk).strip()
        
        # Clean up punctuation formatting
        text_clean = text.replace('"', '').replace("'", "’")
        
        # Highlight punchline moments with bright gold/yellow style
        is_highlight = any(k in text_clean.lower() for k in ["slapped", "queen", "treason", "old age", "punchline", "gallows", "king"])
        style = "ShortsPunchline" if is_highlight else "ShortsDefault"
        
        start_str = format_ass_time(t_start)
        end_str = format_ass_time(t_end)
        
        events.append(f"Dialogue: 0,{start_str},{end_str},{style},,0,0,0,,{text_clean}")
        i += chunk_size
        
    with open(OUTPUT_ASS, "w", encoding="utf-8") as f:
        f.write(ass_header + "\n".join(events) + "\n")
        
    print(f"[+] Kinetic ASS subtitles generated -> {OUTPUT_ASS} ({len(events)} cues)")
    return OUTPUT_ASS

if __name__ == "__main__":
    generate_ass_subtitles()
