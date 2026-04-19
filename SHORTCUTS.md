# Raccourcis iPhone & Bookmarklet Desktop

## 🎙 Raccourci iOS (Shortcuts App)

Créez un nouveau raccourci dans l'app Raccourcis Apple qui envoie l'URL YouTube au podcast en 2 taps.

### Étapes de création :

1. **Ouvrir l'app Raccourcis** (pré-installée sur iOS 12+)
2. **Créer un nouveau raccourci** (`+` → "Créer un raccourci")
3. **Ajouter les actions suivantes** :

   ```
   1. Ajouter → "Obtenir le presse-papiers"
      (capture l'URL depuis le share sheet)
   
   2. Ajouter → "URL de demande"
      - URL: https://podcast.bard3.duckdns.org/api/episodes
      - Méthode: POST
      - En-têtes:
         Authorization: Bearer YOUR_API_KEY
         Content-Type: application/json
      - Corps: {"url": [Presse-papiers]}
      - Type de contenu: JSON
   
   3. Ajouter → "Afficher le résultat"
   
   4. Ajouter → "Afficher une alerte"
      Titre: "Ajouté ✓"
      Message: [Résultat de la demande]
   ```

4. **Nommer le raccourci** : "Ajouter au Podcast"
5. **Ajouter au partage** : Touchez les 3 points → "Ajouter au Partage"

### Utilisation :

1. Ouvrez la vidéo YouTube dans Safari/YouTube app
2. Touchez le bouton **Partager**
3. Touchez **"Ajouter au Podcast"**
4. L'URL est envoyée au backend ✓

---

## 📱 Bookmarklet Desktop

Sauvegardez ce code comme un marque-page dans votre navigateur.

### Chrome/Safari/Firefox :

1. **Créer un nouveau marque-page** (Ctrl+D ou Cmd+D)
2. **URL** : copiez le code ci-dessous
3. **Nom** : "Ajouter au Podcast"
4. **Enregistrer**

### Code du bookmarklet :

```javascript
javascript:(function(){
  const url = prompt('URL YouTube:');
  if (!url) return;
  
  fetch('https://podcast.bard3.duckdns.org/api/episodes', {
    method: 'POST',
    headers: {
      'Authorization': 'Bearer YOUR_API_KEY',
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ url })
  })
  .then(r => r.json())
  .then(data => alert('✓ Ajouté au podcast'))
  .catch(e => alert('✗ Erreur: ' + e.message));
})();
```

### Utilisation :

1. Aller sur YouTube ou une vidéo
2. Cliquer le marque-page "Ajouter au Podcast"
3. Coller l'URL → OK
4. Confirmation dans l'alerte ✓

---

## 🔐 Configuration

Remplacez `YOUR_API_KEY` par votre vraie clé API dans les deux raccourcis.

Pour le raccourci iOS, vous pouvez aussi utiliser un URL handler :
```
https://podcast.bard3.duckdns.org/add?url=YOUTUBE_URL&key=YOUR_API_KEY
```
(À implémenter côté backend pour plus de fluidité)
