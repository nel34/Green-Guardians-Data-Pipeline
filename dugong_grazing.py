import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

@st.cache_data
def load_data():
    df = pd.read_excel('TRANSECT_DATA_SUMMARY.xlsx', sheet_name='TRANSECT DATA SUMMARY')
    return df

def format_float(val):
    if pd.isnull(val):
        return ""
    val_rounded = round(float(val), 2)
    if val_rounded == int(val_rounded):
        return str(int(val_rounded))
    return f"{val_rounded:.2f}"

def main():
    df = load_data()
    st.title("🦭 Dugong – Grazing Traces and Seagrass Condition")
    st.markdown("Analysis of dugong grazing traces and their relationship with seagrass condition.")

    # Traitement du champ GRAZING_EVIDENCE
    df['grazing_bin'] = df['GRAZING_EVIDENCE'].apply(lambda x: 1 if str(x).strip().upper() in ['Y', 'YES', '1'] else 0)
    df['ZONE'] = pd.to_numeric(df['ZONE'], errors='coerce')
    df['YEAR'] = pd.to_numeric(df['YEAR'], errors='coerce')
    df['MONTH'] = df['MONTH'].astype(str)

    # Filtres dynamiques
    col1, col2, col3 = st.columns(3)
    with col1:
        zones = sorted(df['ZONE'].dropna().unique())
        zone_sel = st.multiselect("Zones:", zones, default=zones)
    with col2:
        mois = sorted(df['MONTH'].dropna().unique())
        mois_sel = st.multiselect("Months:", mois, default=mois)
    with col3:
        years = sorted(df['YEAR'].dropna().unique())
        annee_sel = st.multiselect("Years:", years, default=years)

    df_filt = df[
        df['ZONE'].isin(zone_sel) &
        df['MONTH'].isin(mois_sel) &
        df['YEAR'].isin(annee_sel)
    ]

    tab1, tab2 = st.tabs([
        "Grazing frequency by zone/year",
        "Impact on seagrass",
    ])

    # --- Tab 1 : Présence de traces de pâturage par zone/année ---
    with tab1:
        st.subheader("Grazing frequency by zone and year")
        grazing_stats = df_filt.groupby(['ZONE', 'YEAR'])['grazing_bin'].mean().reset_index()
        grazing_stats.columns = ['Zone', 'Année', 'Fréquence de pâturage']

        if grazing_stats.empty:
            st.warning("Aucune donnée sur le pâturage pour cette sélection.")
        else:
            # Display only the chart (removed side table)
            fig1 = px.bar(
                grazing_stats,
                x='Année', y='Fréquence de pâturage', color='Zone', barmode='group',
                labels={'Fréquence de pâturage': "Fréquence de pâturage (0-1)", 'Année': 'Année', 'Zone': 'Zone'},
                text=grazing_stats['Fréquence de pâturage'].apply(format_float),
                title="Fréquence de pâturage du dugong par zone et par année"
            )
            fig1.update_yaxes(tickformat=".2f")
            fig1.update_traces(texttemplate='%{text}')
            st.plotly_chart(fig1, use_container_width=True)

    # --- Tab 2 : Lien pâturage & couverture herbière ---
    with tab2:
        st.subheader("Relationship between grazing and seagrass cover")
        df_cov = df_filt.dropna(subset=['SEAGRASS_COVER'])
        if df_cov.empty:
            st.warning("Pas de données suffisantes.")
        else:
            # Display only the chart (removed side table)
            cover_stats = df_cov.groupby('grazing_bin')['SEAGRASS_COVER'].agg(['mean', 'std', 'count']).reset_index()
            cover_stats['grazing'] = cover_stats['grazing_bin'].map({0: "Pas de pâturage", 1: "Avec pâturage"})

            # compute standard error for error bars
            cover_stats['std_err'] = cover_stats.apply(lambda r: (r['std'] / np.sqrt(r['count'])) if r['count'] > 0 else np.nan, axis=1)

            # Plot only (no side table)
            fig2 = px.bar(
                cover_stats,
                x='grazing',
                y='mean',
                error_y='std_err',
                labels={'grazing': 'Pâturage', 'mean': 'Moyenne couverture herbière (%)'},
                title="Couverture moyenne des herbiers selon présence de pâturage",
                text=cover_stats['mean'].apply(format_float)
            )
            fig2.update_yaxes(tickformat=".2f")
            fig2.update_traces(texttemplate='%{text}', textposition='outside')
            st.plotly_chart(fig2, use_container_width=True)

if __name__ == '__main__':
    main()
