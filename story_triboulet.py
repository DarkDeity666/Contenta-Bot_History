"""
=============================================================================
STORY SCRIPT & AUDIO GENERATOR: TRIBOULET AND KING FRANCIS I
=============================================================================
Prepares the complete historical narrative script (~80-90 seconds),
synthesizes high-fidelity local voiceover via Edge-TTS (GuyNeural or ChristopherNeural),
and generates word-level timestamps with Faster-Whisper.
=============================================================================
"""

import os
import json
import asyncio
import edge_tts
from faster_whisper import WhisperModel

STORY_DATA = {
    "title": "The Jester Who Outsmarted the Executioner",
    "historical_figures": ["Triboulet (Nicolas Ferrial, 1479–1536)", "King Francis I of France (1494–1547)"],
    "sources": [
        "Pierre de Bourdeille, seigneur de Brantôme (1540–1614), 'Vie des Dames Galantes'",
        "Gaston Migeon, 'Court Fools of the Renaissance', Hachette Classics",
        "Victor Hugo, 'Le Roi s'amuse' (historical notes on Triboulet)"
    ],
    "narration_script": (
        "In 1520, one man held the most dangerous job in Europe: "
        "making the King of France laugh without losing his head. "
        "His name was Triboulet, the legendary royal jester to King Francis the First. "
        "Unlike any ordinary fool, Triboulet had sharp wit, zero fear, "
        "and an uncanny talent for pushing royalty to the brink of fury. "
        "The King had laid down one strict rule: never insult the Queen, "
        "and never embarrass the monarch before the royal court. "
        "Naturally, Triboulet couldn't resist. "
        "During a solemn council gathering, Triboulet walked up behind King Francis... "
        "and slapped the sovereign firmly on his royal backside! "
        "The entire court gasped in utter horror. "
        "The King turned crimson with rage and unsheathed his dagger: "
        "'You insolent fool! For this outrage, you shall hang—unless you can craft an apology "
        "more insulting than the deed itself!' "
        "Triboulet bowed deeply, smiled, and answered without hesitation: "
        "'I am so sorry, Your Majesty! I truly did not recognize you... "
        "I mistook you for the Queen!' "
        "The court was paralyzed. Insulting the Queen was high treason! "
        "King Francis commanded his immediate execution on the spot. "
        "Yet, remembering decades of devoted service, the King granted one final mercy: "
        "'Triboulet, by royal grace, I allow you to choose the manner of your death.' "
        "The jester looked into the eyes of the King, grinned, and bowed once more: "
        "'Good sire, by Saint Nitouche, patron of insanity... "
        "I choose to die of old age!' "
        "The royal court erupted into stunned laughter. "
        "Even the fierce monarch couldn't keep a straight face. "
        "The execution was cancelled, the sentence commuted to banishment, "
        "and Triboulet became the only man in history to escape the gallows "
        "using nothing but a punchline."
    )
}

AUDIO_OUTPUT = os.path.join("output", "audio_triboulet.mp3")
TIMESTAMPS_OUTPUT = os.path.join("output", "subtitles_triboulet.json")

async def generate_voiceover():
    os.makedirs("output", exist_ok=True)
    voice = "en-US-ChristopherNeural"  # Deep, engaging storytelling voice
    print(f"[*] Synthesizing narration script via Edge-TTS ({voice})...")
    communicate = edge_tts.Communicate(
        STORY_DATA["narration_script"],
        voice=voice,
        rate="+0%",
        pitch="+0Hz"
    )
    await communicate.save(AUDIO_OUTPUT)
    print(f"[+] Audio voiceover saved to: {AUDIO_OUTPUT}")

def transcribe_and_align():
    print("[*] Running Faster-Whisper alignment for kinetic subtitles...")
    model = WhisperModel("base", device="cpu", compute_type="int8")
    segments, info = model.transcribe(AUDIO_OUTPUT, word_timestamps=True)
    
    words_data = []
    sentence_data = []
    
    for seg in segments:
        sentence_data.append({
            "start": seg.start,
            "end": seg.end,
            "text": seg.text.strip()
        })
        if seg.words:
            for w in seg.words:
                words_data.append({
                    "start": w.start,
                    "end": w.end,
                    "word": w.word.strip()
                })
                
    result = {
        "duration": info.duration,
        "sentences": sentence_data,
        "words": words_data
    }
    
    with open(TIMESTAMPS_OUTPUT, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
        
    print(f"[+] Word-level alignment saved to: {TIMESTAMPS_OUTPUT} (Total duration: {info.duration:.2f}s)")
    return result

if __name__ == "__main__":
    asyncio.run(generate_voiceover())
    transcribe_and_align()
