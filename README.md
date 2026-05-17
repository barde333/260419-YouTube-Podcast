# YouTube Podcast Converter

Converts YouTube videos to MP3 and serves them as an iTunes-compatible RSS feed for Pocket Casts on iPhone.

## Overview

- **Backend**: Flask API + SQLite
- **Audio**: yt-dlp + ffmpeg
- **Feed**: RSS 2.0 with iTunes namespace
- **Hosting**: Docker on a personal server
- **Public URL**: `https://podcast.bard3.duckdns.org`

## Quick Start

```bash
cp .env.example .env   # fill in PUBLIC_URL
docker compose up -d
```

## API

| Method | Route | Auth | Description |
|--------|-------|------|-------------|
| GET | `/health` | — | Service health check |
| GET | `/` | — | Web interface |
| GET | `/feed.rss` | — | RSS feed (Pocket Casts) |
| GET | `/api/episodes` | — | List episodes |
| POST | `/api/episodes` | — | Add a YouTube URL |
| DELETE | `/api/episodes/<id>` | — | Delete an episode |
| GET | `/bookmarklet` | — | Shortcut help page |

### Example — add a video

```bash
curl -X POST https://podcast.bard3.duckdns.org/api/episodes \
  -H "Content-Type: application/json" \
  -d '{"url": "https://youtube.com/watch?v=..."}'
```

## Project Structure

```
.
├── src/
│   ├── app.py          # Flask: routes + auth
│   ├── database.py     # SQLite init
│   ├── converter.py    # yt-dlp + ffmpeg (background task)
│   ├── rss.py          # iTunes RSS generator
│   └── wsgi.py         # Gunicorn entry point
├── templates/
│   ├── index.html      # Web interface
│   └── bookmarklet.html
├── data/               # Docker volume: SQLite + MP3
├── Dockerfile
├── docker-compose.yml
├── .env.example
└── requirements.txt
```

## Environment Variables

See [.env.example](.env.example). Key variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `DB_PATH` | `/data/podcast.db` | SQLite database path |
| `MEDIA_DIR` | `/data/media` | MP3 storage directory |
| `PUBLIC_URL` | — | Public URL of the service |
| `MAX_WORKERS` | `2` | Concurrent conversions |
| `YT_DLP_COOKIES_FILE` | — | Cookies file to bypass HTTP 403 |

---

## Pathfinder Progress

### ✅ Step 1 — Project skeleton + GitHub guardrails
- `src/`, `data/` structure, `.gitignore`, `.env.example`
- Git repo initialised, no secrets committed

### ✅ Step 2 — Minimal Flask backend (endpoints + SQLite)
- Table `videos`: id, youtube_url, video_id, title, filename, duration, filesize, status, created_at, converted_at
- Routes: `GET /health`, `GET|POST /api/videos`, `DELETE /api/videos/<id>`, `GET /media/<file>`
- Deduplication by `video_id`

### ✅ Step 3 — YouTube → MP3 conversion engine
- `converter.py`: background daemon thread with `MAX_WORKERS` semaphore
- yt-dlp + ffmpeg: MP3 192K, embedded thumbnail, metadata
- Cookie support (`YT_DLP_COOKIES_FILE`) to bypass HTTP 403
- Statuses: `pending` → `converting` → `done` / `error: ...`

### ✅ Step 4 — RSS feed generator
- `rss.py`: RSS 2.0 + `itunes:` namespace (Pocket Casts compatible)
- Episodes filtered on `status='done'`, sorted by conversion date
- Fields: `<enclosure>` MP3, `<itunes:duration>`, `<pubDate>` RFC 2822

### ✅ Step 5 — Minimal web interface
- Light theme, vanilla CSS (DM Sans font)
- Episode table (title, duration, delete) with placeholders for pending/converting/error states
- YouTube URL input + Add button
- RSS section with copy URL and Pocket Casts link

### ✅ Step 6 — Security: API key
- Bearer token authentication initially implemented
- Simplified in Step 11 for personal usage

### ✅ Step 7 — Dockerisation
- `Dockerfile`: python:3.11-slim + ffmpeg, Gunicorn 2 workers
- `docker-compose.yml`: persistent volume `/opt/podcastyt/data`, port bound to `192.168.2.64:5000`
- `.dockerignore` included

### ✅ Step 8 — Server deployment
- Container `podcastyt` running on CT 103 (`192.168.2.64`)
- Let's Encrypt cert issued for `podcast.bard3.duckdns.org` (via NPM)
- HTTPS enforced — `https://podcast.bard3.duckdns.org/health` ✓

### ✅ Step 9 — iPhone shortcut + desktop bookmarklet
- Browser bookmarklet via `/bookmarklet` page: drag-and-drop instructions
- iOS Shortcuts app for iPhone share integration

### ✅ Step 10 — End-to-end testing
- Full flow validated: YouTube URL → yt-dlp → MP3 → SQLite → RSS feed → Pocket Casts iPhone
- Final backend wiring (routes previously using mock data now connected to DB and converter)
- RSS feed enriched with `<itunes:category>` and `<itunes:owner>` (required by Pocket Casts for feed validation)
- `/media/<filename>` route added to serve MP3 files to podcast clients

### ✅ Step 11 — API key removal (simplified personal use)
- Bearer token authentication removed from `POST /api/episodes` and `DELETE /api/episodes/<id>`
- No more `prompt()` dialogs on mobile or Safari localStorage issues
- Direct web interface and bookmarklet usage without credentials
- `/add` endpoint removed (URL handler pattern deprecated)

---

**Detailed roadmap**: [PATHFINDER.md](PATHFINDER.md)
