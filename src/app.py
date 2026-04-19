from flask import Flask, render_template, request, jsonify
from functools import wraps
import os

app = Flask(__name__, template_folder='../templates')
API_KEY = os.getenv('API_KEY', 'dev-key-change-in-production')

# Mock data for demo
EPISODES = [
    {'id': 1, 'title': 'Joe Rogan #2145 — Elon Musk', 'duration': '3h 02m', 'date': '19 avr.'},
    {'id': 2, 'title': 'Lex Fridman — Sam Altman', 'duration': '2h 18m', 'date': '17 avr.'},
    {'id': 3, 'title': 'Huberman Lab — Sleep Science', 'duration': '1h 44m', 'date': '15 avr.'},
]

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization', '')
        token = auth_header.replace('Bearer ', '') if auth_header.startswith('Bearer ') else None
        if not token or token != API_KEY:
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated_function

@app.route('/health')
def health():
    return jsonify({'status': 'ok'})

# Public routes (no auth needed)
@app.route('/')
def index():
    return render_template('index.html', episodes=EPISODES, rss_url='https://podcast.bard3.duckdns.org/feed.rss')

@app.route('/api/episodes', methods=['GET'])
def get_episodes():
    return jsonify(EPISODES)

@app.route('/feed.rss', methods=['GET'])
def get_rss_feed():
    return 'RSS feed here', 200, {'Content-Type': 'application/rss+xml'}

# Protected routes (API_KEY required)
@app.route('/api/episodes', methods=['POST'])
@require_api_key
def add_episode():
    data = request.get_json()
    if not data or 'url' not in data:
        return jsonify({'error': 'Missing url'}), 400
    return jsonify({'status': 'ok', 'id': 4}), 201

@app.route('/api/episodes/<int:episode_id>', methods=['DELETE'])
@require_api_key
def delete_episode(episode_id):
    return jsonify({'status': 'deleted'}), 200

@app.route('/add', methods=['GET'])
def add_via_url():
    url = request.args.get('url')
    key = request.args.get('key')

    if not url or key != API_KEY:
        return 'Invalid URL or API key', 400

    # Call add_episode logic (would connect to yt-dlp in production)
    return f'<html><body style="font-family:sans-serif;padding:20px"><h2>✓ Ajout en cours</h2><p>YouTube: {url}</p><p>Redirection...</p><script>setTimeout(()=>window.close(),2000)</script></body></html>'

@app.route('/bookmarklet')
def bookmarklet():
    return render_template('bookmarklet.html',
        public_url='https://podcast.bard3.duckdns.org',
        domain='podcast.bard3.duckdns.org')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
