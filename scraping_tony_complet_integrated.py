#!/usr/bin/env python3
"""
Script de scraping complet intégré - Tony
=========================================

Ce script combine en une seule session :
1. Connexion à l'espace participant
2. Scraping des profils depuis le catalogue
3. Scraping détaillé de chaque page de profil
4. Sauvegarde complète des données

Le script maintient la connexion tout au long du processus et navigue
intelligemment entre la liste et les pages détaillées.

Utilisation :
    python scraping_tony_complet_integrated.py [nombre_profils]
    
Arguments :
    nombre_profils : Nombre de profils à traiter (0 pour tous, défaut: 2)

Exemples :
    python scraping_tony_complet_integrated.py 3    # 3 profils complets
    python scraping_tony_complet_integrated.py 0    # Tous les profils
    python scraping_tony_complet_integrated.py       # 2 profils (défaut)
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
from selenium.webdriver.common.action_chains import ActionChains
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TonyCompletIntegratedScraper:
    def __init__(self):
        self.driver = None
        self.wait = None
        self.profils_complets = []
        self.catalogue_url = "https://le-spot.retail-leaders.fr/fr/sheet/926247/catalog"
        
    def setup_driver(self):
        """Configure le driver Selenium"""
        options = webdriver.ChromeOptions()
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--disable-web-security')
        options.add_argument('--disable-features=VizDisplayCompositor')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--no-sandbox')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        # options.add_argument('--headless')  # Désactivé pour voir le processus
        self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 15)
        
    def connexion_espace_participant(self):
        """Connexion complète avec email et mot de passe"""
        try:
            logger.info("🔐 Connexion en cours...")
            
            # ÉTAPE 1: Page de connexion initiale
            self.driver.get("https://le-spot.retail-leaders.fr/fr/login")
            self.wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
            time.sleep(2)
            
            # Saisir l'email
            email_field = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#email_email")))
            email_field.clear()
            email_field.send_keys("tony@metagora.tech")
            logger.info("✅ Email saisi")
            
            # Cliquer sur Valider
            valider_btn = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit'][form='registration-form-login']")))
            valider_btn.click()
            logger.info("✅ Bouton 'Valider' cliqué")
            
            # Attendre la page suivante
            time.sleep(3)
            
            # ÉTAPE 2: Saisir le mot de passe
            password_field = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#login_password")))
            password_field.clear()
            password_field.send_keys("nOx$$1990!!")
            logger.info("✅ Mot de passe saisi")
            
            # Cliquer sur Se connecter
            connecter_btn = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit'][form='registration-form']")))
            connecter_btn.click()
            
            # Attendre la connexion
            logger.info("⏳ Connexion en cours...")
            time.sleep(5)
            
            # Vérifier la connexion
            current_url = self.driver.current_url
            if "login" not in current_url.lower():
                logger.info("🎉 Connexion réussie!")
                return True
            else:
                logger.error("❌ Échec de la connexion")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erreur lors de la connexion : {str(e)}")
            return False
    
    def scraper_profil_base(self, element_profil):
        """Scrape les informations de base d'un profil avec système de secours"""
        try:
            # Fonction helper pour extraire texte avec sélecteurs de secours
            def extraire_texte_avec_selecteurs(selecteurs, conteneur_parent, nom_champ):
                for selecteur in selecteurs:
                    try:
                        elements = conteneur_parent.find_elements(By.CSS_SELECTOR, selecteur)
                        if elements and elements[0].text.strip():
                            return elements[0].text.strip()
                    except:
                        continue
                return f"Non trouvé ({nom_champ})"

            # Entreprise - avec sélecteurs de secours
            selecteurs_entreprise = [
                ".catalog-company",
                ".catalog__title", 
                ".company-name",
                "[class*='title']",
                "[class*='company']"
            ]
            entreprise = extraire_texte_avec_selecteurs(selecteurs_entreprise, element_profil, "entreprise")

            # Nom et prénom - avec sélecteurs de secours
            selecteurs_nom = [
                ".catalog-name",
                ".user__infos .name",
                ".user__name",
                ".profile-name",
                "[class*='name']"
            ]
            nom_prenom = extraire_texte_avec_selecteurs(selecteurs_nom, element_profil, "nom")

            # Poste - avec sélecteurs de secours
            selecteurs_poste = [
                ".catalog-position",
                ".user__infos .job",
                ".user__job",
                ".profile-job",
                "[class*='job']",
                "[class*='position']"
            ]
            poste = extraire_texte_avec_selecteurs(selecteurs_poste, element_profil, "poste")

            # URL du profil - avec sélecteurs de secours
            selecteurs_url = [
                "a.catalog-link",
                ".catalog-sheet-more",
                "[href*='profile']",
                "[href*='user']",
                "a[href*='sheet']"
            ]

            url_profil = None
            for selecteur_url in selecteurs_url:
                try:
                    url_element = element_profil.find_element(By.CSS_SELECTOR, selecteur_url)
                    href = url_element.get_attribute('href')
                    if href:
                        if href.startswith('http'):
                            url_profil = href
                        else:
                            url_profil = f"https://le-spot.retail-leaders.fr{href}"
                        break
                except:
                    continue

            if not url_profil:
                url_profil = "Non disponible"

            # Avatar - avec sélecteurs de secours
            selecteurs_avatar = [
                ".catalog-avatar img",
                ".user-avatar img",
                "[class*='avatar'] img",
                "img[src*='avatar']"
            ]
            avatar_url = ""
            for selecteur_avatar in selecteurs_avatar:
                try:
                    avatar_elem = element_profil.find_element(By.CSS_SELECTOR, selecteur_avatar)
                    avatar_url = avatar_elem.get_attribute('src')
                    if avatar_url:
                        break
                except:
                    continue

            return {
                'index': len(self.profils_complets) + 1,
                'entreprise': entreprise,
                'nom_prenom': nom_prenom,
                'poste': poste,
                'url_profil': url_profil,
                'avatar_url': avatar_url
            }

        except Exception as e:
            logger.error(f"❌ Erreur lors du scraping du profil base : {str(e)}")
            return None
    
    def extraire_elements_cles(self):
        """Extrait les éléments clés depuis la section dédiée"""
        elements_cles = {}
        
        try:
            # Plusieurs IDs possibles pour la section éléments clés
            selectors = ["#object-d6fa1ac7", "section h2:contains('Éléments clés')"]
            
            for selector in selectors:
                try:
                    section = self.driver.find_element(By.CSS_SELECTOR, f"{selector} .section__content")
                    items = section.find_elements(By.TAG_NAME, "li")
                    
                    for item in items:
                        text = item.text.strip()
                        if text.startswith("Effectifs"):
                            elements_cles['effectifs'] = text.replace("Effectifs : ", "")
                        elif text.startswith("Chiffre d'affaires"):
                            elements_cles['chiffre_affaires'] = text.replace("Chiffre d'affaires : ", "")
                        elif any(keyword in text.lower() for keyword in ['transformation', 'digital', 'retail', 'tech']):
                            elements_cles['competences'] = text
                    break
                except:
                    continue
                    
        except Exception as e:
            logger.warning(f"⚠️ Section Éléments clés non trouvée : {str(e)}")
            
        return elements_cles
    
    def extraire_secteur_activite(self):
        """Extrait le secteur d'activité"""
        try:
            # Recherche flexible de la section secteur
            secteur_selectors = [
                "#object-Me3f9M9edd .section__content li.highlight",
                "h2:contains('SECTEUR') + .section__content li",
                "*[id*='secteur'] .section__content li"
            ]
            
            for selector in secteur_selectors:
                try:
                    element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    return element.text.strip()
                except:
                    continue
                    
        except Exception as e:
            logger.warning(f"⚠️ Secteur d'activité non trouvé : {str(e)}")
            return None
    
    def extraire_mission(self):
        """Extrait la mission en une phrase"""
        try:
            mission_selectors = [
                "#object-M4561Macb7 .section__content li",
                "h2:contains('Ma mission') + .section__content li",
                "*[id*='mission'] .section__content li"
            ]
            
            for selector in mission_selectors:
                try:
                    element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    return element.text.strip()
                except:
                    continue
                    
        except Exception as e:
            logger.warning(f"⚠️ Mission non trouvée : {str(e)}")
            return None
    
    def extraire_nombre_points_vente(self):
        """Extrait le nombre de points de vente"""
        try:
            points_selectors = [
                "#object-M91ceM1169 .section__content li.highlight",
                "h2:contains('points de vente') + .section__content li",
                "*[id*='vente'] .section__content li"
            ]
            
            for selector in points_selectors:
                try:
                    element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    return element.text.strip()
                except:
                    continue
                    
        except Exception as e:
            logger.warning(f"⚠️ Nombre de points de vente non trouvé : {str(e)}")
            return None
    
    def extraire_solutions_competences(self):
        """Extrait les solutions/compétences recherchées"""
        try:
            solutions_selectors = [
                "#object-M184bM50c8 .section__content li.highlight",
                "h2:contains('Solutions') + .section__content li",
                "*[id*='solution'] .section__content li"
            ]
            
            for selector in solutions_selectors:
                try:
                    element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    return element.text.strip()
                except:
                    continue
                    
        except Exception as e:
            logger.warning(f"⚠️ Solutions non trouvées : {str(e)}")
            return None
    
    def scraper_profil_detail(self):
        """Scrape les détails détaillés d'un profil avec récupération de l'URL LinkedIn réelle"""
        details = {}
        try:
            # Attendre que la page soit chargée
            self.wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
            time.sleep(2)
            
            # Extraire toutes les informations détaillées
            details = {
                'elements_cles': self.extraire_elements_cles(),
                'secteur_activite': self.extraire_secteur_activite(),
                'mission': self.extraire_mission(),
                'nombre_points_vente': self.extraire_nombre_points_vente(),
                'solutions_competences': self.extraire_solutions_competences(),
                'scraped_at': datetime.now().isoformat()
            }
            
            # Scraper l'URL LinkedIn avec gestion de redirection
            linkedin_url = ""
            try:
                # Recherche prioritaire du bouton de redirection LinkedIn
                linkedin_button = self.driver.find_element(By.CSS_SELECTOR, "a[href*='forward/'][target='_blank']")
                redirect_url = linkedin_button.get_attribute('href')
                
                if redirect_url:
                    logger.info(f"🔗 Détection du bouton LinkedIn : {redirect_url}")
                    
                    # Ouvrir un onglet temporaire pour suivre la redirection
                    original_window = self.driver.current_window_handle
                    self.driver.execute_script("window.open('');")
                    self.driver.switch_to.window(self.driver.window_handles[-1])
                    
                    try:
                        # Naviguer vers l'URL de redirection
                        self.driver.get(redirect_url)
                        time.sleep(3)  # Attendre la redirection complète
                        
                        # Capturer l'URL finale après redirection
                        final_url = self.driver.current_url
                        
                        # Extraire l'URL LinkedIn réelle même depuis les pages d'authentification
                        linkedin_url = final_url
                        
                        # Si c'est une URL d'authentification LinkedIn, extraire l'URL de redirection
                        if "linkedin.com/authwall" in final_url or "sessionRedirect" in final_url:
                            # Extraire l'URL de redirection depuis les paramètres
                            if "sessionRedirect=" in final_url:
                                import urllib.parse
                                redirect_param = final_url.split("sessionRedirect=")[1]
                                if "%3F" in redirect_param:
                                    redirect_param = redirect_param.split("%3F")[0]
                                linkedin_url = urllib.parse.unquote(redirect_param)
                                logger.info(f"✅ URL LinkedIn extraite depuis authwall : {linkedin_url}")
                            else:
                                logger.info(f"✅ URL LinkedIn détectée : {final_url}")
                        elif "linkedin.com/in/" in final_url:
                            # URL LinkedIn directe - nettoyer les paramètres
                            base_url = final_url.split("?")[0]
                            linkedin_url = base_url
                            logger.info(f"✅ URL LinkedIn finale obtenue : {linkedin_url}")
                        else:
                            logger.warning(f"⚠️ URL non-LinkedIn détectée : {final_url}")
                            linkedin_url = final_url
                            
                    except Exception as e:
                        logger.warning(f"⚠️ Erreur lors de la redirection : {str(e)}")
                        linkedin_url = redirect_url  # Fallback sur l'URL de redirection
                    finally:
                        # Fermer l'onglet temporaire et revenir au profil
                        self.driver.close()
                        self.driver.switch_to.window(original_window)
                        
            except:
                # Fallback : recherche d'un lien LinkedIn direct
                try:
                    linkedin_element = self.driver.find_element(By.CSS_SELECTOR, "a[href*='linkedin.com/in/']")
                    linkedin_url = linkedin_element.get_attribute('href')
                    logger.info(f"✅ Lien LinkedIn direct trouvé : {linkedin_url}")
                except:
                    linkedin_url = ""
                    logger.info("ℹ️ Aucun lien LinkedIn trouvé")
            
            details['linkedin_url'] = linkedin_url
            
            logger.info("✅ Informations détaillées extraites")
            return details
            
        except Exception as e:
            logger.error(f"❌ Erreur lors du scraping détaillé : {str(e)}")
            return {}
    
    def charger_tous_les_profils(self):
        """Clique sur 'Voir plus' jusqu'à charger tous les profils"""
        try:
            logger.info("🔄 Chargement de tous les profils...")
            
            profils_initiaux = 0
            profils_totaux = 0
            pages_chargees = 0
            
            while True:
                # Compter les profils actuellement visibles
                selecteurs_profils = [
                    ".catalog__item",
                    ".catalog-item",
                    "[class*='catalog'] [class*='item']",
                    ".card-profile",
                    ".catalog-card",
                    "[class*='profile-card']"
                ]
                
                profils_actuels = 0
                for selecteur in selecteurs_profils:
                    profils_actuels = len(self.driver.find_elements(By.CSS_SELECTOR, selecteur))
                    if profils_actuels > 0:
                        break
                
                profils_totaux = profils_actuels
                
                # Vérifier si le bouton "Voir plus" existe et est cliquable
                try:
                    bouton_voir_plus = self.wait.until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, ".btn.btn-primary.see-more"))
                    )
                    
                    # Scroller jusqu'au bouton
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", bouton_voir_plus)
                    time.sleep(1)
                    
                    # Cliquer sur le bouton
                    self.driver.execute_script("arguments[0].click();", bouton_voir_plus)
                    pages_chargees += 1
                    
                    # Attendre que de nouveaux profils se chargent
                    logger.info(f"📄 Page {pages_chargees} chargée - {profils_totaux} profils actuellement")
                    time.sleep(3)
                    
                    # Vérifier si de nouveaux profils ont été ajoutés
                    if profils_actuels == profils_initiaux:
                        logger.info("✅ Tous les profils ont été chargés")
                        break
                    
                    profils_initiaux = profils_actuels
                    
                except:
                    logger.info(f"✅ Plus de bouton 'Voir plus' - {profils_totaux} profils au total")
                    break
            
            logger.info(f"🎯 {profils_totaux} profils trouvés au total après {pages_chargees} clics sur 'Voir plus'")
            return profils_totaux
            
        except Exception as e:
            logger.error(f"❌ Erreur lors du chargement des profils : {str(e)}")
            return 0

    

    def demander_parametres_scraping(self):
        """Demande interactivement les paramètres de scraping"""
        try:
            print("\n" + "="*50)
            print("📊 CONFIGURATION DU SCRAPING")
            print("="*50)
            
            # Demander le nombre de profils à scraper
            while True:
                try:
                    nb_profils = input("\n📋 Combien de profils voulez-vous scraper ? (0 = tous) : ").strip()
                    nb_profils = int(nb_profils)
                    if nb_profils >= 0:
                        break
                    else:
                        print("❌ Veuillez entrer un nombre positif ou 0")
                except ValueError:
                    print("❌ Veuillez entrer un nombre valide")
            
            # Demander la position de départ
            while True:
                try:
                    position_depart = input("\n🎯 À partir de quel numéro de profil ? (1 = premier) : ").strip()
                    position_depart = int(position_depart)
                    if position_depart >= 1:
                        break
                    else:
                        print("❌ Veuillez entrer un nombre >= 1")
                except ValueError:
                    print("❌ Veuillez entrer un nombre valide")
            
            print(f"\n✅ Configuration : {nb_profils} profils à partir du n°{position_depart}")
            return nb_profils, position_depart
            
        except KeyboardInterrupt:
            logger.info("🛑 Scraping annulé par l'utilisateur")
            return None, None

    def scraper_profils_catalogue(self):
        """Scrape les profils depuis le catalogue avec chargement complet"""
        try:
            logger.info("🔍 Recherche des profils dans le catalogue...")
            
            # Attendre que la page soit chargée
            self.wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
            time.sleep(3)
            
            # Trier par "Derniers inscrits" - ATTENDRE et cliquer sur le bouton radio
            logger.info("📅 Tri par 'Derniers inscrits'...")
            try:
                # Attendre que le bouton radio soit présent
                radio_derniers = WebDriverWait(self.driver, 15).until(
                    EC.presence_of_element_located((By.ID, "orderBy_2"))
                )
                
                # Vérifier si ce n'est pas déjà sélectionné
                if not radio_derniers.is_selected():
                    # Scroller jusqu'à l'élément avec une marge pour éviter les headers fixes
                    self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", radio_derniers)
                    time.sleep(2)
                    
                    # Cliquer via JavaScript pour éviter les problèmes d'interception
                    self.driver.execute_script("arguments[0].click();", radio_derniers)
                    logger.info("✅ Tri par 'Derniers inscrits' activé")
                    time.sleep(3)  # Attendre le rechargement complet
                else:
                    logger.info("ℹ️ Tri 'Derniers inscrits' déjà activé")
                    
            except TimeoutException:
                logger.warning("⚠️ Bouton 'Derniers inscrits' non trouvé, continuation...")
            except Exception as e:
                logger.warning(f"⚠️ Erreur lors du tri : {str(e)}, continuation...")
            
            # Charger tous les profils en cliquant sur "Voir plus"
            total_profils = self.charger_tous_les_profils()
            if total_profils == 0:
                logger.error("❌ Aucun profil trouvé")
                return False
                
            # Demander les paramètres de scraping
            nb_profils, position_depart = self.demander_parametres_scraping()
            if nb_profils is None or position_depart is None:
                return False
            
            # Localiser les conteneurs de profils après chargement complet
            profil_conteneurs = []
            selecteurs_profils = [
                ".catalog__item",
                ".catalog-item",
                "[class*='catalog'] [class*='item']",
                ".card-profile",
                ".catalog-card",
                "[class*='profile-card']"
            ]
            
            for selecteur in selecteurs_profils:
                profil_conteneurs = self.driver.find_elements(By.CSS_SELECTOR, selecteur)
                if profil_conteneurs:
                    logger.info(f"✅ {len(profil_conteneurs)} profils trouvés avec le sélecteur: {selecteur}")
                    break
            
            if len(profil_conteneurs) == 0:
                logger.error("❌ Aucun profil trouvé avec aucun sélecteur")
                # Sauvegarder une capture pour debug
                self.driver.save_screenshot(f"debug_catalogue_{int(time.time())}.png")
                return False
            
            # Afficher le nombre total de profils disponibles
            total_profils = len(profil_conteneurs)
            print(f"\n📊 Nombre total de profils disponibles : {total_profils}")
            
            # Calculer les indices de début et fin
            index_debut = position_depart - 1  # Convertir en index 0-based
            
            if nb_profils == 0:
                # Prendre tous les profils à partir de la position de départ
                index_fin = total_profils
                logger.info(f"📊 Scraping de tous les profils à partir du n°{position_depart}")
            else:
                # Prendre le nombre demandé ou jusqu'à la fin
                index_fin = min(index_debut + nb_profils, total_profils)
                logger.info(f"📊 Scraping de {nb_profils} profils à partir du n°{position_depart}")
            
            # Vérifier si la plage est valide
            if index_debut >= total_profils:
                logger.error(f"❌ Position de départ {position_depart} supérieure au nombre de profils ({total_profils})")
                return False
            
            # Boucle de scraping
            for index in range(index_debut, index_fin):
                try:
                    # Re-trouver les éléments (DOM peut avoir changé)
                    profil_conteneurs = self.driver.find_elements(By.CSS_SELECTOR, selecteurs_profils[0])
                    profil_element = profil_conteneurs[index]
                    
                    profil_numero = index + 1  # Numéro de profil pour l'affichage
                    
                    # Scraper les infos de base
                    profil_base = self.scraper_profil_base(profil_element)
                    if not profil_base or not profil_base.get('url_profil'):
                        logger.warning(f"⚠️ Profil {profil_numero} ignoré (pas d'URL)")
                        continue
                    
                    total_a_traiter = index_fin - index_debut
                    logger.info(f"\n📋 Profil {profil_numero}/{index_fin}: {profil_base['nom_prenom']} - {profil_base['entreprise']}")
                    
                    # Ouvrir le profil dans un nouvel onglet
                    original_window = self.driver.current_window_handle
                    self.driver.execute_script("window.open('');")
                    self.driver.switch_to.window(self.driver.window_handles[1])
                    
                    # Aller sur la page du profil
                    self.driver.get(profil_base['url_profil'])
                    
                    # Scraper les détails
                    details = self.scraper_profil_detail()
                    
                    # Combiner les informations
                    profil_complet = {**profil_base, **details}
                    self.profils_complets.append(profil_complet)
                    
                    # Fermer l'onglet et revenir au catalogue
                    self.driver.close()
                    self.driver.switch_to.window(original_window)
                    
                    logger.info("✅ Profil complet enrichi")
                    
                    # Pause entre les profils
                    time.sleep(1)
                    
                except Exception as e:
                    logger.error(f"❌ Erreur lors du traitement du profil {index+1}: {str(e)}")
                    # Revenir au catalogue en cas d'erreur
                    if len(self.driver.window_handles) > 1:
                        self.driver.close()
                        self.driver.switch_to.window(self.driver.window_handles[0])
                    continue
            
            logger.info(f"✅ Scraping du catalogue terminé : {len(self.profils_complets)} profils extraits")
            return True
                    
        except Exception as e:
            logger.error(f"❌ Erreur lors du scraping du catalogue : {str(e)}")
            # Sauvegarder une capture pour debug
            self.driver.save_screenshot(f"debug_erreur_{int(time.time())}.png")
            return False
    
    def navigation_catalogue(self):
        """Navigue vers le catalogue après connexion"""
        try:
            logger.info("🚀 Navigation vers le Catalogue...")
            
            # Attendre que la navigation soit chargée
            self.wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
            time.sleep(2)
            
            # Rechercher et cliquer sur l'icône Catalogue
            catalogue_icon = self.wait.until(EC.element_to_be_clickable((
                By.CSS_SELECTOR, 
                "span.nav-item-icon.icon-Catalogue"
            )))
            
            # Trouver l'élément clickable parent
            catalogue_link = catalogue_icon.find_element(
                By.XPATH, 
                ".//ancestor::a[1] | .//ancestor::button[1] | .//parent::div"
            )
            
            # Scroller et cliquer
            self.driver.execute_script("arguments[0].scrollIntoView(true);", catalogue_link)
            time.sleep(1)
            catalogue_link.click()
            
            # Attendre la navigation
            time.sleep(3)
            
            # Vérifier la navigation
            current_url = self.driver.current_url
            page_title = self.driver.title
            
            if "catalog" in current_url.lower():
                logger.info("✅ Navigation vers le catalogue réussie!")
                return True
            else:
                logger.warning(f"⚠️ URL actuelle: {current_url}")
                # Essayer d'accéder directement à l'URL du catalogue
                self.driver.get(self.catalogue_url)
                time.sleep(3)
                return True
                
        except Exception as e:
            logger.error(f"❌ Erreur lors de la navigation vers le catalogue : {str(e)}")
            # Sauvegarder une capture pour debug
            self.driver.save_screenshot(f"debug_navigation_{int(time.time())}.png")
            return False

    def sauvegarder_resultats(self):
        """Sauvegarde les résultats complets"""
        if not self.profils_complets:
            logger.warning("⚠️ Aucun profil à sauvegarder")
            return
            
        timestamp = int(time.time())
        
        # Sauvegarder en JSON
        json_filename = f'profils_tony_complets_integrated_{timestamp}.json'
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(self.profils_complets, f, ensure_ascii=False, indent=2)
        logger.info(f"✅ Sauvegardé : {json_filename}")
        
        # Sauvegarder en CSV
        csv_filename = f'profils_tony_complets_integrated_{timestamp}.csv'
        try:
            with open(csv_filename, 'w', newline='', encoding='utf-8') as f:
                if self.profils_complets:
                    # Obtenir tous les champs possibles
                    all_fields = set()
                    for profil in self.profils_complets:
                        all_fields.update(profil.keys())
                    
                    fieldnames = sorted(list(all_fields))
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(self.profils_complets)
            logger.info(f"✅ Sauvegardé : {csv_filename}")
        except Exception as e:
            logger.error(f"❌ Erreur lors de la sauvegarde CSV : {str(e)}")
    
    def run(self):
        """Exécute le scraping complet"""
        try:
            logger.info("🚀 Démarrage du scraping complet intégré")
            self.setup_driver()
            
            # Connexion
            if not self.connexion_espace_participant():
                logger.error("❌ Impossible de se connecter")
                return
            
            # Navigation vers le catalogue
            if not self.navigation_catalogue():
                logger.error("❌ Impossible d'accéder au catalogue")
                return
            
            # Scraping complet des profils
            if self.scraper_profils_catalogue():
                # Sauvegarde
                self.sauvegarder_resultats()
                logger.info(f"✅ Scraping terminé : {len(self.profils_complets)} profils complets")
            else:
                logger.error("❌ Échec du scraping du catalogue")
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'exécution : {str(e)}")
        finally:
            if self.driver:
                self.driver.quit()

def main():
    """Fonction principale simplifiée"""
    print("🚀 Scraping Tony - Le Spot Automation")
    print("=" * 40)
    print("Ce script va :")
    print("1. Se connecter au site")
    print("2. Naviguer vers le catalogue")
    print("3. Trier par 'Derniers inscrits'")
    print("4. Charger tous les profils")
    print("5. Vous demander quels profils scraper")
    print("=" * 40)
    
    input("\nAppuyez sur Entrée pour commencer...")
    
    scraper = TonyCompletIntegratedScraper()
    scraper.run()

if __name__ == "__main__":
    main()