import os
from dotenv import load_dotenv  # type: ignore

load_dotenv()

# --- Telegram ---
BOT_TOKEN = os.getenv("BOT_TOKEN")

# --- Storage ---
# Base folder where downloads are temporarily stored before zipping.
# Each request gets its own sub-folder (see services/youtube.py) so
# concurrent users never collide.
BASE_DOWNLOAD_DIR = os.getenv("DOWNLOAD_DIR", "download")

# --- Limits ---
# Telegram bot API hard-caps regular bot uploads at 50MB.
MAX_UPLOAD_SIZE_MB = int(os.getenv("MAX_UPLOAD_SIZE_MB", "50"))
MAX_UPLOAD_SIZE_BYTES = MAX_UPLOAD_SIZE_MB * 1024 * 1024

# Cap on number of playlist entries to download in one go, so a huge
# playlist can't blow past the upload limit or run for hours.
MAX_PLAYLIST_ITEMS = int(os.getenv("MAX_PLAYLIST_ITEMS", "25"))

# --- yt-dlp ---
AUDIO_FORMAT = os.getenv("AUDIO_FORMAT", "mp3")
AUDIO_QUALITY = os.getenv("AUDIO_QUALITY", "192")


def audio_ydl_opts(outtmpl: str) -> dict:
    return {
        "outtmpl": outtmpl,
        "format": "bestaudio/best",
        "playlistend": MAX_PLAYLIST_ITEMS,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": AUDIO_FORMAT,
                "preferredquality": AUDIO_QUALITY,
            }
        ],
    }


def video_ydl_opts(outtmpl: str) -> dict:
    return {
        "outtmpl": outtmpl,
        "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "merge_output_format": "mp4",
        "playlistend": MAX_PLAYLIST_ITEMS,
    }
