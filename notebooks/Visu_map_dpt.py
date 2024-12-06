#!/usr/bin/env python
# coding: utf-8

# In[70]:


import pandas as pd


# In[71]:


df = pd.read_csv("corr_all.csv")


# In[72]:


import pandas as pd

# Désactiver le troncage des colonnes et des lignes
pd.set_option('display.max_rows', None)  # Affiche toutes les lignes
pd.set_option('display.max_columns', None)  # Affiche toutes les colonnes
pd.set_option('display.width', None)  # Largeur illimitée pour éviter les coupures
pd.set_option('display.max_colwidth', None)  # Pas de limite pour la largeur des colonnes




# In[73]:


df.drop(columns=["Unnamed: 7", "Unnamed: 8"], inplace=True)


# In[74]:


# Remplacement des virgules par des points dans les colonnes de corrélation
df['correlation_commune'] = df['correlation_commune'].str.replace(',', '.').astype(float)
df['correlation_departement'] = df['correlation_departement'].str.replace(',', '.').astype(float)
df['correlation_region'] = df['correlation_region'].str.replace(',', '.').astype(float)

# Conversion des colonnes 'departement', 'region', et 'ville' en category
df = df.astype({
    'departement': 'category',
    'region': 'category',
    'ville': 'category',
})

# Vérification des types
print(df.dtypes)



# In[75]:


import requests

# 1. Obtenir le fichier GeoJSON pour les départements français
geojson_url_departements = 'https://france-geojson.gregoiredavid.fr/repo/departements.geojson'
response_departements = requests.get(geojson_url_departements)
france_departements_geojson = response_departements.json()

# 2. Extraire les noms des départements pour vérification
geojson_departements = [feature['properties']['nom'] for feature in france_departements_geojson['features']]
print("Départements dans le GeoJSON :", geojson_departements)

# Liste des départements à exclure (exemple : départements d'outre-mer, si nécessaire)
excluded_departements = ['Guadeloupe', 'Martinique', 'Guyane', 'La Réunion', 'Mayotte']

# 3. Filtrer la liste des départements
filtered_departements = [departement for departement in geojson_departements if departement not in excluded_departements]

print("Départements restants après suppression :", filtered_departements)

# 4. Mise à jour du GeoJSON pour ne conserver que les départements filtrés
filtered_features = [
    feature for feature in france_departements_geojson['features']
    if feature['properties']['nom'] in filtered_departements
]

# Créer un nouveau GeoJSON avec uniquement les départements filtrés
france_departements_geojson['features'] = filtered_features

# Vérifier les départements restants
remaining_departements = [feature['properties']['nom'] for feature in france_departements_geojson['features']]
print("Départements restants dans le GeoJSON :", remaining_departements)



# In[77]:


# Vérifier les correspondances pour les départements
df_departements = df['departement'].unique()

# Différences entre les départements du DataFrame et du GeoJSON
missing_departements = set(df_departements) - set(geojson_departements)
additional_departements = set(geojson_departements) - set(df_departements)

print("Départements non présents dans le GeoJSON :", missing_departements)
print("Départements non présents dans le DataFrame :", additional_departements)




# In[78]:


#REGIONS

import pandas as pd
import plotly.express as px
import requests


# 2. Obtain the GeoJSON file for French regions
geojson_url = 'https://france-geojson.gregoiredavid.fr/repo/regions.geojson'
response = requests.get(geojson_url)
france_regions_geojson = response.json()

# 3. Match region names between your data and the GeoJSON file
# Extract region names from GeoJSON to verify matching
geojson_regions = [feature['properties']['nom'] for feature in france_regions_geojson['features']]
print("Regions in GeoJSON:", geojson_regions)

# Liste des régions à exclure
excluded_regions = ['Guadeloupe', 'Martinique', 'Guyane', 'La Réunion', 'Mayotte']

# Filtrer la liste des régions (équivalent à .drop())
filtered_regions = [region for region in geojson_regions if region not in excluded_regions]

print("Régions restantes après suppression :", filtered_regions)

# Mise à jour du GeoJSON pour ne conserver que les régions filtrées
filtered_features = [
    feature for feature in france_regions_geojson['features']
    if feature['properties']['nom'] in filtered_regions
]

# Créer un nouveau GeoJSON avec uniquement les régions filtrées
france_regions_geojson['features'] = filtered_features

remaining_regions = [feature['properties']['nom'] for feature in france_regions_geojson['features']]
print("Régions restantes dans le GeoJSON :", remaining_regions)





# In[80]:


import requests

# 1. Obtenir le fichier GeoJSON pour les régions françaises
geojson_url_regions = 'https://france-geojson.gregoiredavid.fr/repo/regions.geojson'
response_regions = requests.get(geojson_url_regions)
france_regions_geojson = response_regions.json()

# 2. Extraire les noms des régions pour vérification
geojson_regions = [feature['properties']['nom'] for feature in france_regions_geojson['features']]
print("Régions dans le GeoJSON :", geojson_regions)

# Liste des régions à exclure (par exemple : régions d'outre-mer)
excluded_regions = ['Guadeloupe', 'Martinique', 'Guyane', 'La Réunion', 'Mayotte']

# 3. Filtrer la liste des régions
filtered_regions = [region for region in geojson_regions if region not in excluded_regions]

print("Régions restantes après suppression :", filtered_regions)

# 4. Mise à jour du GeoJSON pour ne conserver que les régions filtrées
filtered_features = [
    feature for feature in france_regions_geojson['features']
    if feature['properties']['nom'] in filtered_regions
]

# Créer un nouveau GeoJSON avec uniquement les régions filtrées
france_regions_geojson['features'] = filtered_features

# Vérifier les régions restantes
remaining_regions = [feature['properties']['nom'] for feature in france_regions_geojson['features']]
print("Régions restantes dans le GeoJSON :", remaining_regions)


# In[84]:


import plotly.express as px

# Assurez-vous que les GeoJSON des régions et des départements sont prêts
# france_regions_geojson contient les régions
# france_departements_geojson contient les départements
# df contient les colonnes 'region', 'departement', 'correlation_region', et 'correlation_departement'

# Carte principale : France avec les régions
fig = px.choropleth(
    df,
    geojson=france_regions_geojson,
    locations='region',
    featureidkey='properties.nom',
    color='correlation_region',
    color_continuous_scale='Viridis',
    title='Corrélation par Région',
    labels={'correlation_region': 'Corrélation'}
)

# Ajustement de la projection et des dimensions
fig.update_geos(
    visible=False,  # Cache les axes
    fitbounds="locations",  # Centre et ajuste automatiquement
    projection_type="mercator"  # Utilise une projection standard
)

fig.update_layout(
    margin={"r": 0, "t": 30, "l": 0, "b": 0},  # Ajuste les marges
    title_x=0.5  # Centre le titre
)

# Ajout d'un menu déroulant pour afficher les départements
buttons = []

for region in df['region'].unique():
    # Filtrer les départements pour la région sélectionnée
    df_region = df[df['region'] == region]

    # Créer un sous-GeoJSON des départements pour cette région
    geojson_filtered = {
        "type": "FeatureCollection",
        "features": [
            feature for feature in france_departements_geojson['features']
            if feature['properties']['nom'] in df_region['departement'].values
        ]
    }

    # Ajouter un bouton pour cette région
    buttons.append(dict(
        args=[
            {
                "geojson": geojson_filtered,
                "locations": df_region['departement'],
                "z": df_region['correlation_departement'],
                "featureidkey": "properties.nom",
                "coloraxis": None  # Garde la même échelle de couleur
            }
        ],
        label=region,
        method="restyle"
    ))

# Ajouter le menu déroulant au layout
fig.update_layout(
    updatemenus=[dict(
        active=0,
        buttons=buttons,
        x=1.15,  # Place le menu à droite de la carte
        y=1,
        xanchor="left",
        yanchor="top"
    )]
)

# Afficher la carte interactive
fig.show()


# In[87]:


import plotly.express as px

# Fonction pour afficher une carte interactive des régions et départements
def plot_map_with_selector(df_region, df_departement, geojson_regions, geojson_departements):
    # Carte principale : France avec les régions
    fig = px.choropleth(
        df_region,
        geojson=geojson_regions,
        locations="region",
        featureidkey="properties.nom",
        color="correlation_region",
        color_continuous_scale="Viridis",
        title="Carte des régions de France (corrélation)",
        hover_name="region",  # Affiche le nom de la région
    )

    fig.update_geos(fitbounds="locations", visible=False)

    # Ajouter un menu déroulant pour le choix de la vue
    buttons = []

    # 1. Bouton pour afficher toutes les régions
    buttons.append(
        dict(
            args=[{
                "geojson": [geojson_regions],  # GeoJSON des régions
                "locations": [df_region["region"]],
                "z": [df_region["correlation"]],
                "hovertemplate": "<b>Région : %{location}</b><br>Corrélation : %{z:.2f}<extra></extra>",
            }],
            label="France entière",
            method="update",
        )
    )

    # 2. Boutons pour afficher les départements d'une région
    for region in df_region["region"].unique():
        # Filtrer les départements pour la région sélectionnée
        filtered_df = df_departement[df_departement["region"] == region]

        buttons.append(
            dict(
                args=[{
                    "geojson": [geojson_departements],  # GeoJSON des départements
                    "locations": [filtered_df["departement"]],
                    "z": [filtered_df["correlation_departement"]],
                    "hovertemplate": "<b>Département : %{location}</b><br>Corrélation : %{z:.2f}<extra></extra>",
                }],
                label=region,
                method="update",
            )
        )

    # Ajouter le menu déroulant à la carte
    fig.update_layout(
        updatemenus=[
            dict(
                buttons=buttons,
                direction="down",
                x=0.1,
                y=1.1,
                showactive=True,
            )
        ]
    )

    # Ajuster les marges pour un affichage optimal
    fig.update_layout(margin={"r": 0, "t": 50, "l": 0, "b": 0})

    # Afficher la carte
    fig.show()

# Appeler la fonction pour afficher la carte interactive
plot_map_with_selector(df_region, df_departement, geojson_regions, geojson_departements)

