import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

@st.cache_data
def load_data():
    df = pd.read_excel('TRANSECT_DATA_SUMMARY.xlsx', sheet_name='TRANSECT DATA SUMMARY')
    return df

df = load_data()

# Nettoyage de la colonne YEAR
df['YEAR'] = pd.to_numeric(df['YEAR'], errors='coerce')
df = df.dropna(subset=['YEAR'])
df['YEAR'] = df['YEAR'].astype(int)

st.title("Couverture moyenne de la phanérogame marine (seagrass)")

# Filtrer pour les années d'intérêt
years_available = sorted(df['YEAR'].unique())
years_interest = st.multiselect("Sélectionnez les années d'intérêt :", years_available, default=years_available[:5])

if not years_interest:
    st.warning("Aucune année sélectionnée. Veuillez sélectionner au moins une année pour afficher les données.")
    st.stop()  # Arrête l'exécution si aucune année sélectionnée

df_filtered = df[df['YEAR'].isin(years_interest)]

# S'assurer que SEAGRASS_COVER est bien numérique
df_filtered['SEAGRASS_COVER'] = pd.to_numeric(df_filtered['SEAGRASS_COVER'], errors='coerce')

# Calcul des moyennes et erreurs standard
stats = []
for year in years_interest:
    covers = df_filtered[df_filtered['YEAR'] == year]['SEAGRASS_COVER'].dropna()
    mean = covers.mean()
    std_err = covers.std(ddof=1) / np.sqrt(len(covers)) if len(covers) > 0 else np.nan
    stats.append((year, mean, std_err, len(covers)))

# Création du graphique interactif avec Plotly
fig = go.Figure()
for (year, mean, std_err, n) in stats:
    fig.add_trace(go.Bar(
        x=[str(year)],
        y=[mean],
        name=str(year),
        error_y=dict(type='data', array=[std_err], visible=True),
        text=[f"{mean:.2f} ± {std_err:.2f}"],
        textposition='outside',
        marker_color='gray',
        opacity=0.8
    ))
fig.update_layout(
    title="Overall Seagrass Cover",
    xaxis_title="YEAR",
    yaxis_title="% Cover",
    yaxis=dict(range=[0, max([x[1] + (x[2] if not np.isnan(x[2]) else 0) + 5 for x in stats])]),
    bargap=0.5,
    showlegend=False,
    height=600
)
st.plotly_chart(fig)

# Affichage du tableau récapitulatif SANS index
st.write("**Statistiques récapitulatives :**")
result_table = pd.DataFrame(stats, columns=['Année', 'Moyenne (%)', "Erreur standard", "n"])
result_table['Année'] = result_table['Année'].astype(str)  # éviter la virgule
st.dataframe(result_table.reset_index(drop=True))  # masquer la colonne d'index
st.write("**Source des données :** TRANSECT_DATA_SUMMARY.xlsx, feuille TRANSECT DATA SUMMARY")