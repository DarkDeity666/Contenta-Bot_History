import asyncio
import os
import json
from pathlib import Path
from typing import Dict, Any, List
import edge_tts
from config import OUTPUT_DIR, DEFAULT_VOICE, VOICE_RATE, VOICE_PITCH, WHISPER_DEVICE, WHISPER_COMPUTE_TYPE
from database import get_connection

async def synthesize_speech_edge(
    text: str, 
    output_path: str, 
    voice: str = DEFAULT_VOICE, 
    rate: str = VOICE_RATE, 
    pitch: str = VOICE_PITCH
) -> str:
    """Generates hyper-realistic human storytelling narration using Microsoft Neural Voices."""
    communicate = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
    await communicate.save(output_path)
    return output_path

def generate_voiceover(text: str, script_id: int) -> str:
    """Wrapper to run async speech generation synchronously."""
    audio_filename = f"voiceover_{script_id}.mp3"
    audio_path = str(OUTPUT_DIR / audio_filename)
    print(f"[*] Synthesizing human storytelling voice for script #{script_id} using {DEFAULT_VOICE} ({VOICE_RATE}, {VOICE_PITCH})...")
    asyncio.run(synthesize_speech_edge(text, audio_path))
    print(f"[+] Audio generated at: {audio_path}")
    return audio_path

def transcribe_with_word_timestamps(audio_path: str) -> List[Dict[str, Any]]:
    """Runs Whisper to extract precise word-level timestamps for kinetic video subtitles."""
    print(f"[*] Extracting word-level timestamps with Whisper (device: {WHISPER_DEVICE})...")
    from faster_whisper import WhisperModel
    
    words_data = []
    try:
        model = WhisperModel("tiny", device=WHISPER_DEVICE, compute_type=WHISPER_COMPUTE_TYPE)
        segments, info = model.transcribe(audio_path, word_timestamps=True)
        for segment in segments:
            for word in segment.words:
                words_data.append({
                    "word": word.word.strip(),
                    "start": round(word.start, 2),
                    "end": round(word.end, 2),
                    "probability": round(word.probability, 2)
                })
        print(f"[+] Extracted {len(words_data)} timestamped words in {round(info.duration, 2)}s audio.")
    except Exception as e:
        print(f"[!] Primary transcription note ({e}), running CPU fallback...")
        model = WhisperModel("tiny", device="cpu", compute_type="int8")
        segments, info = model.transcribe(audio_path, word_timestamps=True)
        for segment in segments:
            for word in segment.words:
                words_data.append({
                    "word": word.word.strip(),
                    "start": round(word.start, 2),
                    "end": round(word.end, 2),
                    "probability": round(word.probability, 2)
                })
        print(f"[+] Extracted {len(words_data)} timestamped words on CPU.")
        
    return words_data

def process_audio_for_script(script_id: int) -> Dict[str, Any]:
    """Generates human speech and timestamps for a specific script."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT full_narration FROM scripts WHERE id = ?", (script_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        raise ValueError(f"Script #{script_id} not found.")
        
    text = row["full_narration"]
    audio_path = generate_voiceover(text, script_id)
    timestamps = transcribe_with_word_timestamps(audio_path)
    
    json_path = str(OUTPUT_DIR / f"timestamps_{script_id}.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(timestamps, f, indent=2)
        
    return {
        "audio_path": audio_path,
        "timestamps_path": json_path,
        "word_count": len(timestamps)
    }

if __name__ == "__main__":
    result = process_audio_for_script(1)
    print("Audio processing complete:", result)
