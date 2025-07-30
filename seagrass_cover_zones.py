import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from scipy.stats import linregress

@st.cache_data
def load_data():
    df = pd.read_excel('TRANSECT_DATA_SUMMARY.xlsx', sheet_name='TRANSECT DATA SUMMARY')
    return df

def format_float(val):
    # Affiche 2 décimales sauf si .00, alors affiche entier
    if pd.isnull(val):
        return ""
    val_rounded = round(val, 2)
    if val_rounded == int(val_rounded):
        return str(int(val_rounded))
    return f"{val_rounded:.2f}"

def main():
    df = load_data()

    # -------- Sélection des filtres (toujours tout en haut) -----------
    st.title("🌱 Exploration herbiers marins (richesse spécifique & couverture)")

    st.markdown("### Sélection des données")
    col1, col2, col3 = st.columns(3)
    with col1:
        zones = sorted([z for z in df.dropna(subset=['ZONE'])["ZONE"].unique() if pd.notnull(z)])
        zone_sel = st.multiselect("Zones :", zones, default=zones)
    with col2:
        mois = sorted(df.dropna(subset=['MONTH'])["MONTH"].astype(str).unique())
        mois_sel = st.multiselect("Mois :", mois, default=mois)
    with col3:
        annees = sorted(df.dropna(subset=['YEAR'])["YEAR"].astype(int).unique())
        annees_sel = st.multiselect("Années :", annees, default=annees)

    # -------- Ajout des onglets pour les graphiques --------
    tab1, tab2, tab3, tab4 = st.tabs([
        "Richesse spécifique par zone",
        "Richesse spécifique par mois",
        "Couverture des herbiers",
        "Corrélation & Régression"
    ])

    # -------- Préparation des données filtrées ----------- 
    df_rich = df.dropna(subset=['SP_RICHNESS', 'ZONE', 'MONTH', 'YEAR']).copy()
    df_rich["ZONE"] = pd.to_numeric(df_rich["ZONE"], errors='coerce')
    df_rich["YEAR"] = pd.to_numeric(df_rich["YEAR"], errors='coerce')
    df_rich["MONTH"] = df_rich["MONTH"].astype(str)
    df_rich["SP_RICHNESS"] = pd.to_numeric(df_rich["SP_RICHNESS"], errors='coerce')

    df_rich_filt = df_rich[
        (df_rich['ZONE'].isin(zone_sel)) &
        (df_rich['MONTH'].isin(mois_sel)) &
        (df_rich['YEAR'].isin(annees_sel))
    ]

    if df_rich_filt.empty:
        st.warning("Aucune donnée de richesse spécifique pour cette sélection.")
    else:
        with tab1:
            st.header("Richesse spécifique moyenne par zone")
            zone_stats = df_rich_filt.groupby('ZONE').agg(
                moyenne=('SP_RICHNESS', 'mean'),
                erreur_std=('SP_RICHNESS', lambda x: x.std(ddof=1) / np.sqrt(len(x))),
                effectif=('SP_RICHNESS', 'count')
            ).reset_index()
            fig_zone = px.bar(
                zone_stats,
                x='ZONE', y='moyenne',
                error_y='erreur_std',
                text=zone_stats['moyenne'].apply(format_float),
                labels={"moyenne": "Richesse spécifique moyenne", "ZONE": "Zone"},
                title='Richesse spécifique par zone'
            )
            fig_zone.update_yaxes(tickformat=".2f")
            c1, c2 = st.columns([2,1])
            with c1:
                st.plotly_chart(fig_zone, use_container_width=True)
            # Pour le tableau
            with c2:
                zone_stats_fmt = zone_stats.copy()
                zone_stats_fmt['moyenne'] = zone_stats_fmt['moyenne'].apply(format_float)
                zone_stats_fmt['erreur_std'] = zone_stats_fmt['erreur_std'].apply(format_float)
                st.dataframe(zone_stats_fmt)

        with tab2:
            st.header("Richesse spécifique par mois")
            sel_par_zone = st.checkbox("Afficher par zone", value=False, key="sp_month")
            if sel_par_zone:
                mois_stats = df_rich_filt.groupby(['MONTH', 'ZONE']).agg(
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
                mois_stats = df_rich_filt.groupby('MONTH').agg(
                    moyenne=('SP_RICHNESS', 'mean'),
                    erreur_std=('SP_RICHNESS', lambda x: x.std(ddof=1) / np.sqrt(len(x)))
                ).reset_index()
                fig_mois = px.line(
                    mois_stats, x='MONTH', y='moyenne', error_y='erreur_std',
                    markers=True,
                    labels={"moyenne": "Richesse spécifique", "MONTH": "Mois"},
                    title="Évolution mensuelle toutes zones confondues"
                )
            fig_mois.update_yaxes(tickformat=".2f")
            c3, c4 = st.columns([3,2])
            with c3:
                st.plotly_chart(fig_mois, use_container_width=True)
            with c4:
                mois_stats_fmt = mois_stats.copy()
                mois_stats_fmt['moyenne'] = mois_stats_fmt['moyenne'].apply(format_float)
                mois_stats_fmt['erreur_std'] = mois_stats_fmt['erreur_std'].apply(format_float)

                # Nouveau graphique à barres stylisé pour remplacer le tableau
                fig_bar = px.bar(
                    mois_stats,
                    x='MONTH',
                    y='moyenne',
                    error_y='erreur_std',
                    text=mois_stats['moyenne'].apply(format_float),
                    labels={"moyenne": "Richesse spécifique moyenne", "MONTH": "Mois"},
                    title="Richesse spécifique moyenne par mois",
                    color='moyenne',
                    color_continuous_scale='Viridis'
                )
                fig_bar.update_traces(marker_line_color='black', marker_line_width=1.5, textposition='outside')
                fig_bar.update_layout(
                    yaxis=dict(tickformat=".2f"),
                    xaxis_title="Mois",
                    yaxis_title="Richesse spécifique moyenne",
                    plot_bgcolor='rgba(245,245,245,1)',
                    bargap=0.3,
                    showlegend=False,
                    height=400
                )
                st.plotly_chart(fig_bar, use_container_width=True)

            # Stat globale
            st.subheader("Richesse spécifique globale (tous filtres appliqués)")
            global_stats = df_rich_filt["SP_RICHNESS"].agg(['mean', 'std', 'count'])
            global_mean = global_stats['mean']
            global_stderr = global_stats['std'] / np.sqrt(global_stats['count']) if global_stats['count'] > 0 else np.nan
            st.write(f"**Richesse spécifique moyenne globale :** {global_mean:.2f} ± {global_stderr:.2f} (n={global_stats['count']})")

            # Export
            csv = df_rich_filt.to_csv(index=False).encode('utf-8')
            st.download_button(label="Télécharger les données filtrées (CSV)", data=csv, file_name='richesse_specific_filtrée.csv', mime='text/csv')

    # --------- Couverture des herbiers ----------- 
    with tab3:
        st.header("Comparaison de la couverture des herbiers")
        df_cov = df.copy()
        df_cov['ZONE'] = pd.to_numeric(df_cov['ZONE'], errors='coerce')
        df_cov['SEAGRASS_COVER'] = pd.to_numeric(df_cov['SEAGRASS_COVER'], errors='coerce')
        df_cov['YEAR'] = pd.to_numeric(df_cov['YEAR'], errors='coerce')
        df_cov['MONTH'] = df_cov['MONTH'].astype(str)
        df_cov = df_cov.dropna(subset=['ZONE', 'SEAGRASS_COVER', 'YEAR', 'MONTH'])
        df_cov_filt = df_cov[
            df_cov['ZONE'].isin(zone_sel) &
            df_cov['MONTH'].isin(mois_sel) &
            df_cov['YEAR'].isin(annees_sel)
        ]

        if df_cov_filt.empty:
            st.warning("Aucune donnée de couverture pour cette sélection.")
        else:
            stats = []
            for zone in sorted(df_cov_filt['ZONE'].unique()):
                covers = df_cov_filt[df_cov_filt['ZONE'] == zone]['SEAGRASS_COVER']
                mean = covers.mean()
                std_err = covers.std(ddof=1) / np.sqrt(len(covers)) if len(covers) > 0 else np.nan
                stats.append((f"Zone {int(zone)}", mean, std_err))
            fig = go.Figure()
            for (zone_name, mean, std_err) in stats:
                fig.add_trace(go.Bar(
                    x=[zone_name],
                    y=[mean],
                    name=zone_name,
                    error_y=dict(type='data', array=[std_err], visible=True),
                    text=[f"{mean:.2f} ± {std_err:.2f}"],
                    textposition='outside',
                    marker_color='green'
                ))
            if stats:
                try:
                    ymax = max([x[1] + (x[2] if not np.isnan(x[2]) else 0) + 5 for x in stats])
                except Exception:
                    ymax = 100
            else:
                ymax = 100
            fig.update_layout(
                title=f"Comparaison de la couverture des herbiers par zone ({', '.join(mois_sel)} - {', '.join([str(y) for y in annees_sel])})",
                xaxis_title="Zone",
                yaxis_title="% Couverture",
                yaxis=dict(range=[0, ymax]),
                bargap=0.5,
                showlegend=False,
                height=600
            )
            c5, c6 = st.columns([2,1])
            with c5:
                st.plotly_chart(fig, use_container_width=True)
            with c6:
                result_table = pd.DataFrame(stats, columns=['Zone', 'Moyenne (%)', "Erreur standard"])
                result_table_fmt = result_table.copy()
                result_table_fmt['Moyenne (%)'] = result_table_fmt['Moyenne (%)'].apply(format_float)
                result_table_fmt['Erreur standard'] = result_table_fmt['Erreur standard'].apply(format_float)
                st.dataframe(result_table_fmt)
                
    with tab4:
        st.header("Corrélation entre richesse spécifique et couverture des herbiers (Fig. 7 & 8)")

        df_corr = df.dropna(subset=['SEAGRASS_COVER', 'SP_RICHNESS']).copy()
        df_corr['SEAGRASS_COVER'] = pd.to_numeric(df_corr['SEAGRASS_COVER'], errors='coerce')
        df_corr['SP_RICHNESS'] = pd.to_numeric(df_corr['SP_RICHNESS'], errors='coerce')
        df_corr['ZONE'] = pd.to_numeric(df_corr['ZONE'], errors='coerce')
        df_corr['YEAR'] = pd.to_numeric(df_corr['YEAR'], errors='coerce')
        df_corr['MONTH'] = df_corr['MONTH'].astype(str)

        # Appliquer les filtres dynamiques
        df_corr_filt = df_corr[
            df_corr['ZONE'].isin(zone_sel) &
            df_corr['MONTH'].isin(mois_sel) &
            df_corr['YEAR'].isin(annees_sel)
        ]

        if df_corr_filt.empty:
            st.warning("Aucune donnée disponible pour afficher la corrélation.")
        else:
            # Régression linéaire

            x = df_corr_filt['SP_RICHNESS']
            y = df_corr_filt['SEAGRASS_COVER']
            slope, intercept, r_value, p_value, std_err = linregress(x, y)
            r_squared = r_value**2

            fig_corr = px.scatter(
                df_corr_filt,
                x='SP_RICHNESS',
                y='SEAGRASS_COVER',
                color='ZONE',
                opacity=0.8,
                labels={
                    "SP_RICHNESS": "Richesse spécifique",
                    "SEAGRASS_COVER": "% Couverture"
                },
                title=f"Corrélation entre richesse spécifique et couverture des herbiers<br><sup>Régression linéaire : y = {slope:.2f}x + {intercept:.2f} (R² = {r_squared:.2f})</sup>"
            )

            fig_corr.update_traces(
                marker=dict(size=8, line=dict(width=1, color='DarkSlateGrey'))
            )



            # Ligne de régression
            x_vals = np.linspace(x.min(), x.max(), 100)
            y_vals = slope * x_vals + intercept
            fig_corr.add_trace(go.Scatter(x=x_vals, y=y_vals, mode='lines', name='Régression', line=dict(color='black', dash='dash')))

            fig_corr.update_layout(height=600)
            st.plotly_chart(fig_corr, use_container_width=True)
