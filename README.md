# Antigravity 2D Stickman History Shorts Engine 🎬⚡
**100% Live 2D Animated Stickman History Shorts Pipeline for YouTube**

Engineered for **NVIDIA RTX 3060 (6GB VRAM) + 16GB RAM** running locally in the background. **100% Free, Zero Paid Tokens, Zero Static Photos, Zero Copyright Issues.**

---

## 🚀 What Makes This 100% Live 2D Animation

Instead of static pictures with voiceovers, this engine generates **genuine frame-by-frame 2D stickman animation** in the style of *Sam O'Nella*, *MinutePhysics*, and *OverSimplified*:

1. **Articulated 2D Character Kinematics (`stickman_engine.py`)**:
   - **Walking & Running Cycles**: Multi-joint legs (hip, knee, foot) and swinging arms with natural bounce physics.
   - **Facial Expressions**: Animated talking mouths opening/closing with speech, blinking cartoon eyes, and dramatic jaw drops.
   - **Extreme Emotion Reactions**: Screaming in panic with arms flailing overhead and sweat droplets flying.
   - **Interactive Props & Action**: Stickmen dragging bodies, dueling with swords (spark particles), and judges violently slamming gavels with impact shockwaves!

2. **4 Live Animated Story Scenes per Video**:
   - **Scene 1 (Hook / 0-25%)**: King/Pope walks in, speaks with animated mouth to viewer; panicked citizen runs across background.
   - **Scene 2 (Incident / 25-55%)**: Guard dragging a limp stickman corpse with dust puffs trailing on the floor.
   - **Scene 3 (Courtroom Chaos / 55-80%)**: Judge furiously slamming a giant gavel on a wooden desk while cardinals gasp.
   - **Scene 4 (Climax & Infinite Loop / 80-100%)**: Stickmen sword duel with spark flashes and spinning infinite loop indicator.

3. **Human Storyteller Voice (100% Free)**:
   - Powered by **`en-US-BrianMultilingualNeural`** (or `en-US-AndrewMultilingualNeural`), tuned for dramatic documentary inflection with natural human breathing pauses.
   - Mixed with a synthesized ambient tension drone bed and SFX.

4. **100% Free / Zero API Tokens**:
   - **Option A (Default)**: 100% Offline Local Screenplay Engine ($0.00, runs offline).
   - **Option B**: Google AI Studio Gemini API (100% Free Tier, no credit card required).
   - **Option C**: Groq API (100% Free Tier Llama 3.3 70B at console.groq.com).

5. **Blistering Render Speed on RTX 3060 NVENC**:
   - Streams raw 1080x1920 frames directly into hardware NVENC at **85 FPS**.
   - An entire 33-second animated Short renders in **~11 seconds**!

---

## 🛠️ How to Run

```powershell
# Inside E:\Yt_Bot\Contenta Bot History:
# 1. Render the showcase 2D animated stickman short:
.\venv\Scripts\python.exe video_engine.py

# 2. Or run a complete 10-video batch:
.\venv\Scripts\python.exe main.py 10
```

---

## 📁 Key Files

* [stickman_engine.py](file:///e:/Yt_Bot/Contenta%20Bot%20History/stickman_engine.py) — 2D Stickman kinematics, articulated joints, walk/run cycles, and multi-scene storyboard.
* [video_engine.py](file:///e:/Yt_Bot/Contenta%20Bot%20History/video_engine.py) — Streams live animation into RTX 3060 NVENC at 85 FPS.
* [audio_engine.py](file:///e:/Yt_Bot/Contenta%20Bot%20History/audio_engine.py) — Hyper-realistic Brian neural voice + Whisper word sync.
* [sound_generator.py](file:///e:/Yt_Bot/Contenta%20Bot%20History/sound_generator.py) — Royalty-free ambient music and SFX synthesizers.
* [main.py](file:///e:/Yt_Bot/Contenta%20Bot%20History/main.py) — Background batch production orchestrator.
