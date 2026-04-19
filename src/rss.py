import os
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom.minidom import parseString
from datetime import datetime, timezone

from database import get_conn

PUBLIC_URL = os.environ.get("PUBLIC_URL", "http://localhost:5000").rstrip("/")
PODCAST_TITLE = os.environ.get("PODCAST_TITLE", "My YouTube Podcast")
PODCAST_DESC = os.environ.get("PODCAST_DESCRIPTION", "YouTube videos converted to audio")
PODCAST_LANG = os.environ.get("PODCAST_LANGUAGE", "fr")
PODCAST_AUTHOR = os.environ.get("PODCAST_AUTHOR", "Anonymous")
PODCAST_OWNER_EMAIL = os.environ.get("PODCAST_OWNER_EMAIL", "owner@example.com")
PODCAST_CATEGORY = os.environ.get("PODCAST_CATEGORY", "Technology")

ITUNES_NS = "http://www.itunes.com/dtds/podcast-1.0.dtd"


def build_rss() -> str:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM videos WHERE status='done' ORDER BY converted_at DESC"
        ).fetchall()

    rss = Element("rss", version="2.0")
    rss.set("xmlns:itunes", ITUNES_NS)

    channel = SubElement(rss, "channel")
    _text(channel, "title", PODCAST_TITLE)
    _text(channel, "link", PUBLIC_URL)
    _text(channel, "description", PODCAST_DESC)
    _text(channel, "language", PODCAST_LANG)
    _text(channel, "lastBuildDate", _rfc2822_now())

    itunes = lambda tag, val: _text(channel, f"itunes:{tag}", val)
    itunes("author", PODCAST_AUTHOR)
    itunes("explicit", "no")
    itunes("summary", PODCAST_DESC)
    SubElement(channel, "itunes:image", href=f"{PUBLIC_URL}/static/cover.png")
    SubElement(channel, "itunes:category", text=PODCAST_CATEGORY)
    owner = SubElement(channel, "itunes:owner")
    _text(owner, "itunes:name", PODCAST_AUTHOR)
    _text(owner, "itunes:email", PODCAST_OWNER_EMAIL)

    for row in rows:
        item = SubElement(channel, "item")
        title = row["title"] or row["video_id"]
        _text(item, "title", title)
        _text(item, "itunes:title", title)

        mp3_url = f"{PUBLIC_URL}/media/{row['filename']}"
        enc = SubElement(item, "enclosure")
        enc.set("url", mp3_url)
        enc.set("type", "audio/mpeg")
        enc.set("length", str(row["filesize"] or 0))

        _text(item, "guid", mp3_url)
        _text(item, "link", row["youtube_url"])
        _text(item, "pubDate", _to_rfc2822(row["converted_at"]))
        _text(item, "itunes:author", PODCAST_AUTHOR)

        if row["duration"]:
            _text(item, "itunes:duration", _fmt_duration(int(row["duration"])))

    raw = tostring(rss, encoding="unicode")
    return parseString(raw).toprettyxml(indent="  ", encoding=None)


# ---------------------------------------------------------------------------

def _text(parent: Element, tag: str, text: str):
    el = SubElement(parent, tag)
    el.text = text
    return el


def _rfc2822_now() -> str:
    return datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S +0000")


def _to_rfc2822(dt_str: str) -> str:
    if not dt_str:
        return _rfc2822_now()
    try:
        dt = datetime.fromisoformat(dt_str).replace(tzinfo=timezone.utc)
        return dt.strftime("%a, %d %b %Y %H:%M:%S +0000")
    except ValueError:
        return _rfc2822_now()


def _fmt_duration(seconds: int) -> str:
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"
