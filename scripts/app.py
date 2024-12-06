# Standard library imports
import base64
import os
import tempfile
import zipfile

# Third-party imports
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
import seaborn as sns
import altair as alt
import folium
import json
import geopandas as gpd
from branca.colormap import LinearColormap

# Constants
BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATHS = {
    'images': os.path.join(BASE_PATH, "images"),
    'data': os.path.join(BASE_PATH, "data"),
    'notebooks': os.path.join(BASE_PATH, "notebooks")
}

ASSETS = {
    'logo': os.path.join(PATHS['images'], "logo-vectoriel-le-wagon-removebg-preview.png"),
    'main_data': os.path.join(PATHS['data'], "main.xlsx"),
    'notebook': 'notebooks/visu_dpt.ipynb',
    'jose_gif': os.path.join(PATHS['images'], "jose.gif"),
    'logo_sporteco': os.path.join(PATHS['images'], "logo sporteco.jpeg"),
    'lofo_lfp': os.path.join(PATHS['images'], "lofo-lfp.png"),
    'logo_datagouv': os.path.join(PATHS['images'], "logo-datagouv.png"),
    'logo_insee': os.path.join(PATHS['images'], "logo-insee.jpg"),
    'logo_trasnfermarkt': os.path.join(PATHS['images'], "logo-trasnfermarkt.png"),
    'logo_uefa': os.path.join(PATHS['images'], "logo-uefa.jpeg"),
    'logocurssaf': os.path.join(PATHS['images'], "logocurssaf.png"),
    'logofifa': os.path.join(PATHS['images'], "logofifa.png"),
    'clement': os.path.join(PATHS['images'], "clement.jpeg"),
    'yohann': os.path.join(PATHS['images'], "yohann.jpeg"),
    'louis': os.path.join(PATHS['images'], "Photo Louis Tang pro.jpg"),
    'edriss': os.path.join(PATHS['images'], "edriss.jpeg"),
    'asana': os.path.join(PATHS['images'], "asana.png"),
    'bigquery': os.path.join(PATHS['images'], "bigquery.png"),
    'drive': os.path.join(PATHS['images'], "drive.png"),
    'python': os.path.join(PATHS['images'], "python-removebg-preview.png"),
    'vsc': os.path.join(PATHS['images'], "vsc-removebg-preview.png"),
    'github': os.path.join(PATHS['images'], "github-removebg-preview.png")
}

# Color mappings
REGION_COLORS = {
    'ile de france': 'purple',
    'nouvelle-aquitaine': 'blue',
    'auvergne-rhône-alpes': 'red',
    'bourgogne-franche-comté': 'green',
    'bretagne': 'orange',
    'centre-val de loire': 'brown',
    'grand est': 'pink',
    'hauts-de-france': 'gray',
    'normandie': 'cyan',
    'occitanie': 'magenta',
    'pays de la loire': 'yellow',
    "provence-alpes-côte d'azur": 'lime'
}

# Load CSS from file
def load_css():
    """Load custom CSS styles from file, create if not exists."""
    css_file = os.path.join(PATHS['images'], 'style.css')
    try:
        with open(css_file) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning(f"Le fichier CSS n'a pas été trouvé : {css_file}")
        st.info("Création du fichier CSS avec les styles par défaut...")
        os.makedirs(os.path.dirname(css_file), exist_ok=True)
        with open(css_file, 'w') as f:
            f.write("""/* Styles généraux */
.stApp {
    max-width: 100%;
    background-color: #f8f9fa;
}

/* En-tête moderne */
.header-container {
    background: linear-gradient(135deg, #1e3d59 0%, #17a2b8 100%);
    padding: 2rem;
    border-radius: 0 0 30px 30px;
    margin: -6rem -4rem 2rem -4rem;
    box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    position: relative;
    z-index: 1000;
}

.title-container {
    background: rgba(255,255,255,0.1);
    backdrop-filter: blur(10px);
    border-radius: 20px;
    padding: 2rem;
    margin: 1rem 0;
    border: 1px solid rgba(255,255,255,0.2);
}

.header-title {
    color: white !important;
    font-size: 3.5rem !important;
    font-weight: 700 !important;
    text-align: center;
    margin: 0;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
}

.header-subtitle {
    color: rgba(255,255,255,0.9) !important;
    font-size: 1.5rem !important;
    font-weight: 400 !important;
    text-align: center;
    margin-top: 1rem !important;
}

/* Conteneur principal */
.main-content {
    padding: 0 2rem;
}

/* Graphiques */
.js-plotly-plot, .stPlotlyChart {
    width: 100% !important;
    margin: 1rem 0;
    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    border-radius: 15px;
    padding: 15px;
    background: white;
}

/* Team member styles */
.team-member {
    text-align: center;
    padding: 1rem;
    background: white;
    border-radius: 15px;
    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    transition: transform 0.3s ease;
}

.team-member:hover {
    transform: translateY(-5px);
}

.team-name {
    margin-top: 1rem;
    font-weight: 600;
    color: #1e3d59;
}""")
        # Charger les styles nouvellement créés
        with open(css_file) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

@st.cache
def load_and_prepare_data():
    """Load and prepare the main dataset with error handling."""
    try:
        df = pd.read_excel(ASSETS['main_data'])
        df.columns = df.columns.str.lower()
        for col in ['region', 'ville']:
            if col in df.columns:
                df[col] = df[col].str.lower()
        return df
    except Exception as e:
        st.error(f"Erreur lors du chargement des données : {str(e)}")
        return None

@st.cache
def create_filtered_data(df, saison="Toutes", region="Toutes", ville="Toutes"):
    """Create filtered dataframe based on user selections."""
    if df is None:
        return None

    df_filtered = df.copy()

    filters = {
        'saison': (saison, lambda x: x == saison),
        'region': (region, lambda x: x == region.lower()),
        'ville': (ville, lambda x: x == ville.lower())
    }

    for col, (value, condition) in filters.items():
        if value != "Toutes" and col in df_filtered.columns:
            df_filtered = df_filtered[df_filtered[col].apply(condition)]

    return df_filtered

def center_text(text, size=1):
    """Centers text with specified heading size."""
    st.markdown(f"<h{size} style='text-align: center;'>{text}</h{size}>", unsafe_allow_html=True)

# Display the main application layout
st.set_page_config(
    page_title="Drwatobut",
    page_icon=ASSETS['logo_sporteco'],
    layout="wide",
    initial_sidebar_state="expanded"
)

load_css()

# Wrap all content in a main-content div
st.markdown('<div class="main-content">', unsafe_allow_html=True)

# En-tête moderne
st.markdown("""
    <div class="header-container">
        <div style="display: flex; align-items: center; justify-content: space-between;">
            <div class="logo-container" style="flex: 1;">
                <img src="data:image/gif;base64,{}" style="width: 100%; border-radius: 10px;">
            </div>
            <div class="title-container" style="flex: 3; margin: 0 2rem;">
                <h1 class="header-title">Drwatobut</h1>
                <h2 class="header-subtitle">Sport et économie : un duo gagnant pour nos villes !</h2>
            </div>
            <div class="logo-container" style="flex: 1;">
                <img src="data:image/png;base64,{}" style="width: 100%; border-radius: 10px;">
            </div>
        </div>
    </div>
""".format(
    base64.b64encode(open(ASSETS['jose_gif'], "rb").read()).decode(),
    base64.b64encode(open(ASSETS['logo'], "rb").read()).decode()
), unsafe_allow_html=True)

# Main tabs
tab1, tab2, tab3 = st.tabs(["🗺️ Accueil", "📈 Nos Analyses", "🎯 Nos Suggestions"])

# Vue Générale tab
with tab1:
    # Création des sous-onglets
    orga_tab, info_tab = st.tabs(["Vue générale", "Infos Supplémentaires"])

    with orga_tab:
        # Ajout du titre principal
        st.markdown("<h2 style='text-align: center;'>Les performances sportives impactent-elles l'économie d'une ville ?</h2>", unsafe_allow_html=True)

        # Création de la pyramide inversée
        fig = go.Figure()

        # Définition des niveaux et des valeurs
        levels = ['France', 'Région', 'Département', 'Votre choix']
        values = [100, 75, 50, 25]

        # Création du graphique en entonnoir
        fig.add_trace(go.Funnel(
            name='Pyramide',
            y=levels,
            x=values,
            textinfo="label",
            textposition="inside",
            textfont=dict(
                color=['white', 'white', 'white', 'white'],  # Tous les niveaux en blanc
                size=20  # Augmentation de la taille du texte
            ),
            marker=dict(
                color=['#ADD8E6', '#6495ED', '#4169E1', '#00008B']  # Dégradé de bleu clair à bleu foncé
            )
        ))

        # Mise en page
        fig.update_layout(
            showlegend=False,
            margin=dict(l=20, r=20, t=20, b=20),
            funnelmode="stack",
            height=500,
            yaxis=dict(showticklabels=False),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )

        # Afficher le graphique
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

        st.markdown("<br>", unsafe_allow_html=True)  # Ajouter un espace

        # Création des conteneurs pour les scores
        score_sportif, score_economique = st.columns(2)

        # Style CSS pour les bulles
        st.markdown("""
        <style>
        .sport-container, .eco-container {
            display: flex;
            gap: 30px;
            margin-top: 20px;
            margin-bottom: 40px;
        }
        .eco-container {
            margin-left: 40px;
            position: relative;
        }
        div.eco-container::before {
            content: '';
            position: absolute;
            left: -20px;
            top: 0;
            height: 100%;
            width: 2px;
            background-color: var(--text-color, #262730) !important;
        }
        .sport-list, .criteria-list, .geo-list {
            background: #f0f2f6;
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            min-width: 200px;
        }
        .sport-item, .eco-item {
            background: white;
            margin: 10px 0;
            padding: 10px 15px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
            transition: transform 0.2s;
        }
        .sport-item:hover, .eco-item:hover {
            transform: translateX(5px);
        }
        .criteria-item {
            background: white;
            margin: 8px 0;
            padding: 8px 15px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        }
        .sub-criteria {
            margin-left: 20px;
            font-size: 0.95em;
            color: #444;
        }
        .title {
            font-weight: bold;
            color: #262730;
            margin-bottom: 15px;
        }
        </style>
        """, unsafe_allow_html=True)

        with score_sportif:
            center_text("Score Sportif", 3)
            st.markdown("""
            <div class="sport-container">
                <div class="sport-list">
                    <div class="title">5 sports collectifs</div>
                    <div class="sport-item">⚽ Football</div>
                    <div class="sport-item">🏉 Rugby</div>
                    <div class="sport-item">🏀 Basketball</div>
                    <div class="sport-item">🤾 Handball</div>
                    <div class="sport-item">🏑 Hockey</div>
                </div>
                <div class="criteria-list">
                    <div class="title">Critères d'évaluation</div>
                    <div class="criteria-item">
                        🏆 Performance Sportive
                        <div class="sub-criteria">• Classement</div>
                        <div class="sub-criteria">• Division</div>
                        <div class="sub-criteria">• Parcours européen</div>
                    </div>
                    <div class="criteria-item">👥 Affluence (foot uniquement)</div>
                    <div class="criteria-item">💰 Données économique de clubs (Foot uniquement)</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with score_economique:
            center_text("Score Économique", 3)
            st.markdown("""
            <div class="eco-container">
                <div class="geo-list">
                    <div class="title">Base Géographique</div>
                    <div class="eco-item">🏙️ Ville</div>
                    <div class="eco-item">🏛️ Département</div>
                    <div class="eco-item">🗺️ Région</div>
                </div>
                <div class="criteria-list">
                    <div class="title">📊 Indicateurs économiques</div>
                    <div class="criteria-item">
                        Taux de chômage
                    </div>
                    <div class="criteria-item">
                        Salaire Median
                    </div>
                    <div class="criteria-item">
                        Nombre de création d'entreprises
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Ajout d'espace avant la section "Nos Sources"
        st.markdown("<div style='margin-top: 40px;'></div>", unsafe_allow_html=True)

        # Ajout de la section "Nos Sources"
        center_text("Nos Sources", 3)

        # Container pour centrer le contenu
        container = st.container()
        with container:
            # Première ligne de logos
            _, col1, col2, col3, col4, _ = st.columns([0.5, 1, 1, 1, 1, 0.5])
            with col1:
                st.image(ASSETS['lofo_lfp'], width=100)
            with col2:
                st.image(ASSETS['logo_datagouv'], width=100)
            with col3:
                st.image(ASSETS['logo_insee'], width=100)
            with col4:
                st.image(ASSETS['logo_trasnfermarkt'], width=100)

            # Espacement
            st.markdown("<br>", unsafe_allow_html=True)

            # Deuxième ligne de logos avec colonnes centrées
            _, col1, col2, col3, _ = st.columns([0.5, 1, 1, 1, 0.5])
            with col1:
                st.image(ASSETS['logo_uefa'], width=100)
            with col2:
                st.image(ASSETS['logocurssaf'], width=100)
            with col3:
                st.image(ASSETS['logofifa'], width=100)

        # Notre équipe
        st.markdown("---")
        st.markdown("<h3 style='text-align: center;'>Notre équipe</h3>", unsafe_allow_html=True)

        # Créer le HTML pour tous les membres en une seule fois
        team_html = f'''
        <div class="team-section">
            <div class="team-container">
                <div class="team-member">
                    <img src="data:image/jpeg;base64,{base64.b64encode(open(ASSETS['clement'], "rb").read()).decode()}"/>
                    <div class="team-name">Clément ROSSI</div>
                </div>
                <div class="team-member">
                    <img src="data:image/jpeg;base64,{base64.b64encode(open(ASSETS['yohann'], "rb").read()).decode()}"/>
                    <div class="team-name">Yohann CEBALS</div>
                </div>
                <div class="team-member">
                    <img src="data:image/jpeg;base64,{base64.b64encode(open(ASSETS['louis'], "rb").read()).decode()}"/>
                    <div class="team-name">Louis TANG</div>
                </div>
                <div class="team-member">
                    <img src="data:image/jpeg;base64,{base64.b64encode(open(ASSETS['edriss'], "rb").read()).decode()}"/>
                    <div class="team-name">Edriss BEN JEMAA</div>
                </div>
            </div>
        </div>
        '''

        st.markdown(team_html, unsafe_allow_html=True)

    with info_tab:
        st.markdown("<h3 style='text-align: center;'>Notre organisation</h3>", unsafe_allow_html=True)

        # First row of images
        _, col1, col2, col3, _ = st.columns([0.5, 1, 1, 1, 0.5])

        with col1:
            st.image(ASSETS['asana'], caption="Asana", use_column_width=True)
        with col2:
            st.image(ASSETS['bigquery'], caption="BigQuery", use_column_width=True)
        with col3:
            st.image(ASSETS['drive'], caption="Drive", use_column_width=True)

        # Add some spacing between rows
        st.markdown("<br>", unsafe_allow_html=True)

        # Second row of images
        _, col4, col5, col6, _ = st.columns([0.5, 1, 1, 1, 0.5])

        with col4:
            st.image(ASSETS['python'], use_column_width=True)
            st.markdown("<p style='text-align: center;'>Python</p>", unsafe_allow_html=True)
        with col5:
            st.image(ASSETS['vsc'], use_column_width=True)
            st.markdown("<p style='text-align: center;'>Visual Studio Code</p>", unsafe_allow_html=True)
        with col6:
            st.image(ASSETS['github'], use_column_width=True)
            st.markdown("<p style='text-align: center;'>GitHub</p>", unsafe_allow_html=True)

        # Ajout d'un séparateur
        st.markdown("---")

        # Lecture du fichier zip
        zip_path = os.path.join(PATHS['data'], "Scores-final.zip")
        try:
            # Créer un dossier temporaire pour extraire les fichiers
            with tempfile.TemporaryDirectory() as temp_dir:
                # Extraire les fichiers du zip
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(temp_dir)

                # Chemin vers le dossier Scores
                scores_dir = os.path.join(temp_dir, "Scores")

                # Trouver tous les fichiers Excel dans le dossier Scores
                excel_files = [f for f in os.listdir(scores_dir) if f.endswith(('.xlsx', '.xls'))]

                if not excel_files:
                    st.error("Aucun fichier Excel trouvé dans le dossier Scores")
                else:
                    # Créer un sélecteur pour les fichiers Excel
                    selected_file = st.selectbox("Sélectionner un fichier:", excel_files)

                    # Lire le fichier Excel sélectionné
                    excel_path = os.path.join(scores_dir, selected_file)
                    with pd.ExcelFile(excel_path) as xlsx:
                        sheet_names = xlsx.sheet_names

                        # Créer un sélecteur pour les feuilles
                        selected_sheet = st.selectbox("Sélectionner une feuille:", sheet_names)

                        # Afficher le tableau sélectionné
                        df_selected = pd.read_excel(excel_path, sheet_name=selected_sheet)
                        st.write(df_selected)

        except FileNotFoundError:
            st.error(f"Le fichier zip n'a pas été trouvé à l'emplacement : {zip_path}")
        except zipfile.BadZipFile:
            st.error("Le fichier zip est corrompu ou n'est pas un fichier zip valide")
        except Exception as e:
            st.error(f"Erreur lors de la lecture du fichier : {str(e)}")

# Nos Analyses tab
with tab2:
    main_tab, sub_tab2, sub_tab1 = st.tabs(["Les coefficients", "Emplacement", "Secteur"])

    # Load the correct data
    with zipfile.ZipFile(os.path.join(PATHS['data'], "Scores-final.zip")) as z:
        with z.open("Scores/scores.xlsx") as f:
            df_scores = pd.read_excel(f)
            # Convertir les scores en nombres avant l'agrégation
            df_scores['score_sportif'] = pd.to_numeric(df_scores['score_sportif'], errors='coerce')
            df_scores['score_economique'] = pd.to_numeric(df_scores['score_economique'], errors='coerce')

            # Grouper par région pour df_region
            df_region = df_scores.groupby(['region', 'annee']).agg({
                'score_sportif': 'mean',
                'score_economique': 'mean'
            }).reset_index()

            # Grouper par département pour df_dept
            df_dept = df_scores.groupby(['departement', 'annee']).agg({
                'score_sportif': 'mean',
                'score_economique': 'mean'
            }).reset_index()

            # Grouper par ville pour df_city
            df_city = df_scores.groupby(['ville', 'annee']).agg({
                'score_sportif': 'mean',
                'score_economique': 'mean'
            }).reset_index()

    # Clean the data - just convert annee to int, scores are already numeric
    df_region['annee'] = df_region['annee'].apply(lambda x: int(''.join(filter(str.isdigit, str(x)))))
    df_dept['annee'] = df_dept['annee'].apply(lambda x: int(''.join(filter(str.isdigit, str(x)))))

    with main_tab:
        st.markdown("<h3 style='text-align: center;'>Analyse de coefficients</h3>", unsafe_allow_html=True)

        # Sélecteur de granularité
        granularity = st.selectbox(
            'Sélectionnez une granularité',
            ['Région', 'Département', 'Ville'],
            index=0
        )

        # Préparation des données selon la granularité
        if granularity == 'Région':
            df_analysis = df_region
            df_raw = df_scores
            group_by_col = 'region'
        elif granularity == 'Département':
            df_analysis = df_dept
            df_raw = df_scores
            group_by_col = 'departement'
        else:  # Ville
            df_analysis = df_city
            df_raw = df_scores
            group_by_col = 'ville'

        # Calcul des scores
        current_year = df_analysis['annee'].max()
        current_data = df_analysis[df_analysis['annee'] == current_year]
        current_raw_data = df_raw[df_raw['annee'] == current_year]

        mean_eco = current_data['score_economique'].mean()
        mean_sport = current_data['score_sportif'].mean()

        # Utiliser les données brutes pour les tops
        top_eco = current_raw_data.nlargest(1, 'score_economique')
        top_sport = current_raw_data.nlargest(1, 'score_sportif')

        # Affichage des score cards
        col1, col2, col3, col4 = st.columns(4)

        card_style = """
        <div style="
            padding: 20px;
            border-radius: 10px;
            background-color: white;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            text-align: center;
            margin: 10px;
        ">
            <h4 style="color: #666;">{}</h4>
            <h2 style="color: #343a40;">{:.2f}</h2>
            <p style="color: #666; font-size: 0.9em;">{}</p>
        </div>
        """

        with col1:
            st.markdown(card_style.format(
                "Moyenne Score Économique",
                mean_eco,
                f"Moyenne {granularity.lower()}s"
            ), unsafe_allow_html=True)
        with col2:
            st.markdown(card_style.format(
                "Moyenne Score Sportif",
                mean_sport,
                f"Moyenne {granularity.lower()}s"
            ), unsafe_allow_html=True)
        with col3:
            st.markdown(card_style.format(
                "Top 1 Score Économique",
                float(top_eco['score_economique'].iloc[0]),
                f"{top_eco[group_by_col].iloc[0]}"
            ), unsafe_allow_html=True)
        with col4:
            st.markdown(card_style.format(
                "Top 1 Score Sportif",
                float(top_sport['score_sportif'].iloc[0]),
                f"{top_sport[group_by_col].iloc[0]}"
            ), unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)  # Add some spacing

        # Evolution des scores par région au cours du temps
        st.subheader("Evolution des scores par région au cours du temps")

        # Sélecteur de région
        regions = sorted(df_region['region'].unique())
        selected_region = st.selectbox('Sélectionnez une région', regions)

        # Filtrer les données pour la région sélectionnée
        df_region_filtered = df_region[df_region['region'] == selected_region]
        df_region_filtered = df_region_filtered.sort_values('annee')

        fig_region = go.Figure()
        fig_region.add_trace(go.Scatter(x=df_region_filtered["annee"], y=df_region_filtered["score_sportif"],
                                      mode='lines+markers', name='Score Sportif',
                                      line=dict(color='blue')))
        fig_region.add_trace(go.Scatter(x=df_region_filtered["annee"], y=df_region_filtered["score_economique"],
                                      mode='lines+markers', name='Score Économique',
                                      line=dict(color='red')))
        fig_region.update_layout(
            title=f"Evolution des scores pour la région {selected_region}",
            xaxis_title="Année",
            yaxis_title="Score",
            showlegend=True,
            height=500,
            margin=dict(l=20, r=20, t=40, b=20),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_region, use_container_width=True, config={'displayModeBar': False})

        # Afficher les clubs de la région sélectionnée
        df_clubs_region = pd.read_excel(os.path.join(PATHS['data'], "score_sport.xlsx"), sheet_name="concat_sports")

        # Mapping des sports pour normalisation
        sport_mapping = {
            'basket': 'Basketball',
            'football': 'Football',
            'handball': 'Handball',
            'hockey': 'Hockey',
            'rugby': 'Rugby'
        }

        # Normaliser les sports uniquement
        df_clubs_region['sport'] = df_clubs_region['sport'].map(sport_mapping)

        # Filtrer les clubs de la région sélectionnée (utiliser le nom exact de la région)
        df_clubs_region = df_clubs_region[df_clubs_region['region'] == selected_region]
        clubs_region = df_clubs_region[['club', 'sport']].drop_duplicates().sort_values(['sport', 'club'])

        st.markdown("---")  # Ajout d'une ligne de séparation
        st.write(f"### Clubs de la région ({len(clubs_region)})")

        # Créer des colonnes pour chaque sport
        sports = sorted(clubs_region['sport'].unique())
        if sports:  # Vérifier qu'il y a des sports à afficher
            cols = st.columns(len(sports))
            for idx, sport in enumerate(sports):
                with cols[idx]:
                    clubs_in_sport = clubs_region[clubs_region['sport'] == sport]
                    clubs_count = len(clubs_in_sport)
                    st.markdown(f"**{sport.capitalize()} ({clubs_count})**")
                    for club in sorted(clubs_in_sport['club']):
                        st.write(f"• {club}")

        # Evolution des scores par département au cours du temps
        st.subheader("Evolution des scores par département au cours du temps")

        # Sélecteur de département
        departements = sorted(df_dept['departement'].unique())
        selected_dept = st.selectbox('Sélectionnez un département', departements)

        # Filtrer les données pour le département sélectionné
        df_dept_filtered = df_dept[df_dept['departement'] == selected_dept]
        df_dept_filtered = df_dept_filtered.sort_values('annee')

        fig_dept = go.Figure()
        fig_dept.add_trace(go.Scatter(x=df_dept_filtered["annee"], y=df_dept_filtered["score_sportif"],
                                    mode='lines+markers', name='Score Sportif',
                                    line=dict(color='blue')))
        fig_dept.add_trace(go.Scatter(x=df_dept_filtered["annee"], y=df_dept_filtered["score_economique"],
                                    mode='lines+markers', name='Score Économique',
                                    line=dict(color='red')))
        fig_dept.update_layout(
            title=f"Evolution des scores pour le département {selected_dept}",
            xaxis_title="Année",
            yaxis_title="Score",
            showlegend=True,
            height=500,
            margin=dict(l=20, r=20, t=40, b=20),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_dept, use_container_width=True, config={'displayModeBar': False})

        st.markdown("---")  # Ajout d'une ligne de séparation

        # Evolution des scores par commune au cours du temps
        st.subheader("Evolution des scores par commune au cours du temps")

        # Sélecteur de commune
        villes = sorted(df_city['ville'].unique())
        selected_ville = st.selectbox('Sélectionnez une ville', villes, key='ville_selector')

        # Filtrer les données pour la ville sélectionnée
        df_ville_filtered = df_city[df_city['ville'] == selected_ville]
        df_ville_filtered = df_ville_filtered.sort_values('annee')

        fig_ville = go.Figure()
        fig_ville.add_trace(go.Scatter(x=df_ville_filtered["annee"], y=df_ville_filtered["score_sportif"],
                                     mode='lines+markers', name='Score Sportif',
                                     line=dict(color='blue')))
        fig_ville.add_trace(go.Scatter(x=df_ville_filtered["annee"], y=df_ville_filtered["score_economique"],
                                     mode='lines+markers', name='Score Économique',
                                     line=dict(color='red')))
        fig_ville.update_layout(
            title=f"Evolution des scores pour la ville de {selected_ville}",
            xaxis_title="Année",
            yaxis_title="Score",
            showlegend=True,
            height=500,
            margin=dict(l=20, r=20, t=40, b=20),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_ville, use_container_width=True, config={'displayModeBar': False})

    with sub_tab2:
        st.markdown("<h3 style='text-align: center;'>Carte des corrélations par département</h3>", unsafe_allow_html=True)

        # Charger les données de corrélation
        df_corr = pd.read_csv(os.path.join(PATHS['data'], "corr_dpt.csv"))

        # Convertir la colonne correlation_departement en float (remplacer la virgule par un point)
        df_corr['correlation_departement'] = df_corr['correlation_departement'].str.replace(',', '.').astype(float)

        # Charger le GeoJSON des départements français
        geojson_path = os.path.join(PATHS['data'], "departements.geojson")

        try:
            with open(geojson_path, 'r') as f:
                departements = json.load(f)

            # Créer la carte choroplèthe
            fig_map = go.Figure(go.Choroplethmapbox(
                geojson=departements,
                locations=df_corr['departement'],
                z=df_corr['correlation_departement'],
                colorscale=[[0, 'rgb(255,255,255)'], [1, 'rgb(0,0,139)']],  # De blanc à bleu foncé
                zmin=-1,
                zmax=1,
                marker_opacity=0.7,
                marker_line_width=0.5,
                colorbar_title="Corrélation",
                featureidkey="properties.nom"
            ))

            # Mise à jour du layout
            fig_map.update_layout(
                mapbox_style="carto-positron",
                mapbox=dict(
                    center=dict(lat=46.5, lon=2.5),
                    zoom=4.5
                ),
                height=600,
                margin={"r":0,"t":0,"l":0,"b":0}
            )

            # Afficher la carte
            st.plotly_chart(fig_map, use_container_width=True)

        except FileNotFoundError:
            st.error("Le fichier GeoJSON des départements n'a pas été trouvé. Veuillez vérifier le chemin du fichier.")
        except Exception as e:
            st.error(f"Une erreur s'est produite lors de la création de la carte : {str(e)}")

        # st.markdown("<h1 style='text-align: center; font-size: 2.5em;'>No spoil, map is comming...</h1>", unsafe_allow_html=True)

    with sub_tab1:
        st.markdown("<h3 style='text-align: center;'>Analyse sectorielle</h3>", unsafe_allow_html=True)

        try:
            # Utilisation de @st.cache pour mettre en cache le chargement des données
            @st.cache(allow_output_mutation=True)
            def load_sector_data():
                df = pd.read_csv(os.path.join(PATHS['data'], "df_filtered_secteurs_88.csv"),
                               dtype={
                                   'code_postal': 'category',
                                   'region': 'category',
                                   'departement': 'category',
                                   'zone': 'category',
                                   'grand_secteur_d_activite': 'category',
                                   'secteur_na17': 'category',
                                   'secteur_na38': 'category',
                                   'secteur_na88': 'category',
                                   'année': 'int32',
                                   'nb_effectif': 'float32',
                                   'nb_effectif_total': 'float32',
                                   'nb_entreprise': 'float32',
                                   'nb_entreprise_total': 'float32'
                               },
                               low_memory=False)

                if 'score_sectoriel' not in df.columns:
                    df["part_effectif"] = (df["nb_effectif"] / df["nb_effectif_total"] * 100).round(2)
                    df["part_entreprise"] = (df["nb_entreprise"] / df["nb_entreprise_total"] * 100).round(2)
                    df['score_sectoriel'] = (0.5 * df['part_effectif'] + 0.5 * df['part_entreprise'])
                    min_score = df['score_sectoriel'].min()
                    max_score = df['score_sectoriel'].max()
                    df['score_sectoriel'] = (df['score_sectoriel'] - min_score) / (max_score - min_score)

                return df

            # Chargement des données avec cache
            df_sector = load_sector_data()

            # Fonction pour obtenir les valeurs uniques
            @st.cache(allow_output_mutation=True)
            def get_unique_values(df, column):
                return sorted(df[column].unique())

            # Filtres interactifs optimisés
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                regions = get_unique_values(df_sector, 'region')
                selected_region = st.selectbox('Région:', ['Toutes les régions'] + regions)

            # Filtrage optimisé des départements
            if selected_region != 'Toutes les régions':
                dept_mask = df_sector['region'] == selected_region
                dept_options = sorted(df_sector[dept_mask]['departement'].unique())
            else:
                dept_options = get_unique_values(df_sector, 'departement')

            with col2:
                selected_dept = st.selectbox('Département:', ['Tous les départements'] + dept_options)

            # Filtrage optimisé des zones
            if selected_dept != 'Tous les départements':
                zone_mask = df_sector['departement'] == selected_dept
                zone_options = sorted(df_sector[zone_mask]['zone'].unique())
            else:
                zone_options = get_unique_values(df_sector, 'zone')

            with col3:
                selected_zone = st.selectbox('Zone:', ['Toutes les zones'] + zone_options)

            with col4:
                sectors = get_unique_values(df_sector, 'secteur_na88')
                selected_sector = st.selectbox('Secteur:', ['Tous les secteurs'] + sectors)

            # Filtrage optimisé des données avec masque
            mask = pd.Series(True, index=df_sector.index)
            if selected_region != 'Toutes les régions':
                mask &= df_sector['region'] == selected_region
            if selected_dept != 'Tous les départements':
                mask &= df_sector['departement'] == selected_dept
            if selected_zone != 'Toutes les zones':
                mask &= df_sector['zone'] == selected_zone
            if selected_sector != 'Tous les secteurs':
                mask &= df_sector['secteur_na88'] == selected_sector

            df_filtered = df_sector[mask]

            # Calcul optimisé du taux de croissance
            if selected_sector != 'Tous les secteurs' and not df_filtered.empty:
                df_filtered = df_filtered.sort_values('année')
                last_5_years = sorted(df_filtered['année'].unique())[-5:]
                df_last_5_years = df_filtered[df_filtered['année'].isin(last_5_years)]

            # Création du graphique optimisé
            if not df_filtered.empty:
                fig = go.Figure()

                # Agrégation des données avant création des traces
                for sector in df_filtered['secteur_na88'].unique():
                    sector_data = df_filtered[df_filtered['secteur_na88'] == sector]
                    agg_data = sector_data.groupby('année')['score_sectoriel'].mean().reset_index()

                    fig.add_trace(go.Scatter(
                        x=agg_data['année'],
                        y=agg_data['score_sectoriel'],
                        name=sector,
                        mode='lines+markers'
                    ))

                title_suffix = f" ({selected_sector})" if selected_sector != "Tous les secteurs" else ""
                fig.update_layout(
                    title=f"Évolution des scores sectoriels pour {selected_zone}, {selected_dept} ({selected_region}){title_suffix}",
                    xaxis_title="Année",
                    yaxis_title="Score sectoriel",
                    showlegend=True,
                    height=600,
                    template="plotly_white",
                    hovermode='x unified'
                )

                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
            else:
                st.warning("Aucune donnée disponible pour les critères sélectionnés.")

        except FileNotFoundError:
            st.error("Le fichier de données sectorielles n'a pas été trouvé. Veuillez vérifier que le fichier 'df_filtered_secteurs_88.csv' est présent dans le dossier 'data'.")
        except Exception as e:
            st.error(f"Une erreur s'est produite lors du chargement des données : {str(e)}")

# Nos Suggestions
with tab3:
    options_tab, recherche_tab, reveal_opt1_tab, reveal_opt2_tab = st.tabs(["Nos options", "Ma recherche", "Reveal Opt1", "Reveal Opt2"])

    with options_tab:
        _, col1, col2, _ = st.columns([0.5, 1, 1, 0.5])

        with col1:
            st.markdown("""
            <div style="
                padding: 20px;
                border-radius: 10px;
                background-color: white;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                text-align: center;
                margin: 10px;
                min-height: 200px;
            ">
                <h3 style='color: var(--primary);'>Option 1</h3>
                <div style="margin-top: 15px;">
                    <div style="
                        margin: 15px 0;
                        padding: 10px;
                        border-radius: 8px;
                        background-color: #f8f9fa;
                        transition: transform 0.2s;
                        cursor: pointer;
                    " onmouseover="this.style.transform='scale(1.05)'" onmouseout="this.style.transform='scale(1)'">
                        <i class="fas fa-map-marker-alt" style="color: #dc3545; font-size: 1.2em; margin-right: 8px;"></i>
                        <span style="font-weight: 500;">Pas-de-Calais</span>
                    </div>
                    <div style="
                        margin: 15px 0;
                        padding: 10px;
                        border-radius: 8px;
                        background-color: #f8f9fa;
                        transition: transform 0.2s;
                        cursor: pointer;
                    " onmouseover="this.style.transform='scale(1.05)'" onmouseout="this.style.transform='scale(1)'">
                        <i class="fas fa-bed" style="color: #198754; font-size: 1.2em; margin-right: 8px;"></i>
                        <span style="font-weight: 500;">Hébergement</span>
                    </div>
                    <div style="
                        margin: 15px 0;
                        padding: 10px;
                        border-radius: 8px;
                        background-color: #f8f9fa;
                        transition: transform 0.2s;
                        cursor: pointer;
                    " onmouseover="this.style.transform='scale(1.05)'" onmouseout="this.style.transform='scale(1)'">
                        <i class="fas fa-futbol" style="color: #0d6efd; font-size: 1.2em; margin-right: 8px;"></i>
                        <span style="font-weight: 500;">Football</span>
                    </div>
                </div>
            </div>
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css">
            """, unsafe_allow_html=True)

        with col2:
            st.markdown("""
            <div style="
                padding: 20px;
                border-radius: 10px;
                background-color: white;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                text-align: center;
                margin: 10px;
                min-height: 200px;
            ">
                <h3 style='color: var(--primary);'>Option 2</h3>
                <div style="margin-top: 15px;">
                    <div style="
                        margin: 15px 0;
                        padding: 10px;
                        border-radius: 8px;
                        background-color: #f8f9fa;
                        transition: transform 0.2s;
                        cursor: pointer;
                    " onmouseover="this.style.transform='scale(1.05)'" onmouseout="this.style.transform='scale(1)'">
                        <i class="fas fa-map-marker-alt" style="color: #dc3545; font-size: 1.2em; margin-right: 8px;"></i>
                        <span style="font-weight: 500;">Val d'Oise</span>
                    </div>
                    <div style="
                        margin: 15px 0;
                        padding: 10px;
                        border-radius: 8px;
                        background-color: #f8f9fa;
                        transition: transform 0.2s;
                        cursor: pointer;
                    " onmouseover="this.style.transform='scale(1.05)'" onmouseout="this.style.transform='scale(1)'">
                        <i class="fas fa-utensils" style="color: #198754; font-size: 1.2em; margin-right: 8px;"></i>
                        <span style="font-weight: 500;">Restauration</span>
                    </div>
                    <div style="
                        margin: 15px 0;
                        padding: 10px;
                        border-radius: 8px;
                        background-color: #f8f9fa;
                        transition: transform 0.2s;
                        cursor: pointer;
                    " onmouseover="this.style.transform='scale(1.05)'" onmouseout="this.style.transform='scale(1)'">
                        <i class="fas fa-volleyball-ball" style="color: #0d6efd; font-size: 1.2em; margin-right: 8px;"></i>
                        <span style="font-weight: 500;">Handball</span>
                    </div>
                </div>
            </div>
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css">
            """, unsafe_allow_html=True)

    with recherche_tab:
        st.markdown("<h3 style='text-align: center;'>Ma recherche personnalisée</h3>", unsafe_allow_html=True)

        # Créer deux colonnes pour les sélecteurs
        col1, col2 = st.columns(2)

        # Variables pour suivre les couleurs
        correlation_green = False
        growth_rate_green = False

        with col1:
            # Charger les données de corrélation
            with zipfile.ZipFile(os.path.join(PATHS['data'], "Scores-final.zip")) as z:
                with tempfile.NamedTemporaryFile(suffix='.xlsx') as tmp:
                    tmp.write(z.read("Scores/score_correlation.xlsx"))
                    tmp.seek(0)
                    df_correlations = pd.read_excel(tmp.name, sheet_name='df_total')

            # Créer le sélecteur de département
            departement = st.selectbox(
                "Sélectionnez un département",
                options=sorted(df_correlations['departement'].unique()),
                key='dept_selector'
            )

            # Afficher la corrélation dans une scorecard
            correlation = df_correlations[df_correlations['departement'] == departement]['correlation_departement'].values[0]
            correlation_green = correlation >= 0.7

            st.markdown(f"""
            <div style="
                padding: 20px;
                border-radius: 10px;
                background-color: white;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                text-align: center;
                margin: 10px;
            ">
                <h4>Corrélation Sport-Économie</h4>
                <h2 style="color: {'#2ecc71' if correlation_green else '#e74c3c'};">
                    {correlation:.3f}
                </h2>
                <p>pour le département {departement}</p>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            # Charger les données sectorielles
            df_sector = load_sector_data()

            # Créer le sélecteur de secteur
            secteur = st.selectbox(
                "Sélectionnez un secteur d'activité",
                options=sorted(df_sector['secteur_na88'].unique()),
                key='secteur_selector'
            )

            # Filtrer les données pour le département et le secteur sélectionnés
            df_filtered = df_sector[
                (df_sector['secteur_na88'] == secteur) &
                (df_sector['departement'] == departement)
            ].sort_values(by='année')

            last_5_years = sorted(df_filtered['année'].unique())[-5:]
            df_last_5_years = df_filtered[df_filtered['année'].isin(last_5_years)]

            growth_rate = None
            if len(last_5_years) >= 5:
                agg_scores = df_last_5_years.groupby('année')['score_sectoriel'].mean()
                score_start = agg_scores.iloc[0]
                score_end = agg_scores.iloc[-1]

                if score_start > 0:
                    growth_rate = ((score_end - score_start) / score_start) * 100
                    growth_rate_green = growth_rate >= 2

                    st.markdown(f"""
                    <div style="
                        padding: 20px;
                        border-radius: 10px;
                        background-color: white;
                        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                        text-align: center;
                        margin: 10px;
                    ">
                        <h4>Taux de Croissance sur 5 ans</h4>
                        <h2 style="color: {'#2ecc71' if growth_rate_green else '#e74c3c'};">
                            {growth_rate:.1f}%
                        </h2>
                        <p>pour le secteur {secteur} dans le département {departement}</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.warning("Impossible de calculer le taux de croissance (score initial nul ou négatif)")
            else:
                st.warning(f"Pas assez de données pour calculer le taux de croissance sur 5 ans pour le département {departement}")

        # Ajouter l'indicateur visuel centré sous les deux colonnes
        if growth_rate is not None:  # Seulement si on a pu calculer le taux de croissance
            st.markdown("""
            <div style="
                display: flex;
                justify-content: center;
                align-items: center;
                margin-top: 20px;
            ">
            """, unsafe_allow_html=True)

            if correlation_green and growth_rate_green:
                st.markdown("""
                <div style="text-align: center;">
                    <i class="fas fa-thumbs-up" style="color: #2ecc71; font-size: 48px;"></i>
                    <p style="color: #2ecc71; margin-top: 10px; font-weight: bold;">Nous pouvons commencer à creuser ici 👍</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style="text-align: center;">
                    <i class="fas fa-thumbs-down" style="color: #e74c3c; font-size: 48px;"></i>
                    <p style="color: #e74c3c; margin-top: 10px; font-weight: bold;">Si j'étais vous, je n'irai pas ici 👎</p>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)

        # Ajouter la section des clubs
        st.markdown("<br>", unsafe_allow_html=True)

        # Charger et préparer les données des clubs
        df_clubs_region = pd.read_excel(os.path.join(PATHS['data'], "score_sport.xlsx"), sheet_name="concat_sports")

        # Mapping des sports pour normalisation
        sport_mapping = {
            'basket': 'Basketball',
            'football': 'Football',
            'handball': 'Handball',
            'rugby': 'Rugby',
            'volley': 'Volleyball'
        }

        # Filtrer et préparer les données des clubs
        df_clubs_region['sport'] = df_clubs_region['sport'].map(sport_mapping)
        dept_clubs = df_clubs_region[df_clubs_region['departement'] == departement]
        clubs_count = len(dept_clubs)

        # Afficher le nombre total de clubs
        st.markdown(f"### Clubs du département ({clubs_count})")

        if clubs_count > 0:
            # Afficher la répartition des clubs par sport
            sport_counts = dept_clubs['sport'].value_counts()

            # Créer le graphique camembert
            fig_pie = go.Figure(data=[go.Pie(labels=sport_counts.index, values=sport_counts.values)])
            fig_pie.update_layout(
                title=f"Répartition des clubs par sport dans le département {departement}",
                height=400,
                margin=dict(l=20, r=20, t=40, b=20)
            )
            st.plotly_chart(fig_pie, use_container_width=True, config={'displayModeBar': False})
        else:
            st.info("Aucun club n'a été trouvé dans ce département.")

    with reveal_opt1_tab:
        st.image("/Users/clementrossi/Documents/RossiCtrl/sporteco/streamlit.py/images/option1.webp", use_column_width=True)

    with reveal_opt2_tab:
        st.image("/Users/clementrossi/Documents/RossiCtrl/sporteco/streamlit.py/images/option2.webp", use_column_width=True)

# Close main-content div
st.markdown('</div>', unsafe_allow_html=True)
