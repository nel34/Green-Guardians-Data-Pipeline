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
    st.title("🐾 Dugong – Traces de pâturage et état des herbiers")
    st.markdown("Analyse des traces de pâturage attribuées aux dugongs et leur lien avec l’état des herbiers.")

    # Traitement du champ GRAZING_EVIDENCE
    df['grazing_bin'] = df['GRAZING_EVIDENCE'].apply(lambda x: 1 if str(x).strip().upper() in ['Y', 'YES', '1'] else 0)
    df['ZONE'] = pd.to_numeric(df['ZONE'], errors='coerce')
    df['YEAR'] = pd.to_numeric(df['YEAR'], errors='coerce')
    df['MONTH'] = df['MONTH'].astype(str)

    # Filtres dynamiques
    col1, col2, col3 = st.columns(3)
    with col1:
        zones = sorted(df['ZONE'].dropna().unique())
        zone_sel = st.multiselect("Zones :", zones, default=zones)
    with col2:
        mois = sorted(df['MONTH'].dropna().unique())
        mois_sel = st.multiselect("Mois :", mois, default=mois)
    with col3:
        annees = sorted(df['YEAR'].dropna().astype(int).unique())
        annee_sel = st.multiselect("Années :", annees, default=annees)

    df_filt = df[
        df['ZONE'].isin(zone_sel) &
        df['MONTH'].isin(mois_sel) &
        df['YEAR'].isin(annee_sel)
    ]

    tab1, tab2 = st.tabs([
        "Fréquence de pâturage par zone/année",
        "Impact sur les herbiers",
    ])

    # --- Tab 1 : Présence de traces de pâturage par zone/année ---
    with tab1:
        st.header("Fréquence de pâturage du dugong")
        grazing_stats = df_filt.groupby(['ZONE', 'YEAR'])['grazing_bin'].mean().reset_index()
        grazing_stats.columns = ['Zone', 'Année', 'Fréquence de pâturage']

        if grazing_stats.empty:
            st.warning("Aucune donnée sur le pâturage pour cette sélection.")
        else:
            col_graph, col_table = st.columns([3, 2])
            with col_graph:
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
            with col_table:
                grazing_stats_fmt = grazing_stats.copy()
                for col in grazing_stats_fmt.select_dtypes(include=np.number).columns:
                    grazing_stats_fmt[col] = grazing_stats_fmt[col].apply(format_float)
                st.dataframe(grazing_stats_fmt, use_container_width=True, hide_index=True)

    # --- Tab 2 : Lien pâturage & couverture herbière ---
    with tab2:
        st.header("Couverture des herbiers selon pâturage")
        df_cov = df_filt.dropna(subset=['SEAGRASS_COVER'])
        if df_cov.empty:
            st.warning("Pas de données suffisantes.")
        else:
            col_graph2, col_table2 = st.columns([3, 2])
            with col_graph2:
                cover_stats = df_cov.groupby('grazing_bin')['SEAGRASS_COVER'].agg(['mean', 'std', 'count']).reset_index()
                cover_stats['grazing'] = cover_stats['grazing_bin'].map({0: "Pas de pâturage", 1: "Avec pâturage"})
                fig2 = px.bar(
                    cover_stats, x='grazing', y='mean', error_y='std',
                    labels={'mean': "Couverture moyenne (%)", "grazing": "Présence traces de pâturage"},
                    text=cover_stats['mean'].apply(format_float),
                    title="Comparaison de la couverture des herbiers selon la présence de pâturage"
                )
                fig2.update_yaxes(tickformat=".2f")
                fig2.update_traces(texttemplate='%{text}')
                st.plotly_chart(fig2, use_container_width=True)
            with col_table2:
                cover_stats_fmt = cover_stats[["grazing", "mean", "std", "count"]].rename(
                    columns={
                        "grazing": "État pâturage",
                        "mean": "Moyenne couverture (%)",
                        "std": "Écart-type",
                        "count": "N"
                    }
                )
                for col in ["Moyenne couverture (%)", "Écart-type"]:
                    cover_stats_fmt[col] = cover_stats_fmt[col].apply(format_float)
                st.dataframe(cover_stats_fmt, use_container_width=True, hide_index=True)

if __name__ == '__main__':
    main()
