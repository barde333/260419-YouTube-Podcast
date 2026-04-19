from flask import Flask, render_template, request, jsonify
import json
from pathlib import Path

app = Flask(__name__, template_folder='../templates')
DB_PATH = Path('/app/data/podcast.db') if Path('/app/data').exists() else Path('./data/podcast.json')

# Mock data for demo
EPISODES = [
    {'id': 1, 'title': 'Joe Rogan #2145 — Elon Musk', 'duration': '3h 02m', 'date': '19 avr.'},
    {'id': 2, 'title': 'Lex Fridman — Sam Altman', 'duration': '2h 18m', 'date': '17 avr.'},
    {'id': 3, 'title': 'Huberman Lab — Sleep Science', 'duration': '1h 44m', 'date': '15 avr.'},
]

@app.route('/')
def index():
    return render_template('index.html', episodes=EPISODES, rss_url='https://podcast.bard3.duckdns.org/feed.rss')

@app.route('/api/episodes')
def get_episodes():
    return jsonify(EPISODES)

@app.route('/api/episodes', methods=['POST'])
def add_episode():
    return jsonify({'status': 'ok'}), 201

if __name__ == '__main__':
    app.run(debug=True, port=5000)
