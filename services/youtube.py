import os
import uuid

import yt_dlp

from .utils import zip_folder
import config


async def download_ytv_and_zip(ytv_url: str, format_choice: str) -> str:
    """Download the given URL (video or playlist) and zip the result.

    Each call gets its own unique sub-folder under BASE_DOWNLOAD_DIR so
    concurrent requests from different chats never overwrite or zip
    each other's files.
    """
    request_id = uuid.uuid4().hex[:8]
    request_dir = os.path.join(config.BASE_DOWNLOAD_DIR, request_id)
    os.makedirs(request_dir, exist_ok=True)

    outtmpl = os.path.join(request_dir, "%(title)s.%(ext)s")

    if format_choice == "mp3":
        ydl_opts = config.audio_ydl_opts(outtmpl)
    else:
        ydl_opts = config.video_ydl_opts(outtmpl)

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(ytv_url, download=False)
        download_title = info.get("title", "Unknown Playlist")
        ydl.download([ytv_url])

    safe_title = "".join(c for c in download_title if c not in '\\/:*?"<>|').strip() or "download"
    zip_path = os.path.join(config.BASE_DOWNLOAD_DIR, f"{safe_title}-{request_id}.zip")

    await zip_folder(request_dir, zip_path)

    # Clean up the raw (unzipped) files now that they're zipped.
    for root, _, files in os.walk(request_dir, topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))
        os.rmdir(root)

    return zip_path
