#!/usr/bin/env python3
"""
Script Complet pour Tony - Automatisation Le Spot
===============================================

Ce script fusionne toutes les fonctionnalités de connexion et navigation :
1. Connexion complète (email + mot de passe)
2. Navigation vers le catalogue
3. Actions personnalisées sur demande

Usage:
    python scraping_tony_complet.py --action connexion          # Connexion seule
    python scraping_tony_complet.py --action catalogue           # Connexion + Catalogue
    python scraping_tony_complet.py --action custom --target "selector"  # Action personnalisée
"""

import time
import argparse
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class TonyAutomation:
    def __init__(self, headless=False):
        self.email = "tony@metagora.tech"
        self.password = "nOx$$1990!!"
        self.driver = None
        self.wait = None
        self.headless = headless
        
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
            print(f"✅ Email saisi: {self.email}")
            
            # Cliquer sur Valider
            valider_btn = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit'][form='registration-form-login']")))
            valider_btn.click()
            print("✅ Bouton 'Valider' cliqué")
            
            # Attendre la page suivante
            time.sleep(3)
            
            # ÉTAPE 2: Saisir le mot de passe
            password_field = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#login_password")))
            password_field.clear()
            password_field.send_keys(self.password)
            print("✅ Mot de passe saisi")
            
            # Cliquer sur Se connecter
            connecter_btn = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit'][form='registration-form']")))
            connecter_btn.click()
            
            # Attendre la connexion
            print("⏳ Connexion en cours...")
            time.sleep(5)
            
            # Vérifier la connexion
            current_url = self.driver.current_url
            page_title = self.driver.title
            
            if "login" not in current_url.lower():
                print(f"🎉 Connexion réussie!")
                print(f"📍 URL: {current_url}")
                print(f"📄 Titre: {page_title}")
                return True
            else:
                print("❌ Échec de la connexion")
                return False
                
        except Exception as e:
            print(f"❌ Erreur lors de la connexion: {str(e)}")
            return False
    
    def navigation_catalogue(self):
        """Navigue vers le catalogue après connexion"""
        try:
            if not self.connexion_complete():
                return False
                
            print("\n🚀 Navigation vers le Catalogue...")
            
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
                print(f"✅ Navigation réussie!")
                print(f"📍 URL: {current_url}")
                print(f"📄 Titre: {page_title}")
                return True
            else:
                print(f"⚠️ Navigation effectuée - vérifiez la capture")
                return True
                
        except Exception as e:
            print(f"❌ Erreur lors de la navigation: {str(e)}")
            return False
    
    def action_personnalisee(self, selector, action="click", text=None):
        """Exécute une action personnalisée sur un élément"""
        try:
            print(f"🎯 Action personnalisée: {action} sur {selector}")
            
            # Localiser l'élément
            if selector.startswith("#"):
                element = self.wait.until(EC.element_to_be_clickable((By.ID, selector[1:])))
            elif selector.startswith("."):
                element = self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, selector[1:])))
            elif selector.startswith("//"):
                element = self.wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
            else:
                element = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
            
            # Effectuer l'action
            if action == "click":
                element.click()
                print("✅ Clic effectué")
            elif action == "send_keys" and text:
                element.clear()
                element.send_keys(text)
                print(f"✅ Texte saisi: {text}")
            elif action == "get_text":
                text_content = element.text
                print(f"📋 Texte récupéré: {text_content}")
                return text_content
            
            time.sleep(2)
            return True
            
        except Exception as e:
            print(f"❌ Erreur action personnalisée: {str(e)}")
            return False
    
    def sauvegarder_capture(self, nom="capture"):
        """Sauvegarde une capture d'écran"""
        try:
            filename = f"{nom}_{int(time.time())}.png"
            self.driver.save_screenshot(filename)
            print(f"📸 Capture sauvegardée: {filename}")
            return filename
        except Exception as e:
            print(f"❌ Erreur capture: {str(e)}")
            return None
    
    def run(self, action="connexion", selector=None, text=None):
        """Exécute l'action principale"""
        try:
            self.setup_driver()
            
            if action == "connexion":
                success = self.connexion_complete()
            elif action == "catalogue":
                success = self.navigation_catalogue()
            elif action == "custom":
                if not self.connexion_complete():
                    return False
                success = self.action_personnalisee(selector, "send_keys" if text else "click", text)
            else:
                print(f"❌ Action inconnue: {action}")
                return False
            
            if success:
                self.sauvegarder_capture(action)
                
            return success
            
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
    """Fonction principale"""
    parser = argparse.ArgumentParser(description="Automatisation Le Spot pour Tony")
    parser.add_argument("--action", choices=["connexion", "catalogue", "custom"], 
                       default="connexion", help="Action à exécuter")
    parser.add_argument("--target", help="Sélecteur CSS pour action personnalisée")
    parser.add_argument("--text", help="Texte à saisir pour action personnalisée")
    parser.add_argument("--headless", action="store_true", help="Mode sans interface")
    
    args = parser.parse_args()
    
    if args.action == "custom" and not args.target:
        print("❌ --target requis pour l'action 'custom'")
        sys.exit(1)
    
    automation = TonyAutomation(headless=args.headless)
    success = automation.run(args.action, args.target, args.text)
    
    if success:
        print("\n🎉 Script exécuté avec succès!")
    else:
        print("\n❌ Le script a échoué")
        sys.exit(1)

if __name__ == "__main__":
    main()