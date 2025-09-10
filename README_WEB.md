# 🌐 Tony Scraper - Version Web

## 📋 Description
Version web du scraper Tony avec interface utilisateur intuitive via Streamlit.

## 🚀 Installation & Lancement

### Option 1: Streamlit Cloud (Gratuit)
1. Fork ce repository sur GitHub
2. Allez sur [share.streamlit.io](https://share.streamlit.io)
3. Connectez votre compte GitHub
4. Sélectionnez le repository et le fichier `app_streamlit.py`
5. Cliquez sur "Deploy"

### Option 2: Local
```bash
# Installation
pip install -r requirements.txt

# Lancement
streamlit run app_streamlit.py
```

## 🔧 Utilisation

1. **Connexion** : Entrez vos identifiants pour le site scrappé
2. **Configuration** : Choisissez le nombre de profils et l'ordre de tri
3. **Lancement** : Cliquez sur "Lancer le Scraping"
4. **Téléchargement** : Récupérez vos résultats en CSV ou JSON

## 🔐 Sécurité
- Les identifiants ne sont pas stockés
- Connexion sécurisée via HTTPS
- Session temporaire uniquement

## 📊 Fonctionnalités
- Interface moderne et responsive
- Progress bar en temps réel
- Téléchargement direct des résultats
- Tri personnalisable
- Support CSV/JSON