#!/usr/bin/env python3
"""
Script de scraping détaillé des profils Tony
============================================

Ce script complète les informations des profils en scrapant les pages individuelles.
Il extrait des données détaillées depuis les pages de profil comme :
- Éléments clés (effectifs, chiffre d'affaires, etc.)
- Secteur(s) d'activité
- Mission en une phrase
- Nombre de points de vente
- Solutions/compétences recherchées

Utilisation :
    python scraping_tony_profil_detail.py [nombre_profils]
    
Arguments :
    nombre_profils : Nombre de profils à traiter (0 pour tous, défaut: 2)

Exemples :
    python scraping_tony_profil_detail.py 5     # Traiter 5 profils
    python scraping_tony_profil_detail.py 0     # Tous les profils
    python scraping_tony_profil_detail.py       # 2 profils (défaut)
"""

import json
import csv
import time
import sys
import os
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TonyProfilDetailScraper:
    def __init__(self, nombre_profils=2):
        self.nombre_profils = nombre_profils
        self.driver = None
        self.wait = None
        self.profils_complets = []
        
    def setup_driver(self):
        """Configure le driver Selenium"""
        options = webdriver.ChromeOptions()
        options.add_argument('--window-size=1920,1080')
        # options.add_argument('--headless')  # Commenté pour voir le navigateur
        self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 10)
        
    def load_profils_from_json(self):
        """Charge les profils depuis le fichier JSON"""
        try:
            with open('profils_tony.json', 'r', encoding='utf-8') as f:
                profils = json.load(f)
            logger.info(f"✅ {len(profils)} profils chargés depuis profils_tony.json")
            return profils
        except FileNotFoundError:
            logger.error("❌ Fichier profils_tony.json introuvable")
            return []
        except json.JSONDecodeError:
            logger.error("❌ Erreur de lecture du JSON")
            return []
    
    def extraire_elements_cles(self):
        """Extrait les éléments clés depuis la section dédiée"""
        elements_cles = {}
        
        try:
            # Trouver la section Éléments clés
            section = self.driver.find_element(By.CSS_SELECTOR, "#object-d6fa1ac7 .section__content")
            items = section.find_elements(By.TAG_NAME, "li")
            
            for item in items:
                text = item.text.strip()
                if text.startswith("Effectifs"):
                    elements_cles['effectifs'] = text.replace("Effectifs : ", "")
                elif text.startswith("Chiffre d'affaires"):
                    elements_cles['chiffre_affaires'] = text.replace("Chiffre d'affaires : ", "")
                elif "Transformation digitale" in text or "Retail tech" in text:
                    elements_cles['competences'] = text
                    
        except NoSuchElementException:
            logger.warning("⚠️ Section Éléments clés non trouvée")
            
        return elements_cles
    
    def extraire_secteur_activite(self):
        """Extrait le secteur d'activité"""
        try:
            secteur_element = self.driver.find_element(
                By.CSS_SELECTOR, 
                "#object-Me3f9M9edd .section__content li.highlight"
            )
            return secteur_element.text.strip()
        except NoSuchElementException:
            logger.warning("⚠️ Secteur d'activité non trouvé")
            return None
    
    def extraire_mission(self):
        """Extrait la mission en une phrase"""
        try:
            mission_element = self.driver.find_element(
                By.CSS_SELECTOR,
                "#object-M4561Macb7 .section__content li"
            )
            return mission_element.text.strip()
        except NoSuchElementException:
            logger.warning("⚠️ Mission non trouvée")
            return None
    
    def extraire_nombre_points_vente(self):
        """Extrait le nombre de points de vente"""
        try:
            points_vente_element = self.driver.find_element(
                By.CSS_SELECTOR,
                "#object-M91ceM1169 .section__content li.highlight"
            )
            return points_vente_element.text.strip()
        except NoSuchElementException:
            logger.warning("⚠️ Nombre de points de vente non trouvé")
            return None
    
    def extraire_solutions_competences(self):
        """Extrait les solutions/compétences recherchées"""
        try:
            solutions_element = self.driver.find_element(
                By.CSS_SELECTOR,
                "#object-M184bM50c8 .section__content li.highlight"
            )
            return solutions_element.text.strip()
        except NoSuchElementException:
            logger.warning("⚠️ Solutions/compétences non trouvées")
            return None
    
    def scraper_profil_detail(self, profil_url):
        """Scrape une page de profil individuelle"""
        try:
            logger.info(f"🌐 Accès à : {profil_url}")
            self.driver.get(profil_url)
            
            # Attendre le chargement de la page
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            time.sleep(2)  # Temps supplémentaire pour le chargement dynamique
            
            # Extraire toutes les informations
            details = {
                'url_profil': profil_url,
                'scraped_at': datetime.now().isoformat(),
                'elements_cles': self.extraire_elements_cles(),
                'secteur_activite': self.extraire_secteur_activite(),
                'mission': self.extraire_mission(),
                'nombre_points_vente': self.extraire_nombre_points_vente(),
                'solutions_competences': self.extraire_solutions_competences()
            }
            
            logger.info("✅ Informations détaillées extraites")
            return details
            
        except TimeoutException:
            logger.error(f"❌ Timeout lors du chargement de {profil_url}")
            return None
        except Exception as e:
            logger.error(f"❌ Erreur lors du scraping : {str(e)}")
            return None
    
    def enrichir_profils(self):
        """Enrichit les profils avec les détails"""
        profils_base = self.load_profils_from_json()
        
        if not profils_base:
            return
            
        # Déterminer le nombre de profils à traiter
        if self.nombre_profils == 0:
            profils_a_traiter = profils_base
        else:
            profils_a_traiter = profils_base[:self.nombre_profils]
            
        logger.info(f"🎯 Traitement de {len(profils_a_traiter)} profils")
        
        for index, profil in enumerate(profils_a_traiter, 1):
            nom_prenom = profil.get('nom_prenom', 'Inconnu')
            entreprise = profil.get('entreprise', '')
            logger.info(f"\n📋 Profil {index}/{len(profils_a_traiter)}: {nom_prenom} - {entreprise}")
            
            # Récupérer l'URL du profil
            profil_url = profil.get('url_profil')
            
            if not profil_url:
                logger.warning(f"⚠️ Aucune URL de profil trouvée pour {nom_prenom}")
                continue
                
            # Scraper les détails
            details = self.scraper_profil_detail(profil_url)
            
            if details:
                # Combiner les informations
                profil_complet = {**profil, **details}
                self.profils_complets.append(profil_complet)
                logger.info("✅ Profil enrichi avec succès")
            
            # Pause entre les profils pour éviter le blocage
            time.sleep(1)
    
    def sauvegarder_resultats(self):
        """Sauvegarde les résultats en JSON et CSV"""
        if not self.profils_complets:
            logger.warning("⚠️ Aucun profil à sauvegarder")
            return
            
        timestamp = int(time.time())
        
        # Sauvegarder en JSON
        json_filename = f'profils_tony_complets_{timestamp}.json'
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(self.profils_complets, f, ensure_ascii=False, indent=2)
        logger.info(f"✅ Sauvegardé : {json_filename}")
        
        # Sauvegarder en CSV
        csv_filename = f'profils_tony_complets_{timestamp}.csv'
        if self.profils_complets:
            with open(csv_filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=self.profils_complets[0].keys())
                writer.writeheader()
                writer.writerows(self.profils_complets)
            logger.info(f"✅ Sauvegardé : {csv_filename}")
    
    def run(self):
        """Exécute le scraping complet"""
        try:
            logger.info("🚀 Démarrage du scraping détaillé des profils")
            self.setup_driver()
            
            if self.nombre_profils == 0:
                logger.info("🔄 Mode : tous les profils")
            else:
                logger.info(f"🎯 Mode : {self.nombre_profils} premier(s) profil(s)")
            
            self.enrichir_profils()
            self.sauvegarder_resultats()
            
            logger.info(f"✅ Scraping terminé : {len(self.profils_complets)} profils enrichis")
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'exécution : {str(e)}")
        finally:
            if self.driver:
                self.driver.quit()

def main():
    """Fonction principale avec gestion des arguments"""
    nombre_profils = 2  # Valeur par défaut
    
    if len(sys.argv) > 1:
        try:
            nombre_profils = int(sys.argv[1])
            if nombre_profils < 0:
                print("❌ Le nombre de profils doit être positif ou 0")
                sys.exit(1)
        except ValueError:
            print("❌ L'argument doit être un nombre entier")
            sys.exit(1)
    
    scraper = TonyProfilDetailScraper(nombre_profils)
    scraper.run()

if __name__ == "__main__":
    main()