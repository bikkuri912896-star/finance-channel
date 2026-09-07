import os
import platform as _platform
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).parent
load_dotenv(dotenv_path=BASE_DIR / ".env", override=False)
ASSETS_DIR = BASE_DIR / "assets"
BGM_DIR = ASSETS_DIR / "bgm"
CACHE_DIR = BASE_DIR / ".cache"
IMAGE_CACHE_DIR = CACHE_DIR / "images"
OUTPUT_DIR = BASE_DIR / "output"
SESSIONS_DIR = BASE_DIR / "sessions"
USED_TOPICS_FILE = BASE_DIR / "used_topics.json"

for d in [ASSETS_DIR, BGM_DIR, CACHE_DIR, IMAGE_CACHE_DIR, OUTPUT_DIR, SESSIONS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# Color palette — finance theme (deep navy + emerald green + gold)
COLOR_BG        = (8, 18, 38)       # deep navy blue
COLOR_GOLD      = (245, 158, 11)    # amber gold
COLOR_ACCENT    = (16, 185, 129)    # emerald green
COLOR_CREAM     = (248, 247, 244)   # warm white
COLOR_DARK_GOLD = (140, 90, 0)
COLOR_SHADOW    = (0, 0, 0)

# Fonts — bundled in fonts/ for cross-platform compatibility
_FONT_DIR = BASE_DIR / "fonts"
if _platform.system() == "Windows" and not _FONT_DIR.exists():
    FONT_PATH_MINCHO       = "C:/Windows/Fonts/yumindb.ttf"
    FONT_PATH_MINCHO_LIGHT = "C:/Windows/Fonts/yumin.ttf"
    FONT_PATH_LATIN        = "C:/Windows/Fonts/timesbd.ttf"
    FONT_PATH_LATIN_REGULAR= "C:/Windows/Fonts/times.ttf"
else:
    # Linux (GitHub Actions) — use IPA ex Mincho installed via apt
    FONT_PATH_MINCHO        = "/usr/share/fonts/opentype/ipaexfont-mincho/ipaexm.otf"
    FONT_PATH_MINCHO_LIGHT  = "/usr/share/fonts/opentype/ipaexfont-mincho/ipaexm.otf"
    FONT_PATH_LATIN         = "/usr/share/fonts/opentype/ipaexfont-mincho/ipaexm.otf"
    FONT_PATH_LATIN_REGULAR = "/usr/share/fonts/opentype/ipaexfont-mincho/ipaexm.otf"

# Video settings (Shorts: vertical 1080x1920)
VIDEO_WIDTH   = 1080
VIDEO_HEIGHT  = 1920
VIDEO_FPS     = 24
VIDEO_CODEC   = "libx264"
AUDIO_CODEC   = "aac"
VIDEO_BITRATE = "4000k"

# TTS settings
TTS_VOICE  = "ja-JP-KeitaNeural"
TTS_RATE   = "-10%"
TTS_PITCH  = "-20Hz"
TTS_VOLUME = "+0%"

# Channel identity
CHANNEL_NAME    = "お金の泉"
CHANNEL_TAGLINE = "一日一分、金融リテラシーを高めよう"

# Claude model
CLAUDE_MODEL = "claude-sonnet-4-6"

# YouTube upload settings
YOUTUBE_CATEGORY_ID = "27"   # Education
YOUTUBE_LANGUAGE    = "ja"
YOUTUBE_PRIVACY     = "public"

# Scheduling
SCHEDULE_TIME = "19:00"

# Instagram settings
INSTAGRAM_ACCESS_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN", "")
INSTAGRAM_ACCOUNT_ID   = os.getenv("INSTAGRAM_ACCOUNT_ID", "")

# API keys
ANTHROPIC_API_KEY           = os.getenv("ANTHROPIC_API_KEY", "")
YOUTUBE_CLIENT_SECRETS_FILE = os.getenv("YOUTUBE_CLIENT_SECRETS_FILE", "client_secrets.json")
YOUTUBE_TOKEN_FILE          = str(BASE_DIR / "youtube_token.json")
YOUTUBE_SCOPES              = ["https://www.googleapis.com/auth/youtube.upload"]
