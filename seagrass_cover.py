import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

@st.cache_data
def load_data():
    df = pd.read_excel('TRANSECT_DATA_SUMMARY.xlsx', sheet_name='TRANSECT DATA SUMMARY')
    return df

def main():
    df = load_data()

    df['YEAR'] = pd.to_numeric(df['YEAR'], errors='coerce')
    df = df.dropna(subset=['YEAR'])
    df['YEAR'] = df['YEAR'].astype(int)

    st.title("🌿 Couverture moyenne des herbiers marins (seagrass)")

    years_available = sorted(df['YEAR'].unique())
    years_interest = st.multiselect("Sélectionnez les années d'intérêt :", years_available, default=years_available[:5])

    if not years_interest:
        st.warning("Aucune année sélectionnée. Veuillez sélectionner au moins une année pour afficher les données.")
        st.stop()

    df_filtered = df[df['YEAR'].isin(years_interest)]
    df_filtered['SEAGRASS_COVER'] = pd.to_numeric(df_filtered['SEAGRASS_COVER'], errors='coerce')

    stats = []
    for year in years_interest:
        covers = df_filtered[df_filtered['YEAR'] == year]['SEAGRASS_COVER'].dropna()
        mean = covers.mean()
        std_err = covers.std(ddof=1) / np.sqrt(len(covers)) if len(covers) > 0 else np.nan
        stats.append((year, mean, std_err, len(covers)))

    fig = go.Figure()
    def format_float(val):
        return f"{val:.2f}".rstrip('0').rstrip('.') if not np.isnan(val) else ""

    for (year, mean, std_err, n) in stats:
        fig.add_trace(go.Bar(
            x=[str(year)],
            y=[mean],
            name=str(year),
            error_y=dict(type='data', array=[std_err], visible=True),
            text=[f"{format_float(mean)} ± {format_float(std_err)}"],
            textposition='outside',
            marker_color='gray',
            opacity=0.8
        ))

    fig.update_layout(
        title="Overall Seagrass Cover",
        xaxis_title="YEAR",
        yaxis_title="% Cover",
        yaxis=dict(
            range=[0, max([x[1] + (x[2] if not np.isnan(x[2]) else 0) + 5 for x in stats])],
            tickformat=".2~f"  # format sans les zéros inutiles
        ),
        bargap=0.5,
        showlegend=False,
        height=600
    )

    result_table = pd.DataFrame(stats, columns=['Année', 'Moyenne (%)', "Erreur standard", "n"])
    result_table['Année'] = result_table['Année'].astype(str)
    result_table['Moyenne (%)'] = result_table['Moyenne (%)'].apply(format_float)
    result_table['Erreur standard'] = result_table['Erreur standard'].apply(format_float)

    st.plotly_chart(fig, use_container_width=True)
        
    st.header("🌾 Couverture moyenne des herbiers par mois (Fig. 4)")

    # Standardise les noms de mois
    df['MONTH'] = df['MONTH'].astype(str).str.upper()

    # Liste des mois disponibles dynamiquement
    months_available = sorted(df['MONTH'].dropna().unique())
    months_interest = st.multiselect(
        "Sélectionnez les mois :", 
        months_available, 
        default=months_available  # tous cochés par défaut
    )

    # Filtrage
    df_months = df[df['MONTH'].isin(months_interest)].copy()
    df_months['SEAGRASS_COVER'] = pd.to_numeric(df_months['SEAGRASS_COVER'], errors='coerce')
    df_months = df_months.dropna(subset=['SEAGRASS_COVER'])

    if df_months.empty:
        st.warning("Aucune donnée pour les mois sélectionnés.")
    else:
        # Calcul des moyennes et erreurs standard
        month_stats = df_months.groupby('MONTH').agg(
            moyenne=('SEAGRASS_COVER', 'mean'),
            erreur_std=('SEAGRASS_COVER', lambda x: x.std(ddof=1) / np.sqrt(len(x)))
        ).reindex(months_interest).reset_index()

        # Construction du graphique
        fig_month = go.Figure()
        for _, row in month_stats.iterrows():
            fig_month.add_trace(go.Bar(
                x=[row['MONTH']],
                y=[row['moyenne']],
                error_y=dict(type='data', array=[row['erreur_std']], visible=True),
                text=[f"{row['moyenne']:.2f} ± {row['erreur_std']:.2f}"],
                textposition='outside',
                marker_color='teal'
            ))

        fig_month.update_layout(
            title="% de couverture moyen par mois",
            xaxis_title="Mois",
            yaxis_title="% Couverture",
            yaxis=dict(range=[0, max(month_stats['moyenne'] + month_stats['erreur_std']) + 5]),
            bargap=0.5,
            showlegend=False,
            height=500
        )

        st.plotly_chart(fig_month, use_container_width=True)



if __name__ == "__main__":
    main()
