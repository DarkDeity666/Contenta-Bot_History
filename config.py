import os
from pathlib import Path
from dotenv import load_dotenv

# Base Paths
BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"
CHAR_DIR = ASSETS_DIR / "character"
GFX_DIR = ASSETS_DIR / "graphics"
FONTS_DIR = ASSETS_DIR / "fonts"
MUSIC_DIR = ASSETS_DIR / "music"
SFX_DIR = ASSETS_DIR / "sfx"
IMAGES_DIR = ASSETS_DIR / "images"
OUTPUT_DIR = BASE_DIR / "output"
DB_PATH = BASE_DIR / "history_vault.db"

# Ensure directories exist
for directory in [ASSETS_DIR, CHAR_DIR, GFX_DIR, FONTS_DIR, MUSIC_DIR, SFX_DIR, IMAGES_DIR, OUTPUT_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Load environment variables
load_dotenv(BASE_DIR / ".env")

# 100% Free AI Keys (All optional! System works 100% offline with zero cost if blank)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")    # 100% Free at https://aistudio.google.com/
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")        # 100% Free alternative at https://console.groq.com/
YOUTUBE_CLIENT_SECRET_FILE = os.getenv("YOUTUBE_CLIENT_SECRET_FILE", str(BASE_DIR / "client_secret.json"))

# Hardware Acceleration & Local Resource Tuning (RTX 3060 6GB + 16GB RAM)
USE_NVENC = True                  # NVIDIA NVENC hardware chip (h264_nvenc)
WHISPER_DEVICE = "cpu"            # Fast int8 CPU transcription (takes ~1.2s, leaves 100% of VRAM free for you)
WHISPER_COMPUTE_TYPE = "int8"
MAX_CONCURRENT_RENDERS = 1        # Render 1 video at a time
FFMPEG_THREADS = 2                # Limit CPU threads so IDE never stutters

# Network & Port Isolation
# Using obscure unassigned high port to NEVER touch 3000, 8000, 8080, etc.
OAUTH_REDIRECT_PORT = 54892

# Video & Persona Settings
VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920
FPS = 60
TARGET_DURATION = 45

# Hyper-Realistic 100% Free Neural Storytelling Voices (Microsoft Cognitive Neural)
# Brian is deep, rich, and sounds like a gripping documentary narrator with natural breath pauses
DEFAULT_VOICE = "en-US-BrianMultilingualNeural"
SECONDARY_VOICE = "en-US-AndrewMultilingualNeural"
VOICE_RATE = "+2%"
VOICE_PITCH = "-1Hz"

# Colors & Aesthetic (Antique History Theme)
COLOR_BACKGROUND = "#14110F"  # Rich dark antique charcoal
COLOR_GOLD = "#FFD700"        # Royal gold accent
COLOR_WHITE = "#FFFFFF"
