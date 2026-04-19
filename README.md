# YouTube Podcast Converter

Convertit des vidéos YouTube en MP3 et les sert via un flux RSS compatible avec Pocket Casts sur iPhone.

## Vue d'ensemble

- **Backend** : Flask API + SQLite
- **Audio** : yt-dlp + ffmpeg
- **Flux** : RSS 2.0 standard iTunes
- **Hébergement** : Docker sur serveur personnel
- **URL publique** : `https://podcast.bard3.duckdns.org`

## Démarrage rapide

```bash
cp .env.example .env   # puis renseigner API_KEY et PUBLIC_URL
docker compose up -d
```

## API

| Méthode | Route | Auth | Description |
|---------|-------|------|-------------|
| GET | `/health` | — | Santé du service |
| GET | `/` | — | Interface web |
| GET | `/feed.rss` | — | Flux RSS (Pocket Casts) |
| GET | `/api/episodes` | — | Liste des épisodes |
| POST | `/api/episodes` | Bearer | Ajouter une URL YouTube |
| DELETE | `/api/episodes/<id>` | Bearer | Supprimer un épisode |
| GET | `/add?url=...&key=...` | key param | Raccourci iPhone / bookmarklet |
| GET | `/bookmarklet` | — | Page d'aide raccourcis |

### Exemple — ajouter une vidéo

```bash
curl -X POST https://podcast.bard3.duckdns.org/api/episodes \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://youtube.com/watch?v=..."}'
```

## Structure

```
.
├── src/
│   ├── app.py          # Flask : routes + auth
│   ├── database.py     # Init SQLite
│   ├── converter.py    # yt-dlp + ffmpeg (tâche de fond)
│   ├── rss.py          # Générateur RSS iTunes
│   └── wsgi.py         # Point d'entrée Gunicorn
├── templates/
│   ├── index.html      # Interface web
│   └── bookmarklet.html
├── data/               # Volume Docker : SQLite + MP3
├── Dockerfile
├── docker-compose.yml
├── .env.example
└── requirements.txt
```

## Variables d'environnement

Voir [.env.example](.env.example). Variables principales :

| Variable | Valeur par défaut | Description |
|----------|-------------------|-------------|
| `API_KEY` | — | Clé Bearer pour endpoints protégés |
| `DB_PATH` | `/data/podcast.db` | Chemin base SQLite |
| `MEDIA_DIR` | `/data/media` | Dossier MP3 |
| `PUBLIC_URL` | — | URL publique du service |
| `MAX_WORKERS` | `2` | Conversions simultanées |
| `YT_DLP_COOKIES_FILE` | — | Cookies pour contourner les 403 |

---

## Progression Pathfinder

### ✅ Étape 1 — Squelette du projet + garde-fous GitHub
- Structure `src/`, `data/`, `.gitignore`, `.env.example`
- Git repo initialisé, aucun secret committé

### ✅ Étape 2 — Backend Flask minimal (endpoints + SQLite)
- Table `videos` : id, youtube_url, video_id, title, filename, duration, filesize, status, created_at, converted_at
- Routes : `GET /health`, `GET|POST /api/videos`, `DELETE /api/videos/<id>`, `GET /media/<file>`
- Déduplication par `video_id`

### ✅ Étape 3 — Moteur de conversion YouTube → MP3
- `converter.py` : tâche de fond (thread daemon) avec sémaphore `MAX_WORKERS`
- yt-dlp + ffmpeg : MP3 192K, miniature intégrée, métadonnées
- Support cookies (`YT_DLP_COOKIES_FILE`) pour contourner les HTTP 403
- Statuts : `pending` → `converting` → `done` / `error: ...`

### ✅ Étape 4 — Générateur de flux RSS
- `rss.py` : RSS 2.0 + namespace `itunes:` (compatible Pocket Casts)
- Épisodes filtrés sur `status='done'`, triés par date de conversion
- Champs : `<enclosure>` MP3, `<itunes:duration>`, `<pubDate>` RFC 2822

### ✅ Étape 5 — Page web minimaliste
- Interface dark mode CSS vanilla
- Tableau épisodes (titre, durée, date, suppression)
- Champ URL YouTube + bouton Ajouter
- Section RSS avec copie d'URL et lien Pocket Casts

### ✅ Étape 6 — Sécurité : clé API
- Décorateur `@require_api_key` (Bearer token)
- Routes protégées : `POST /api/episodes`, `DELETE /api/episodes/<id>`
- Routes publiques : `GET /api/episodes`, `GET /feed.rss`, `GET /`

### ✅ Étape 7 — Dockerisation
- `Dockerfile` : python:3.11-slim + ffmpeg, Gunicorn 2 workers
- `docker-compose.yml` : volume persistant `/opt/podcastyt/data`, port bindé sur `192.168.2.64:5000`
- `.dockerignore` inclus

### ✅ Étape 8 — Déploiement sur le serveur
- Container `podcastyt` actif sur CT 103 (`192.168.2.64`)
- Cert Let's Encrypt émis pour `podcast.bard3.duckdns.org` (via NPM)
- HTTPS forcé — `https://podcast.bard3.duckdns.org/health` ✓

### ✅ Étape 9 — Raccourci iPhone + Bookmarklet desktop
- Endpoint `/add?url=...&key=...` pour URL handler (iOS Shortcuts + navigateur)
- Page `/bookmarklet` : instructions drag-and-drop

### ✅ Étape 10 — Tests de bout en bout
- Parcours complet validé : URL YouTube → yt-dlp → MP3 → SQLite → flux RSS → Pocket Casts iPhone
- Câblage final du backend (les routes `/feed.rss`, `POST /api/episodes`, `DELETE`, `/add` utilisaient des données mock ; désormais connectées à la DB et au converter)
- Flux RSS enrichi avec `<itunes:category>` et `<itunes:owner>` (requis par Pocket Casts pour valider l'abonnement)
- Route `/media/<filename>` ajoutée pour servir les MP3 aux clients podcast

---

**Roadmap détaillée** : [PATHFINDER.md](PATHFINDER.md)
