# Pathfinder — YouTube Podcast

Projet : convertir des vidéos YouTube en MP3 et les servir via un flux RSS lu par Pocket Casts sur iPhone.

Hébergement : Docker sur serveur perso, sous-domaine stable `podcast.bard3.duckdns.org`.
Code : GitHub public (aucun secret committé, `.env` exclu dès le premier commit).

---

## 1. ✅ Squelette du projet + garde-fous GitHub
On crée la structure des dossiers, le `README.md`, le `.gitignore` et le `.env.example`. Objectif : pouvoir pousser sur GitHub en toute sécurité avant même d'écrire du code métier.
- **Tokens estimés :** ~1 500
- **Modèle :** Haiku

## 2. ✅ Backend Flask minimal (endpoints + base SQLite)
On monte l'application Python : les routes de l'API (ajouter une vidéo, lister, supprimer, flux RSS, santé) et la base SQLite qui remplace l'ancien `videos.json`.
- **Tokens estimés :** ~3 000
- **Modèle :** Sonnet

## 3. ✅ Moteur de conversion YouTube → MP3
Le cœur technique : télécharger la vidéo avec yt-dlp, extraire l'audio avec ffmpeg, gérer les blocages YouTube (HTTP 403) via les cookies du navigateur, et faire tourner ça en tâche de fond pour que l'interface ne se fige pas pendant 15 minutes.
- **Tokens estimés :** ~4 000
- **Modèle :** Sonnet

## 4. ✅ Générateur de flux RSS
On construit le fichier XML que Pocket Casts va lire : titre du podcast, liste des épisodes, lien vers chaque MP3. Format standard iTunes/RSS 2.0.
- **Tokens estimés :** ~2 000
- **Modèle :** Sonnet

## 5. ✅ Page web minimaliste
Une interface très simple : un champ pour coller une URL YouTube, la liste des épisodes convertis avec taille et date, un bouton supprimer par ligne, et un bouton pour copier l'URL du flux RSS à coller dans Pocket Casts.
- **Tokens estimés :** ~2 500
- **Modèle :** Haiku

## 6. ✅ Sécurité : clé API et protection des endpoints sensibles
On protège les routes qui ajoutent ou suppriment des vidéos avec une clé secrète (Bearer token). Les routes de lecture (liste, RSS) restent publiques car Pocket Casts doit y accéder.
- **Tokens estimés :** ~1 500
- **Modèle :** Haiku

## 7. ✅ Dockerisation
On écrit le `Dockerfile` et le `docker-compose.yml` pour que le projet se lance en une commande sur le serveur, avec un volume persistant pour la base et les MP3.
- **Tokens estimés :** ~2 000
- **Modèle :** Sonnet

## 8. ✅ Déploiement sur le serveur
On pousse sur le serveur, on configure le reverse proxy NPM avec le sous-domaine `podcast.bard3.duckdns.org` et HTTPS, puis on vérifie que tout répond bien depuis Internet.
- **Tokens estimés :** ~1 500
- **Modèle :** Sonnet

## 9. ✅ Raccourci iPhone pour ajouter en 2 taps
On configure un raccourci iOS (app Raccourcis Apple) qui apparaît dans le menu Partager de YouTube : un tap sur "Partager" → un tap sur le raccourci → la vidéo est envoyée au backend. Bookmarklet équivalent pour le navigateur desktop.
- **Tokens estimés :** ~1 000
- **Modèle :** Haiku

## 10. ✅ Tests de bout en bout et abonnement Pocket Casts
On teste le parcours complet : URL YouTube → MP3 dispo → flux RSS à jour → Pocket Casts s'abonne et lit l'épisode. On ajuste les derniers détails (titre, image de podcast, métadonnées).
- **Tokens estimés :** ~1 500
- **Modèle :** Haiku

## 11. ✅ Retrait de la clé API (usage perso simplifié)
On supprime la protection par Bearer token sur les routes d'ajout/suppression : plus de `prompt()` qui demande la clé sur mobile, plus de `localStorage` qui saute avec Safari iOS ITP. L'app devient utilisable directement sur n'importe quel appareil. Risque résiduel accepté (projet perso, URL non diffusée).
- **Tokens estimés :** ~1 000
- **Modèle :** Haiku

---

**Total estimé :** ~21 500 tokens
**Répartition modèle :** Haiku ~45% · Sonnet ~55% · Opus 0%
