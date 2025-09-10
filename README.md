# Scraping Tony - Le Spot Automation

Script unique et complet pour l'automatisation de la connexion et navigation sur le site Le Spot.

## 🚀 Utilisation rapide

### Connexion complète
```bash
python scraping_tony_complet.py --action connexion
```

### Connexion + Navigation vers le catalogue
```bash
python scraping_tony_complet.py --action catalogue
```

### Action personnalisée après connexion
```bash
python scraping_tony_complet.py --action custom --target "#mon_element" --text "valeur"
```

## 📋 Options disponibles

| Option | Description | Valeurs |
|--------|-------------|---------|
| `--action` | Action à exécuter | `connexion`, `catalogue`, `custom` |
| `--target` | Sélecteur CSS (action custom) | `#id`, `.classe`, `tag` |
| `--text` | Texte à saisir (optionnel) | `"mon texte"` |
| `--headless` | Mode sans interface | (flag) |

## 🔧 Sélecteurs CSS courants

- `#email_email` - Champ email
- `#login_password` - Champ mot de passe
- `span.nav-item-icon.icon-Catalogue` - Icône Catalogue
- `button[type='submit']` - Boutons de validation

## 📸 Captures d'écran

Les captures sont automatiquement sauvegardées avec un horodatage :
- `connexion_[timestamp].png`
- `catalogue_[timestamp].png`
- `custom_[timestamp].png`

## ✅ Fonctionnalités

- ✅ Connexion automatique avec Tony@metagora.tech
- ✅ Navigation vers le catalogue
- ✅ Actions personnalisées post-connexion
- ✅ Gestion d'erreurs robuste
- ✅ Captures d'écran automatiques
- ✅ Mode avec/sans interface

## 🎯 Exemples d'utilisation

```bash
# Connexion simple
python scraping_tony_complet.py

# Connexion + catalogue
python scraping_tony_complet.py --action catalogue

# Saisir du texte dans un champ après connexion
python scraping_tony_complet.py --action custom --target "#search_field" --text "recherche"

# Clic sur un bouton spécifique
python scraping_tony_complet.py --action custom --target ".submit-button"

# Mode headless
python scraping_tony_complet.py --action catalogue --headless
```