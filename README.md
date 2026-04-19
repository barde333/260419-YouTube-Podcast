# YouTube Podcast Converter

Convertit des vidéos YouTube en MP3 et les sert via un flux RSS compatible avec Pocket Casts sur iPhone.

## Vue d'ensemble

- **Backend** : Flask API + SQLite
- **Audio** : yt-dlp + ffmpeg
- **Flux** : RSS 2.0 standard iTunes
- **Hébergement** : Docker sur serveur personnel
- **URL** : `podcast.bard3.duckdns.org`

## Installation

```bash
docker-compose up -d
```

## API

### Ajouter une vidéo

```bash
curl -X POST http://localhost:5000/api/videos \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://youtube.com/watch?v=..."}'
```

### Flux RSS

```
http://localhost:5000/feed.rss
```

### Lister les vidéos

```bash
curl http://localhost:5000/api/videos
```

## Structure

```
.
├── src/               # Code Python
├── data/              # Base SQLite et MP3 (volume Docker)
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

## Variables d'environnement

Voir `.env.example` et créer `.env` pour la configuration locale.

---

## 📋 Progression du Pathfinder

### ✅ Étape 1 : Squelette du projet + garde-fous GitHub
- Structure dossiers (`src/`, `data/`)
- README.md, .gitignore, .env.example
- requirements.txt initial
- Git repo initialisé

### ✅ Étape 5 : Page web minimaliste
- Interface web minimaliste (design Option A)
- Template Flask: `templates/index.html`
- Tableau des épisodes (Titre | Durée | Date | Actions)
- Input YouTube URL + bouton Ajouter
- Section RSS avec copie d'URL et lien Pocket Casts
- Status message (succès/erreur)
- Design dark mode CSS vanilla

### ✅ Étape 6 : Sécurité - clé API et protection
- Décorateur `@require_api_key` pour Bearer token
- Routes protégées : `POST /api/episodes`, `DELETE /api/episodes/<id>`
- Routes publiques : `GET /api/episodes`, `GET /feed.rss`
- Configuration via `.env` (API_KEY)
- Retour 401 Unauthorized pour requête invalide

### ✅ Étape 9 : Raccourci iPhone + Bookmarklet Desktop
- **iOS** : Instructions Shortcuts App (menu Partager YouTube)
- **Desktop** : Bookmarklet drag-and-drop pour marque-pages
- Endpoint `/add?url=...&key=...` pour URL handler
- Endpoint `/bookmarklet` : page d'aide avec instructions
- Voir `SHORTCUTS.md` pour instructions détaillées

---

### ⏳ À faire
- **Étape 2** : Backend Flask minimal (SQLite)
- **Étape 3** : Moteur de conversion YouTube → MP3 (yt-dlp + ffmpeg)
- **Étape 4** : Générateur de flux RSS
- **Étape 7** : Dockerisation (Dockerfile + docker-compose.yml)
- **Étape 8** : Déploiement sur serveur + NPM reverse proxy
- **Étape 10** : Tests de bout en bout

---

**Projet** : Convertir YouTube en podcast personnel  
**Roadmap** : [PATHFINDER.md](PATHFINDER.md)
