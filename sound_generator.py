import math
import struct
import random
import wave
from pathlib import Path
from config import SFX_DIR, MUSIC_DIR

def create_whoosh_sfx(filename: str = "whoosh.wav", duration: float = 0.4):
    """Synthesizes a clean dynamic whoosh sound effect."""
    sample_rate = 44100
    n_samples = int(sample_rate * duration)
    path = SFX_DIR / filename
    
    with wave.open(str(path), "w") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        
        frames = bytearray()
        for i in range(n_samples):
            t = i / sample_rate
            # Pitch sweeping up then down
            freq = 200 + 1200 * math.sin(math.pi * t / duration)
            # Envelope (fade in, peak, fade out)
            env = math.sin(math.pi * t / duration) ** 2
            # White noise mixed with sine
            noise = (random.random() * 2 - 1) * 0.4
            sample = (math.sin(2 * math.pi * freq * t) * 0.6 + noise) * env
            int_sample = max(-32767, min(32767, int(sample * 18000)))
            frames.extend(struct.pack("<h", int_sample))
            
        wav.writeframes(frames)
    print(f"[+] Synthesized SFX: {filename}")
    return str(path)

def create_dramatic_boom(filename: str = "boom.wav", duration: float = 1.2):
    """Synthesizes a low cinematic orchestral impact boom."""
    sample_rate = 44100
    n_samples = int(sample_rate * duration)
    path = SFX_DIR / filename
    
    with wave.open(str(path), "w") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        
        frames = bytearray()
        for i in range(n_samples):
            t = i / sample_rate
            # Sub-bass dropping pitch (120Hz down to 35Hz)
            freq = max(35, 130 * math.exp(-3.5 * t))
            env = math.exp(-2.8 * t)
            sample = math.sin(2 * math.pi * freq * t) * env
            int_sample = max(-32767, min(32767, int(sample * 24000)))
            frames.extend(struct.pack("<h", int_sample))
            
        wav.writeframes(frames)
    print(f"[+] Synthesized SFX: {filename}")
    return str(path)

def create_tension_drone(filename: str = "history_drone.wav", duration: float = 45.0):
    """Synthesizes a dark, subtle ambient tension bed for documentary shorts."""
    sample_rate = 44100
    n_samples = int(sample_rate * duration)
    path = MUSIC_DIR / filename
    
    with wave.open(str(path), "w") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        
        frames = bytearray()
        for i in range(n_samples):
            t = i / sample_rate
            # Dual oscillating low drone (55Hz A1 + 82.4Hz E2 fifth chord)
            f1, f2 = 55.0, 82.4
            # Subtle low frequency pulse
            lfo = 0.8 + 0.2 * math.sin(2 * math.pi * 0.3 * t)
            sample = (math.sin(2 * math.pi * f1 * t) * 0.6 + math.sin(2 * math.pi * f2 * t) * 0.4) * lfo
            # Very quiet bed (-24dB)
            int_sample = max(-32767, min(32767, int(sample * 4200)))
            frames.extend(struct.pack("<h", int_sample))
            
        wav.writeframes(frames)
    print(f"[+] Synthesized Music Bed: {filename}")
    return str(path)

def generate_all_audio_assets():
    create_whoosh_sfx()
    create_dramatic_boom()
    create_tension_drone()

if __name__ == "__main__":
    generate_all_audio_assets()
