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

**Projet** : Convertir YouTube en podcast personnel
