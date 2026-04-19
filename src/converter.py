import os
import threading
import subprocess
from datetime import datetime

from database import get_conn

MEDIA_DIR = os.environ.get("MEDIA_DIR", "/data/media")
COOKIES_FILE = os.environ.get("YT_DLP_COOKIES_FILE", "")
MAX_WORKERS = int(os.environ.get("MAX_WORKERS", "2"))

_semaphore = threading.Semaphore(MAX_WORKERS)


def enqueue(video_db_id: int, youtube_url: str):
    t = threading.Thread(target=_worker, args=(video_db_id, youtube_url), daemon=True)
    t.start()


def _worker(video_db_id: int, youtube_url: str):
    with _semaphore:
        _set_status(video_db_id, "converting")
        try:
            filename, title, duration, filesize = _convert(youtube_url)
            with get_conn() as conn:
                conn.execute(
                    """UPDATE videos
                       SET status='done', filename=?, title=?, duration=?, filesize=?,
                           converted_at=datetime('now')
                       WHERE id=?""",
                    (filename, title, duration, filesize, video_db_id),
                )
                conn.commit()
        except Exception as exc:
            _set_status(video_db_id, f"error: {exc}")


def _set_status(video_db_id: int, status: str):
    with get_conn() as conn:
        conn.execute("UPDATE videos SET status=? WHERE id=?", (status, video_db_id))
        conn.commit()


def _convert(youtube_url: str):
    os.makedirs(MEDIA_DIR, exist_ok=True)

    # Récupère les métadonnées d'abord
    meta = _yt_dlp_json(youtube_url)
    video_id = meta["id"]
    title = meta.get("title", video_id)
    duration = meta.get("duration")  # secondes
    filename = f"{video_id}.mp3"
    out_path = os.path.join(MEDIA_DIR, filename)

    if not os.path.exists(out_path):
        _run_yt_dlp(youtube_url, out_path)

    filesize = os.path.getsize(out_path) if os.path.exists(out_path) else None
    return filename, title, duration, filesize


def _base_yt_dlp_args():
    args = ["yt-dlp", "--no-playlist"]
    if COOKIES_FILE and os.path.exists(COOKIES_FILE):
        args += ["--cookies", COOKIES_FILE]
    return args


def _yt_dlp_json(youtube_url: str) -> dict:
    import json
    args = _base_yt_dlp_args() + ["--dump-json", "--skip-download", youtube_url]
    result = subprocess.run(args, capture_output=True, text=True, timeout=60)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "yt-dlp metadata failed")
    return json.loads(result.stdout)


def _run_yt_dlp(youtube_url: str, out_path: str):
    # Télécharge et extrait l'audio en MP3 via yt-dlp + ffmpeg
    args = _base_yt_dlp_args() + [
        "--extract-audio",
        "--audio-format", "mp3",
        "--audio-quality", "192K",
        "--embed-thumbnail",
        "--add-metadata",
        "-o", out_path.replace(".mp3", ".%(ext)s"),
        youtube_url,
    ]
    result = subprocess.run(args, capture_output=True, text=True, timeout=900)
    if result.returncode != 0:
        raise RuntimeError(result.stderr[-500:] or "yt-dlp conversion failed")
