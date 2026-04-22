import os
import re
from functools import wraps
from urllib.parse import urlparse, parse_qs

from flask import Flask, render_template, request, jsonify, send_from_directory, abort

from rss import build_rss
from database import init_db, get_conn
from converter import enqueue

init_db()

app = Flask(__name__, template_folder='../templates')
API_KEY = os.getenv('API_KEY', 'dev-key-change-in-production')
MEDIA_DIR = os.environ.get("MEDIA_DIR", "/data/media")
PUBLIC_URL = os.environ.get("PUBLIC_URL", "http://localhost:5000").rstrip("/")


def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization', '')
        token = auth_header.replace('Bearer ', '') if auth_header.startswith('Bearer ') else None
        if not token or token != API_KEY:
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated_function


def extract_video_id(url: str):
    try:
        p = urlparse(url)
    except Exception:
        return None
    host = (p.hostname or '').lower()
    if host.endswith('youtu.be'):
        vid = p.path.lstrip('/').split('/')[0]
        return vid or None
    if 'youtube.com' in host:
        qs = parse_qs(p.query)
        if 'v' in qs:
            return qs['v'][0]
        m = re.match(r'^/(shorts|embed)/([^/?#]+)', p.path)
        if m:
            return m.group(2)
    return None


def row_to_public(row):
    created = row['converted_at'] or row['created_at'] or ''
    date = created[:10] if created else ''
    duration = row['duration'] or 0
    if duration:
        h, rem = divmod(int(duration), 3600)
        m, s = divmod(rem, 60)
        dur_str = f"{h}h{m:02d}" if h else f"{m}:{s:02d}"
    else:
        dur_str = '—'
    status = row['status'] or ''
    if status == 'done':
        title = row['title'] or row['video_id']
    elif status == 'pending':
        title = 'En attente…'
    elif status == 'converting':
        title = 'Conversion en cours…'
    elif status.startswith('error'):
        title = f'⚠ Erreur : {status[6:].lstrip(": ").strip() or "inconnue"}'
    else:
        title = row['title'] or row['video_id']
    return {
        'id': row['id'],
        'title': title,
        'duration': dur_str,
        'date': date,
        'status': status,
    }


def list_episodes():
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM videos ORDER BY COALESCE(converted_at, created_at) DESC"
        ).fetchall()
    return [row_to_public(r) for r in rows]


@app.route('/health')
def health():
    return jsonify({'status': 'ok'})


@app.route('/')
def index():
    return render_template(
        'index.html',
        episodes=list_episodes(),
        rss_url=f"{PUBLIC_URL}/feed.rss",
    )


@app.route('/api/episodes', methods=['GET'])
def get_episodes():
    return jsonify(list_episodes())


@app.route('/feed.rss', methods=['GET'])
def get_rss_feed():
    return build_rss(), 200, {'Content-Type': 'application/rss+xml; charset=utf-8'}


def _add_url(url: str):
    video_id = extract_video_id(url)
    if not video_id:
        return {'error': 'Invalid YouTube URL'}, 400
    with get_conn() as conn:
        existing = conn.execute(
            "SELECT id, status FROM videos WHERE video_id=?", (video_id,)
        ).fetchone()
        if existing:
            return {'status': existing['status'], 'id': existing['id'], 'duplicate': True}, 200
        cur = conn.execute(
            "INSERT INTO videos (youtube_url, video_id, status) VALUES (?, ?, 'pending')",
            (url, video_id),
        )
        conn.commit()
        new_id = cur.lastrowid
    enqueue(new_id, url)
    return {'status': 'pending', 'id': new_id}, 201


@app.route('/api/episodes', methods=['POST'])
@require_api_key
def add_episode():
    data = request.get_json(silent=True) or {}
    url = data.get('url')
    if not url:
        return jsonify({'error': 'Missing url'}), 400
    body, code = _add_url(url)
    return jsonify(body), code


@app.route('/api/episodes/<int:episode_id>', methods=['DELETE'])
@require_api_key
def delete_episode(episode_id):
    with get_conn() as conn:
        row = conn.execute("SELECT filename FROM videos WHERE id=?", (episode_id,)).fetchone()
        if not row:
            return jsonify({'error': 'Not found'}), 404
        filename = row['filename']
        conn.execute("DELETE FROM videos WHERE id=?", (episode_id,))
        conn.commit()
    if filename:
        try:
            os.remove(os.path.join(MEDIA_DIR, filename))
        except FileNotFoundError:
            pass
    return jsonify({'status': 'deleted'}), 200


@app.route('/add', methods=['GET'])
def add_via_url():
    url = request.args.get('url')
    key = request.args.get('key')
    if not url or key != API_KEY:
        return 'Invalid URL or API key', 400
    body, code = _add_url(url)
    msg = 'Ajout en cours' if code == 201 else ('Déjà présent' if body.get('duplicate') else 'Erreur')
    return f'<html><body style="font-family:sans-serif;padding:20px"><h2>✓ {msg}</h2><p>YouTube: {url}</p><p>Statut: {body.get("status")}</p><script>setTimeout(()=>window.close(),2000)</script></body></html>'


@app.route('/media/<path:filename>')
def serve_media(filename):
    if '..' in filename or filename.startswith('/'):
        abort(404)
    return send_from_directory(MEDIA_DIR, filename, mimetype='audio/mpeg')


@app.route('/bookmarklet')
def bookmarklet():
    domain = urlparse(PUBLIC_URL).netloc or 'podcast.bard3.duckdns.org'
    return render_template('bookmarklet.html', public_url=PUBLIC_URL, domain=domain)


if __name__ == '__main__':
    app.run(debug=True, port=int(os.environ.get('PORT', 5000)))
