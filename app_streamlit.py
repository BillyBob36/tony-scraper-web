import streamlit as st
import pandas as pd
import time
import os
from datetime import datetime
import io

# Page configuration
st.set_page_config(
    page_title="Tony Scraper - Interface Web",
    page_icon="🔍",
    layout="wide"
)

st.title("🔍 Tony Scraper - Interface Web")
st.markdown("---")

# Sidebar configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Login credentials
    st.subheader("🔐 Connexion")
    username = st.text_input("Email / Identifiant", type="default")
    password = st.text_input("Mot de passe", type="password")
    
    # Scraping options
    st.subheader("📊 Options de Scraping")
    nb_profiles = st.number_input("Nombre de profils", min_value=1, max_value=100, value=5)
    start_from = st.number_input("Commencer à partir du profil #", min_value=1, value=1)
    
    # Sort options
    sort_option = st.selectbox(
        "Trier par",
        ["Derniers inscrits", "Nom A-Z", "Nom Z-A"]
    )

# Main content
if st.button("🚀 Lancer le Scraping", type="primary"):
    if username and password:
        with st.spinner("🔄 Scraping en cours..."):
            progress_bar = st.progress(0)
            
            # Simulate scraping progress
            for i in range(100):
                time.sleep(0.05)
                progress_bar.progress(i + 1)
            
            # Structure de données optimisée Excel/Google Sheets
            sample_data = {
                'ID': [1, 2, 3],
                'Prénom': ['Flore', 'Emmanuelle', 'Tristan'],
                'Nom': ['DELAPORTE', 'DONADIEU DE LAVIT', 'LAURIN'],
                'Entreprise': ['LES ACTIVES PARIS', 'INOUÏ EDITIONS', 'THE FRANKIE SHOP'],
                'Poste': ['CEO', 'Directrice Marketing', 'Responsable E-commerce'],
                'Email': ['f.delaporte@company.com', 'e.donadieu@company.com', 't.laurin@company.com'],
                'LinkedIn_URL': ['https://linkedin.com/in/flore', 'https://linkedin.com/in/emmanuelle', 'https://linkedin.com/in/tristan'],
                'Téléphone': ['+33 6 12 34 56 78', '+33 6 98 76 54 32', '+33 6 55 44 33 22'],
                'Ville': ['Paris', 'Lyon', 'Paris'],
                'Date_Scraping': [datetime.now().strftime('%d/%m/%Y')] * 3,
                'Source_URL': ['https://le-spot.retail-leaders.fr'] * 3
            }
            
            df = pd.DataFrame(sample_data)
            
            st.success("✅ Scraping terminé avec succès!")
            
            # Display results
            st.subheader("📋 Résultats")
            
            # Affichage du tableau avec en-têtes
            st.dataframe(df, use_container_width=True)
            
            # Statistiques
            st.metric("Nombre de profils", len(df))
            
            # Préparation du fichier Excel optimisé
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Profils_Tony', index=False)
                
                # Ajuster la largeur des colonnes
                worksheet = writer.sheets['Profils_Tony']
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    adjusted_width = min(max_length + 2, 50)
                    worksheet.column_dimensions[column_letter].width = adjusted_width
            
            excel_data = output.getvalue()
            
            # Boutons de téléchargement
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.download_button(
                    label="📊 Télécharger Excel",
                    data=excel_data,
                    file_name=f"tony_scraper_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            
            with col2:
                csv = df.to_csv(index=False, sep=';')
                st.download_button(
                    label="📥 CSV (Google Sheets)",
                    data=csv,
                    file_name=f"tony_scraper_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            
            with col3:
                # Lien Google Sheets
                csv_for_sheets = df.to_csv(index=False)
                st.code(csv_for_sheets, language='csv')
                st.info("📋 Copiez le CSV ci-dessus et collez dans Google Sheets")
    else:
        st.error("⚠️ Veuillez entrer vos identifiants de connexion!")

# Footer
st.markdown("---")
st.markdown("*Développé avec ❤️ pour Tony Scraper*")