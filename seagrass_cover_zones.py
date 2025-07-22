import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

@st.cache_data
def load_data():
    df = pd.read_excel('TRANSECT_DATA_SUMMARY.xlsx', sheet_name='TRANSECT DATA SUMMARY')
    return df
def main():
    df = load_data()
    df = df.dropna(subset=['SP_RICHNESS', 'ZONE', 'MONTH', 'YEAR'])
    st.title("🌱 Richesse spécifique des herbiers marins (2021-2025)")

    # Sélecteurs Streamlit stylisés avec colonnes
    col1, col2, col3 = st.columns(3)
    with col1:
        zone_sel = st.multiselect(
            "Sélectionnez la ou les zones :",
            sorted(df['ZONE'].dropna().unique()),
            default=sorted(df['ZONE'].dropna().unique())
        )
    with col2:
        mois_sel = st.multiselect(
            "Sélectionnez le(s) mois :",
            sorted(df['MONTH'].dropna().unique()),
            default=sorted(df['MONTH'].dropna().unique())
        )
    with col3:
        annees_sel = st.multiselect(
            "Sélectionnez les années :",
            sorted(df['YEAR'].dropna().astype(int).unique()),
            default=sorted(df['YEAR'].dropna().astype(int).unique())
        )

    df_filtrée = df[
        (df['ZONE'].isin(zone_sel)) &
        (df['MONTH'].isin(mois_sel)) &
        (df['YEAR'].isin(annees_sel))
    ]
    df_filtrée["SP_RICHNESS"] = pd.to_numeric(df_filtrée["SP_RICHNESS"], errors='coerce')

    # 1. Graphique par ZONE
    st.subheader("Richesse spécifique moyenne par zone")
    zone_stats = df_filtrée.groupby('ZONE').agg(
        moyenne=('SP_RICHNESS', 'mean'),
        erreur_std=('SP_RICHNESS', lambda x: x.std(ddof=1) / np.sqrt(len(x))),
        effectif=('SP_RICHNESS', 'count')
    ).reset_index()

    fig_zone = px.bar(
        zone_stats,
        x='ZONE', y='moyenne',
        error_y='erreur_std',
        text='moyenne',
        labels={"moyenne": "Richesse spécifique moyenne", "ZONE": "Zone"},
        title='Richesse spécifique par zone'
    )
    col1, col2 = st.columns([2, 1])
    with col1:
        st.plotly_chart(fig_zone, use_container_width=True)
    with col2:
        st.dataframe(zone_stats)

    # 2. Graphique par MOIS (toutes zones ou par zone)
    st.subheader("Richesse spécifique par mois")
    sel_par_zone = st.checkbox("Afficher par zone", value=False)
    if sel_par_zone:
        mois_stats = df_filtrée.groupby(['MONTH', 'ZONE']).agg(
            moyenne=('SP_RICHNESS', 'mean'),
            erreur_std=('SP_RICHNESS', lambda x: x.std(ddof=1) / np.sqrt(len(x)))
        ).reset_index()
        fig_mois = px.line(
            mois_stats, x='MONTH', y='moyenne', error_y='erreur_std',
            color='ZONE', markers=True,
            labels={"moyenne": "Richesse spécifique", "MONTH": "Mois"},
            title="Évolution mensuelle par zone"
        )
    else:
        mois_stats = df_filtrée.groupby('MONTH').agg(
            moyenne=('SP_RICHNESS', 'mean'),
            erreur_std=('SP_RICHNESS', lambda x: x.std(ddof=1) / np.sqrt(len(x)))
        ).reset_index()
        fig_mois = px.line(
            mois_stats, x='MONTH', y='moyenne', error_y='erreur_std',
            markers=True,
            labels={"moyenne": "Richesse spécifique", "MONTH": "Mois"},
            title="Évolution mensuelle toutes zones confondues"
        )
    col1, col2 = st.columns([2, 1])
    with col1:
        st.plotly_chart(fig_mois, use_container_width=True)
    with col2:
        st.dataframe(mois_stats)

    # 3. Graphique global (tous filtres)
    st.subheader("Richesse spécifique globale (tous filtres appliqués)")
    global_stats = df_filtrée["SP_RICHNESS"].agg(['mean', 'std', 'count'])
    global_mean = global_stats['mean']
    global_stderr = global_stats['std'] / np.sqrt(global_stats['count']) if global_stats['count'] > 0 else np.nan

    st.write(f"**Richesse spécifique moyenne globale :** {global_mean:.2f} ± {global_stderr:.2f} (n={global_stats['count']})")

    # 4. Export des données
    csv = df_filtrée.to_csv(index=False).encode('utf-8')
    st.download_button(label="Télécharger les données filtrées (CSV)", data=csv, file_name='richesse_specific_filtrée.csv', mime='text/csv')
