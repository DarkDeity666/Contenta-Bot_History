"""
=============================================================================
SFX & FOLEY GENERATOR - RENAISSANCE COURT
=============================================================================
Generates procedural sound effects and mixes background lute music:
- Jester bells jingling
- Comic slap impact sound
- Crowd gasp / court murmur
- Stunned silence / record scratch
- Cheerful royal court laughter & applause
- Gentle Renaissance lute background music
=============================================================================
"""

import math
import struct
import wave
import os

OUTPUT_DIR = os.path.join("assets", "audio")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def write_wav(filename, samples, sample_rate=44100):
    filepath = os.path.join(OUTPUT_DIR, filename)
    with wave.open(filepath, "w") as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        # Normalize and pack
        max_val = max(max(abs(s) for s in samples), 1e-5)
        scale = 30000.0 / max_val
        data = bytearray()
        for s in samples:
            val = int(s * scale)
            val = max(-32767, min(32767, val))
            data.extend(struct.pack("<h", val))
        wav_file.writeframes(data)
    print(f"[+] Saved SFX: {filepath}")
    return filepath

def generate_jester_bells():
    """Generates bright shimmering silver bells."""
    sr = 44100
    duration = 1.2
    num_samples = int(sr * duration)
    samples = [0.0] * num_samples
    
    # Fundamental frequencies of small brass bells
    freqs = [2093.0, 2349.0, 2793.0, 3136.0, 4186.0]
    for i in range(num_samples):
        t = i / sr
        env = math.exp(-t * 6.0)
        val = 0.0
        for f in freqs:
            val += math.sin(2.0 * math.pi * f * t) * 0.2
            # Add slight frequency modulation for jingle
            val += math.sin(2.0 * math.pi * (f + 15.0 * math.sin(2 * math.pi * 12 * t)) * t) * 0.15
        samples[i] = val * env
    return write_wav("sfx_jester_bells.wav", samples)

def generate_slap_impact():
    """Generates punchy comic slap sound with sharp attack and flesh impact."""
    sr = 44100
    duration = 0.4
    num_samples = int(sr * duration)
    samples = [0.0] * num_samples
    import random
    random.seed(42)
    
    for i in range(num_samples):
        t = i / sr
        # Sharp high-frequency burst + low resonant body thud
        env_crack = math.exp(-t * 45.0)
        env_thud = math.exp(-t * 18.0)
        noise = (random.random() * 2.0 - 1.0) * env_crack
        thud = math.sin(2.0 * math.pi * 140.0 * math.exp(-t * 20.0) * t) * env_thud
        samples[i] = (noise * 0.7 + thud * 0.8)
    return write_wav("sfx_slap_impact.wav", samples)

def generate_court_gasp():
    """Generates sudden breath intake / gasp of shock."""
    sr = 44100
    duration = 1.0
    num_samples = int(sr * duration)
    samples = [0.0] * num_samples
    import random
    random.seed(123)
    
    for i in range(num_samples):
        t = i / sr
        # Inhaling shaped noise with rising formant
        env = math.sin(math.pi * (t / duration)) ** 2
        f = 400.0 + 300.0 * (t / duration)
        noise = (random.random() * 2.0 - 1.0)
        resonance = math.sin(2.0 * math.pi * f * t) * noise
        samples[i] = resonance * env * 0.6
    return write_wav("sfx_court_gasp.wav", samples)

def generate_punchline_whistle():
    """Generates comedic slide up / punchline chime."""
    sr = 44100
    duration = 1.5
    num_samples = int(sr * duration)
    samples = [0.0] * num_samples
    
    # Triumphant golden chord (C major: C5, E5, G5, C6)
    notes = [523.25, 659.25, 783.99, 1046.50]
    for i in range(num_samples):
        t = i / sr
        env = math.exp(-t * 2.5)
        val = 0.0
        for n in notes:
            val += math.sin(2.0 * math.pi * n * t) * 0.25
        samples[i] = val * env
    return write_wav("sfx_triumph_chime.wav", samples)

def generate_court_laughter():
    """Generates warm court laughter and amused murmurs."""
    sr = 44100
    duration = 3.5
    num_samples = int(sr * duration)
    samples = [0.0] * num_samples
    import random
    random.seed(777)
    
    # Multiple laughing voices
    ha_times = [0.1, 0.35, 0.6, 0.85, 1.1, 1.4, 1.7, 2.0]
    for ht in ha_times:
        start_idx = int(ht * sr)
        freq = random.uniform(180, 280)
        ha_len = int(0.22 * sr)
        for j in range(ha_len):
            if start_idx + j < num_samples:
                t = j / sr
                env = math.sin(math.pi * (t / 0.22))
                samples[start_idx + j] += math.sin(2.0 * math.pi * freq * t) * env * 0.4
                # Add breathy noise
                samples[start_idx + j] += (random.random() * 2 - 1) * env * 0.15
                
    return write_wav("sfx_court_laughter.wav", samples)

def generate_renaissance_ambience(total_duration=116.0):
    """Generates gentle ambient Renaissance lute progression for background."""
    sr = 44100
    num_samples = int(sr * total_duration)
    samples = [0.0] * num_samples
    
    # Plucked lute chords progression (D minor, C major, F major, A minor, D minor)
    chords = [
        [146.83, 220.0, 261.63, 349.23],  # Dm
        [130.81, 196.0, 261.63, 329.63],  # C
        [174.61, 220.0, 261.63, 349.23],  # F
        [110.0, 164.81, 220.0, 261.63],   # Am
    ]
    
    chord_len = 3.0  # seconds per chord
    num_chords = int(total_duration / chord_len) + 1
    
    for c_idx in range(num_chords):
        chord = chords[c_idx % len(chords)]
        chord_start_t = c_idx * chord_len
        # Arpeggiate notes in chord
        for note_idx, note_f in enumerate(chord):
            note_start_t = chord_start_t + note_idx * 0.45
            start_i = int(note_start_t * sr)
            note_dur = 2.4
            note_samples = int(note_dur * sr)
            for j in range(note_samples):
                if start_i + j < num_samples:
                    t = j / sr
                    env = math.exp(-t * 2.2)
                    # Plucked string harmonic rich tone
                    tone = (math.sin(2.0 * math.pi * note_f * t) * 0.5 +
                            math.sin(2.0 * math.pi * note_f * 2.0 * t) * 0.25 +
                            math.sin(2.0 * math.pi * note_f * 3.0 * t) * 0.1)
                    samples[start_i + j] += tone * env * 0.12  # Low background bed
                    
    return write_wav("bgm_renaissance_lute.wav", samples)

if __name__ == "__main__":
    print("[*] Generating procedural Foley SFX and Renaissance lute bed...")
    generate_jester_bells()
    generate_slap_impact()
    generate_court_gasp()
    generate_punchline_whistle()
    generate_court_laughter()
    generate_renaissance_ambience(116.0)
    print("[+] All sound effects and background bed generated successfully!")
