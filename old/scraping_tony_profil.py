#!/usr/bin/env python3
"""
Script pour Tony - Scraping des profils sur le catalogue
Scrape les profils avec les informations : entreprise, nom/prénom, poste
Utilisation: python scraping_tony_profil.py [nombre_profils]
Exemples:
- python scraping_tony_profil.py 5  # Scrape 5 profils
- python scraping_tony_profil.py 0  # Scrape tous les profils de la page
- python scraping_tony_profil.py    # Scrape 2 profils par défaut
"""

import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class TonyProfilScraper:
    def __init__(self, headless=False, nombre_profils=2):
        self.email = "tony@metagora.tech"
        self.password = "nOx$$1990!!"
        self.driver = None
        self.wait = None
        self.headless = headless
        self.nombre_profils = nombre_profils
        self.profils_data = []
        
    def setup_driver(self):
        """Configure le driver Chrome"""
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        if not self.headless:
            chrome_options.add_argument("--start-maximized")
            
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        service = Service()
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.wait = WebDriverWait(self.driver, 15)
        
    def connexion_complete(self):
        """Exécute la connexion complète"""
        try:
            print("🚀 Connexion en cours...")
            
            # ÉTAPE 1: Page de connexion initiale
            self.driver.get("https://le-spot.retail-leaders.fr/fr/login")
            self.wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
            time.sleep(2)
            
            # Saisir l'email
            email_field = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#email_email")))
            email_field.clear()
            email_field.send_keys(self.email)
            
            # Cliquer sur Valider
            valider_btn = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit'][form='registration-form-login']")))
            valider_btn.click()
            
            # Attendre la page suivante
            time.sleep(3)
            
            # ÉTAPE 2: Saisir le mot de passe
            password_field = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#login_password")))
            password_field.clear()
            password_field.send_keys(self.password)
            
            # Cliquer sur Se connecter
            connecter_btn = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit'][form='registration-form']")))
            connecter_btn.click()
            
            # Attendre la connexion
            print("⏳ Connexion en cours...")
            time.sleep(5)
            
            # Vérifier la connexion
            current_url = self.driver.current_url
            if "login" not in current_url.lower():
                print("🎉 Connexion réussie!")
                return True
            else:
                print("❌ Échec de la connexion")
                return False
                
        except Exception as e:
            print(f"❌ Erreur lors de la connexion: {str(e)}")
            return False
    
    def navigation_catalogue(self):
        """Navigue vers le catalogue"""
        try:
            print("🚀 Navigation vers le Catalogue...")
            
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
            
            # Attendre le chargement du catalogue
            time.sleep(5)
            print("✅ Navigation vers le catalogue réussie!")
            return True
            
        except Exception as e:
            print(f"❌ Erreur lors de la navigation: {str(e)}")
            return False
    
    def scraper_profils(self):
        """Scrape les profils du catalogue avec gestion des erreurs"""
        try:
            print(f"🎯 Scraping des {self.nombre_profils} premiers profils...")
            
            # Attendre que les profils soient chargés
            self.wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
            time.sleep(3)
            
            # Localiser les conteneurs de profils avec plusieurs sélecteurs
            profil_conteneurs = []
            
            # Essayer plusieurs sélecteurs pour les profils
            selecteurs_profils = [
                ".catalog__item",
                ".catalog-item",
                "[class*='catalog'] [class*='item']",
                ".card-profile"
            ]
            
            for selecteur in selecteurs_profils:
                profil_conteneurs = self.driver.find_elements(By.CSS_SELECTOR, selecteur)
                if profil_conteneurs:
                    print(f"✅ Profils trouvés avec le sélecteur: {selecteur}")
                    break
            
            if len(profil_conteneurs) == 0:
                print("❌ Aucun profil trouvé avec aucun sélecteur")
                return False
            
            # Déterminer le nombre de profils à scraper
            if self.nombre_profils == 0:
                nb_a_scraper = len(profil_conteneurs)
                print(f"📊 {len(profil_conteneurs)} profils trouvés, scraping de tous les profils...")
            else:
                nb_a_scraper = min(self.nombre_profils, len(profil_conteneurs))
                print(f"📊 {len(profil_conteneurs)} profils trouvés, scraping des {nb_a_scraper} premiers...")
            
            # Scraper chaque profil
            for index, conteneur in enumerate(profil_conteneurs[:nb_a_scraper]):
                try:
                    print(f"\n📋 Profil #{index + 1}:")
                    
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
                        ".catalog-title",
                        ".catalog__title",
                        ".company-name",
                        "[class*='title']",
                        "[class*='company']"
                    ]
                    entreprise = extraire_texte_avec_selecteurs(selecteurs_entreprise, conteneur, "entreprise")
                    print(f"   🏢 Entreprise: {entreprise}")
                    
                    # Nom et prénom - avec sélecteurs de secours
                    selecteurs_nom = [
                        ".user__infos .name",
                        ".user__name",
                        ".profile-name",
                        "[class*='name']",
                        ".user__infos span:first-child"
                    ]
                    nom_prenom = extraire_texte_avec_selecteurs(selecteurs_nom, conteneur, "nom")
                    print(f"   👤 Nom: {nom_prenom}")
                    
                    # Poste - avec sélecteurs de secours
                    selecteurs_poste = [
                        ".user__infos .job",
                        ".user__job",
                        ".profile-job",
                        "[class*='job']",
                        "[class*='position']",
                        ".user__infos span:last-child"
                    ]
                    poste = extraire_texte_avec_selecteurs(selecteurs_poste, conteneur, "poste")
                    print(f"   💼 Poste: {poste}")
                    
                    # URL du profil complet - avec sélecteurs de secours
                    selecteurs_url = [
                        ".catalog-sheet-more",
                        "[href*='profile']",
                        "[href*='user']",
                        "a[href*='sheet']"
                    ]
                    
                    profil_url = None
                    for selecteur_url in selecteurs_url:
                        try:
                            url_element = conteneur.find_element(By.CSS_SELECTOR, selecteur_url)
                            href = url_element.get_attribute('href')
                            if href:
                                if href.startswith('http'):
                                    profil_url = href
                                else:
                                    profil_url = f"https://le-spot.retail-leaders.fr{href}"
                                break
                        except:
                            continue
                    
                    if not profil_url:
                        profil_url = "Non disponible"
                    
                    print(f"   🔗 URL: {profil_url}")
                    
                    # Avatar URL (si disponible)
                    selecteurs_avatar = [
                        ".user__avatar img",
                        ".profile-avatar img",
                        "[class*='avatar'] img",
                        "img[src*='avatar']"
                    ]
                    
                    avatar_url = None
                    for selecteur_avatar in selecteurs_avatar:
                        try:
                            avatar_img = conteneur.find_element(By.CSS_SELECTOR, selecteur_avatar)
                            avatar_url = avatar_img.get_attribute('src')
                            if avatar_url:
                                break
                        except:
                            continue
                    
                    if avatar_url:
                        print(f"   🖼️  Avatar: {avatar_url}")
                    else:
                        print("   🖼️  Avatar: Non disponible")
                    
                    # Stocker les données
                    profil_data = {
                        "index": index + 1,
                        "entreprise": entreprise,
                        "nom_prenom": nom_prenom,
                        "poste": poste,
                        "url_profil": profil_url,
                        "avatar_url": avatar_url
                    }
                    
                    self.profils_data.append(profil_data)
                    
                except Exception as e:
                    print(f"❌ Erreur lors du scraping du profil #{index + 1}: {str(e)}")
                    # Ajouter quand même avec des valeurs par défaut
                    profil_data = {
                        "index": index + 1,
                        "entreprise": "Erreur extraction",
                        "nom_prenom": "Erreur extraction",
                        "poste": "Erreur extraction",
                        "url_profil": "Erreur extraction",
                        "avatar_url": None
                    }
                    self.profils_data.append(profil_data)
                    continue
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur lors du scraping: {str(e)}")
            return False
    
    def sauvegarder_donnees(self, nom_fichier="profils_tony"):
        """Sauvegarde les données scrapées"""
        try:
            # Sauvegarder en JSON
            json_filename = f"{nom_fichier}.json"
            with open(json_filename, 'w', encoding='utf-8') as f:
                json.dump(self.profils_data, f, ensure_ascii=False, indent=2)
            
            # Sauvegarder en CSV simple
            csv_filename = f"{nom_fichier}.csv"
            with open(csv_filename, 'w', encoding='utf-8') as f:
                f.write("Index;Entreprise;Nom_Prenom;Poste;URL_Profil\n")
                for profil in self.profils_data:
                    f.write(f"{profil['index']};{profil['entreprise']};{profil['nom_prenom']};{profil['poste']};{profil['url_profil']}\n")
            
            print(f"💾 Données sauvegardées:")
            print(f"   📄 JSON: {json_filename}")
            print(f"   📊 CSV: {csv_filename}")
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur lors de la sauvegarde: {str(e)}")
            return False
    
    def sauvegarder_capture(self, nom="capture_catalogue"):
        """Sauvegarde une capture d'écran"""
        try:
            filename = f"{nom}_{int(time.time())}.png"
            self.driver.save_screenshot(filename)
            print(f"📸 Capture sauvegardée: {filename}")
            return filename
        except Exception as e:
            print(f"❌ Erreur capture: {str(e)}")
            return None
    
    def run(self):
        """Exécute le processus complet"""
        try:
            self.setup_driver()
            
            # Afficher le mode d'exécution
            if self.nombre_profils == 0:
                print("🎯 Mode: Scraping de tous les profils de la page")
            else:
                print(f"🎯 Mode: Scraping des {self.nombre_profils} premiers profils")
            
            # Étape 1: Connexion
            if not self.connexion_complete():
                return False
            
            # Étape 2: Navigation vers le catalogue
            if not self.navigation_catalogue():
                return False
            
            # Étape 3: Scraping des profils
            if not self.scraper_profils():
                return False
            
            # Étape 4: Sauvegarde des données
            self.sauvegarder_donnees("profils_tony")
            
            # Étape 5: Capture finale
            self.sauvegarder_capture("catalogue_final")
            
            # Afficher les données scrapées
            print("\n" + "="*50)
            print("📊 RÉSUMÉ DES DONNÉES SCRAPÉES")
            print("="*50)
            
            for profil in self.profils_data:
                print(f"\n🎯 Profil #{profil['index']}")
                print(f"   Entreprise: {profil['entreprise']}")
                print(f"   Nom: {profil['nom_prenom']}")
                print(f"   Poste: {profil['poste']}")
                print(f"   URL: {profil['url_profil']}")
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur générale: {str(e)}")
            return False
            
        finally:
            if self.driver:
                print("\n💡 Le navigateur reste ouvert pour inspection")
                input("Appuyez sur Entrée pour fermer...")
                self.driver.quit()
                print("✅ Navigateur fermé")

def main():
    """Fonction principale avec arguments"""
    import sys
    
    # Gérer les arguments de ligne de commande
    nombre_profils = 2  # Valeur par défaut
    
    if len(sys.argv) > 1:
        try:
            nombre_profils = int(sys.argv[1])
            if nombre_profils < 0:
                print("❌ Le nombre de profils doit être positif ou 0")
                return
        except ValueError:
            print("❌ Usage: python scraping_tony_profil.py [nombre_profils]")
            print("   Exemples:")
            print("   - python scraping_tony_profil.py 5    # 5 profils")
            print("   - python scraping_tony_profil.py 0    # Tous les profils")
            return
    
    print(f"🚀 Lancement du scraping avec {nombre_profils if nombre_profils > 0 else 'tous'} profil(s)")
    
    scraper = TonyProfilScraper(nombre_profils=nombre_profils)
    success = scraper.run()
    
    if success:
        print("\n🎉 Scraping terminé avec succès!")
    else:
        print("\n❌ Le scraping a échoué")

if __name__ == "__main__":
    main()